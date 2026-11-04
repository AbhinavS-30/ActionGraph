import asyncio

import httpx
import pytest

from app.body_limit import MAX_REQUEST_BYTES, RequestBodyLimit
from app.main import app


@pytest.mark.parametrize(
    "body,headers,expected",
    [
        ([b"ab", b"cd"], [], True),
        ([b"ab", b"cde"], [], False),
        ([b"abcde"], [(b"content-length", b"1")], False),
        ([b"abcd"], [(b"content-length", b"4")], True),
        ([], [(b"content-length", b"5")], False),
        ([b"abcd"], [(b"content-length", b"invalid")], True),
        ([], [(b"content-length", b"9" * 5000)], False),
        ([b"abcd"], [(b"content-length", b"0" * 5000 + b"4")], True),
    ],
)
def test_body_count_boundary_and_headers_do_not_bypass_limit(body, headers, expected):
    calls = []
    sent = []
    messages = [
        {"type": "http.request", "body": chunk, "more_body": index < len(body) - 1}
        for index, chunk in enumerate(body)
    ]

    async def receive():
        return messages.pop(0) if messages else {"type": "http.disconnect"}

    async def downstream(scope, receive, send):
        message = await receive()
        calls.append(message["body"])

    async def send(message):
        sent.append(message)

    asyncio.run(
        RequestBodyLimit(downstream, max_bytes=4)(
            {"type": "http", "headers": headers}, receive, send
        )
    )
    if expected:
        assert calls == [b"".join(body)]
    else:
        assert calls == []
        assert sent[0]["status"] == 413


def test_disconnected_upload_never_runs_endpoint():
    async def downstream(*args):
        pytest.fail("Disconnected upload must not run endpoint")

    async def receive():
        return {"type": "http.disconnect"}

    async def send(message):
        pytest.fail("Do not respond to a disconnected client")

    asyncio.run(
        RequestBodyLimit(downstream)({"type": "http", "headers": []}, receive, send)
    )


@pytest.mark.parametrize(
    "path",
    [
        "/extract",
        "/review",
        "/sessions",
        "/sessions/00000000-0000-0000-0000-000000000000/review",
    ],
)
@pytest.mark.parametrize("streamed", [False, True])
def test_oversized_requests_fail_before_processing_and_normal_requests_still_work(
    path, streamed, monkeypatch
):
    def fail(*args, **kwargs):
        pytest.fail("Oversized body must not create a model client")

    monkeypatch.setattr("app.main.httpx.Client", fail)

    async def chunks():
        yield b"x" * MAX_REQUEST_BYTES
        yield b"x"

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.request(
                "PUT" if path.endswith("/review") and path != "/review" else "POST",
                path,
                content=chunks() if streamed else b"x" * (MAX_REQUEST_BYTES + 1),
            )
            assert response.status_code == 413
            assert set(response.json()) == {"detail"}
            assert "items" not in response.json()
            assert (await client.get("/health")).status_code == 200
            response = await client.post(
                "/extract",
                json={"transcript": "Maya: I will review the report tomorrow."},
            )
            assert response.status_code == 200
            assert response.json()["items"][0]["owner"] == "Maya"

    asyncio.run(run())
