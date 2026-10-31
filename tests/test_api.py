import asyncio
import json
from threading import Event

import httpx
import pytest

from app.main import app, get_ollama_client


def post_extract(body, handler):
    def override():
        with httpx.Client(
            base_url="http://ollama.test", transport=httpx.MockTransport(handler)
        ) as client:
            yield client

    async def request():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            return await client.post("/extract", json=body)

    app.dependency_overrides[get_ollama_client] = override
    try:
        return asyncio.run(request())
    finally:
        app.dependency_overrides.pop(get_ollama_client)


def test_extract_returns_reviewable_items_with_original_evidence():
    transcript = "  Maya: I will send the report tomorrow.\n"
    item = {
        "action": "Send report",
        "owner": "Maya",
        "deadline": "tomorrow",
        "evidence": transcript,
        "review_status": "confirmed",
    }

    def handler(request):
        assert "format" in json.loads(request.content)
        return httpx.Response(
            200, json={"done": True, "response": json.dumps({"items": [item]})}
        )

    response = post_extract({"transcript": transcript}, handler)
    assert response.status_code == 200
    item["review_status"] = "needs_review"
    assert response.json() == {"items": [item]}


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"transcript": " \n"},
        {"transcript": None},
        {"transcript": 42},
        {"transcript": "Hello", "extra": 1},
    ],
)
def test_invalid_request_returns_422_without_model_call(body):
    def handler(request):
        pytest.fail("Invalid input must not call Ollama")

    assert post_extract(body, handler).status_code == 422


@pytest.mark.parametrize(
    "error, status", [(httpx.ConnectError, 503), (httpx.ReadTimeout, 504)]
)
def test_transport_errors_have_actionable_responses(error, status):
    def handler(request):
        raise error("Sensitive internal details", request=request)

    response = post_extract({"transcript": "Maya: Hello."}, handler)
    assert response.status_code == status
    assert "Sensitive" not in response.text
    assert response.json()["detail"]


@pytest.mark.parametrize("upstream, expected", [(404, 503), (500, 502)])
def test_ollama_http_errors(upstream, expected):
    response = post_extract(
        {"transcript": "Maya: Hello."},
        lambda request: httpx.Response(upstream, json={"error": "Failed"}),
    )
    assert response.status_code == expected


@pytest.mark.parametrize(
    "text",
    [
        "Hello!",
        '{"items": 42}',
        json.dumps(
            {
                "items": [
                    {
                        "action": "Send report",
                        "owner": None,
                        "deadline": None,
                        "evidence": "Invented quote",
                    }
                ]
            }
        ),
    ],
)
def test_invalid_model_output_returns_502(text):
    response = post_extract(
        {"transcript": "Maya: Hello."},
        lambda request: httpx.Response(200, json={"done": True, "response": text}),
    )
    assert response.status_code == 502
    assert "items" not in response.json()


def test_invalid_ollama_envelope_returns_502():
    response = post_extract(
        {"transcript": "Maya: Hello."}, lambda request: httpx.Response(200, json={})
    )
    assert response.status_code == 502


@pytest.mark.parametrize("field", ["owner", "deadline"])
def test_string_null_model_field_fails_without_returning_items(field):
    transcript = "Maya: I will send the report."
    item = {
        "action": "Send the report",
        "owner": "Maya",
        "deadline": None,
        "evidence": transcript,
    }
    item[field] = "null"
    text = json.dumps({"items": [item]})
    response = post_extract(
        {"transcript": transcript},
        lambda request: httpx.Response(200, json={"done": True, "response": text}),
    )
    assert response.status_code == 502
    assert "items" not in response.json()


def test_oversized_transcript_is_rejected_before_model_call():
    from app.config import MAX_TRANSCRIPT_CHARS

    def handler(request):
        pytest.fail("Oversized transcripts must not reach the model")

    response = post_extract({"transcript": "x" * (MAX_TRANSCRIPT_CHARS + 1)}, handler)
    assert response.status_code == 422


def test_configured_model_and_generation_limit_reach_ollama():
    from app.config import Settings, get_settings

    def handler(request):
        payload = json.loads(request.content)
        assert payload["model"] == "installed-test-model"
        assert payload["options"] == {"num_predict": 256}
        return httpx.Response(200, json={"done": True, "response": '{"items": []}'})

    app.dependency_overrides[get_settings] = lambda: Settings(
        ollama_model="installed-test-model", ollama_num_predict=256
    )
    try:
        assert post_extract({"transcript": "Maya: Hello."}, handler).status_code == 200
    finally:
        app.dependency_overrides.pop(get_settings)


def test_overlapping_extraction_is_rejected_without_second_model_call():
    entered = Event()
    release = Event()
    calls = []

    def handler(request):
        calls.append(request)
        entered.set()
        if not release.wait(timeout=5):
            raise RuntimeError("Test did not release the model response")
        return httpx.Response(200, json={"done": True, "response": '{"items": []}'})

    def override():
        with httpx.Client(
            base_url="http://ollama.test", transport=httpx.MockTransport(handler)
        ) as client:
            yield client

    async def scenario():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            body = {"transcript": "Maya: Hello."}
            first = asyncio.create_task(client.post("/extract", json=body))
            try:
                assert await asyncio.to_thread(entered.wait, 2)
                second = await client.post("/extract", json=body)
                assert second.status_code == 503
                assert second.headers["Retry-After"] == "1"
                assert len(calls) == 1
                assert (await client.get("/health")).status_code == 200
            finally:
                release.set()
                first_response = await first
            assert first_response.status_code == 200
            assert (await client.post("/extract", json=body)).status_code == 200
            assert len(calls) == 2

    app.dependency_overrides[get_ollama_client] = override
    try:
        asyncio.run(scenario())
    finally:
        release.set()
        app.dependency_overrides.pop(get_ollama_client)


def test_failure_releases_slot_for_next_request():
    def fail(request):
        raise httpx.ReadTimeout("Simulated timeout", request=request)

    assert post_extract({"transcript": "Maya: Hello."}, fail).status_code == 504
    response = post_extract(
        {"transcript": "Maya: Hello."},
        lambda request: httpx.Response(
            200, json={"done": True, "response": '{"items": []}'}
        ),
    )
    assert response.status_code == 200
