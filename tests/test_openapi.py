import asyncio
from uuid import uuid4

import httpx

from app.api_docs import ErrorResponse, ReviewValidationResponse
from app.config import Settings, get_settings
from app.main import app
from app.storage import SessionStore


def test_openapi_declares_existing_errors_and_keeps_validation_and_no_content():
    schema = app.openapi()
    expected = {
        ("/extract", "post"): {"200", "422", "502", "503", "504"},
        ("/sessions", "post"): {"201", "422", "500", "503"},
        ("/sessions/{session_id}", "get"): {"200", "422", "404", "500", "503"},
        ("/sessions/{session_id}/review", "put"): {
            "200",
            "422",
            "404",
            "409",
            "500",
            "503",
        },
        ("/sessions/{session_id}", "delete"): {
            "204",
            "422",
            "404",
            "409",
            "500",
            "503",
        },
        ("/review", "post"): {"200", "422"},
    }
    for (path, method), statuses in expected.items():
        responses = schema["paths"][path][method]["responses"]
        statuses = statuses | {"413"}
        assert set(responses) == statuses
        for status in statuses - {"200", "201", "204", "422"}:
            assert responses[status]["content"]["application/json"]["schema"][
                "$ref"
            ].endswith("/ErrorResponse")
    delete = schema["paths"]["/sessions/{session_id}"]["delete"]["responses"]
    assert "content" not in delete["204"]
    assert (
        "Retry-After"
        in schema["paths"]["/extract"]["post"]["responses"]["503"]["headers"]
    )
    for path, method in [
        ("/sessions", "post"),
        ("/sessions/{session_id}/review", "put"),
    ]:
        assert schema["paths"][path][method]["responses"]["422"]["content"][
            "application/json"
        ]["schema"]["$ref"].endswith("/ReviewValidationResponse")


def test_documented_saved_error_shapes_match_runtime(tmp_path):
    store = SessionStore(tmp_path / "docs.sqlite3")
    store.initialize()
    app.dependency_overrides[get_settings] = lambda: Settings(
        actiongraph_db_path=store.path
    )

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/sessions/" + str(uuid4()))
            assert response.status_code == 404
            ErrorResponse.model_validate(response.json())
            response = await client.post("/sessions", json={"transcript": " "})
            assert response.status_code == 422
            assert isinstance(
                ReviewValidationResponse.model_validate(response.json()).detail, list
            )
            created = (
                await client.post(
                    "/sessions", json={"transcript": "Maya: I will review logs."}
                )
            ).json()
            url = "/sessions/" + created["id"] + "/review"
            response = await client.put(
                url, json={"expected_revision": 1, "decisions": []}
            )
            assert response.status_code == 422
            assert isinstance(
                ReviewValidationResponse.model_validate(response.json()).detail, str
            )
            response = await client.put(
                url, json={"expected_revision": 2, "decisions": []}
            )
            assert response.status_code == 409
            ErrorResponse.model_validate(response.json())

    try:
        asyncio.run(run())
    finally:
        app.dependency_overrides.pop(get_settings, None)
