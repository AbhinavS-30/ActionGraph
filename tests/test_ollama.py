import json

import httpx
import pytest
from pydantic import ValidationError

from app.ollama import OllamaResponseError, generate_text
from app.parsing import parse_extraction_result
from app.prompts import build_extraction_prompt
from app.schemas import ExtractionResult


@pytest.mark.parametrize(
    "model_text, expected_error",
    [
        ('{"items": []}', None),
        ("Hello!", json.JSONDecodeError),
        ('{"items": "Hello!"}', ValidationError),
    ],
)
def test_schema_request_still_requires_local_parsing(model_text, expected_error):
    schema = ExtractionResult.model_json_schema()
    prompt = build_extraction_prompt("Maya: Good morning.")

    def handler(request):
        payload = json.loads(request.content)
        assert payload["format"] == schema
        assert payload["prompt"] == prompt
        return httpx.Response(200, json={"done": True, "response": model_text})

    with httpx.Client(
        base_url="http://ollama.test", transport=httpx.MockTransport(handler)
    ) as client:
        text = generate_text(prompt, client=client, response_schema=schema)

    if expected_error is None:
        assert parse_extraction_result(text).items == []
    else:
        with pytest.raises(expected_error):
            parse_extraction_result(text)


def test_returns_generated_text_without_parsing_it():
    def handler(request):
        assert request.method == "POST"
        assert str(request.url) == "http://127.0.0.1:11434/api/generate"
        assert json.loads(request.content) == {
            "model": "llama3.2:3b",
            "prompt": "Say hello",
            "stream": False,
            "options": {"num_predict": 1024},
        }
        assert request.extensions["timeout"]["read"] == 60.0
        return httpx.Response(200, json={"response": " Hello! ", "done": True})

    with httpx.Client(
        base_url="http://127.0.0.1:11434",
        timeout=60.0,
        transport=httpx.MockTransport(handler),
    ) as client:
        assert generate_text("Say hello", client=client) == " Hello! "


@pytest.mark.parametrize("error", [httpx.ConnectError, httpx.ReadTimeout])
def test_preserves_connection_and_timeout_failures(error):
    def handler(request):
        raise error("Simulated failure", request=request)

    with (
        httpx.Client(
            base_url="http://ollama.test", transport=httpx.MockTransport(handler)
        ) as client,
        pytest.raises(error),
    ):
        generate_text("Say hello", client=client)


@pytest.mark.parametrize("status", [404, 500])
def test_preserves_http_failures(status):
    with (
        httpx.Client(
            base_url="http://ollama.test",
            transport=httpx.MockTransport(
                lambda request: httpx.Response(status, json={"error": "Unavailable"})
            ),
        ) as client,
        pytest.raises(httpx.HTTPStatusError),
    ):
        generate_text("Say hello", client=client)


@pytest.mark.parametrize(
    "body",
    [
        "not JSON",
        "[]",
        "{}",
        '{"response": "Hello"}',
        '{"response": "Hello", "done": false}',
        '{"response": 42, "done": true}',
        '{"response": " ", "done": true}',
        '{"response": "Hello", "done": true, "error": "Failed"}',
    ],
)
def test_rejects_invalid_generation_envelopes(body):
    with (
        httpx.Client(
            base_url="http://ollama.test",
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, text=body)
            ),
        ) as client,
        pytest.raises(OllamaResponseError),
    ):
        generate_text("Say hello", client=client)


@pytest.mark.parametrize("prompt, error", [(None, TypeError), (" \n", ValueError)])
def test_rejects_invalid_prompt_before_request(prompt, error):
    def handler(request):
        pytest.fail("Invalid prompts must not reach Ollama")

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(error),
    ):
        generate_text(prompt, client=client)


def test_generation_limit_is_forwarded_and_truncation_is_rejected():
    def handler(request):
        assert json.loads(request.content)["options"]["num_predict"] == 12
        # Even apparently valid JSON is rejected when generation hit its limit.
        return httpx.Response(
            200,
            json={"done": True, "done_reason": "length", "response": '{"items": []}'},
        )

    with (
        httpx.Client(
            base_url="http://ollama.test", transport=httpx.MockTransport(handler)
        ) as client,
        pytest.raises(OllamaResponseError),
    ):
        generate_text("Hello", client=client, num_predict=12)


@pytest.mark.parametrize("limit", [0, 4097, True])
def test_invalid_generation_limit_never_calls_ollama(limit):
    def handler(request):
        pytest.fail("Invalid generation limit must not reach Ollama")

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(ValueError, match="num_predict"),
    ):
        generate_text("Hello", client=client, num_predict=limit)


class TrackingStream(httpx.SyncByteStream):
    def __init__(self, chunks):
        self.chunks = chunks
        self.closed = False
        self.consumed = 0

    def __iter__(self):
        for chunk in self.chunks:
            self.consumed += 1
            yield chunk

    def close(self):
        self.closed = True


@pytest.mark.parametrize("headers", [{}, {"Content-Length": "1"}])
def test_oversized_stream_stops_reading_and_closes(headers, monkeypatch):
    monkeypatch.setattr("app.ollama.MAX_OLLAMA_RESPONSE_BYTES", 8)
    stream = TrackingStream([b"12345", b"67890", b"never read"])

    def handler(request):
        assert request.headers["Accept-Encoding"] == "identity"
        return httpx.Response(200, headers=headers, stream=stream)

    with pytest.raises(OllamaResponseError, match="limit"), httpx.Client(
        base_url="http://ollama.test", transport=httpx.MockTransport(handler)
    ) as client:
        generate_text("Hello", client=client)
    assert stream.closed and stream.consumed == 2


def test_announced_oversize_rejected_before_body_read(monkeypatch):
    monkeypatch.setattr("app.ollama.MAX_OLLAMA_RESPONSE_BYTES", 8)
    stream = TrackingStream([b"never read"])
    with pytest.raises(OllamaResponseError), httpx.Client(
        base_url="http://ollama.test",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200, headers={"Content-Length": "9" * 5000}, stream=stream
            )
        ),
    ) as client:
        generate_text("Hello", client=client)
    assert stream.closed and stream.consumed == 0


def test_exact_response_boundary_preserves_text_and_closes(monkeypatch):
    body = json.dumps({"done": True, "response": " Hello! "}).encode()
    monkeypatch.setattr("app.ollama.MAX_OLLAMA_RESPONSE_BYTES", len(body))
    stream = TrackingStream([body[:7], body[7:]])
    with httpx.Client(
        base_url="http://ollama.test",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, stream=stream)
        ),
    ) as client:
        assert generate_text("Hello", client=client) == " Hello! "
    assert stream.closed


def test_compressed_response_rejected_without_decompression():
    stream = TrackingStream([b"not even valid gzip"])
    with pytest.raises(OllamaResponseError, match="Compressed"), httpx.Client(
        base_url="http://ollama.test",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200, headers={"Content-Encoding": "gzip"}, stream=stream
            )
        ),
    ) as client:
        generate_text("Hello", client=client)
    assert stream.closed and stream.consumed == 0


def test_bounded_eval_capture_remains_compatible_with_generation():
    from app.ollama import read_bounded_response

    snapshots = []

    def capture(response):
        snapshots.append(read_bounded_response(response))

    body = json.dumps({"done": True, "response": "Hello"}).encode()
    stream = TrackingStream([body])
    with httpx.Client(
        base_url="http://ollama.test",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, stream=stream)
        ),
        event_hooks={"response": [capture]},
    ) as client:
        assert generate_text("Hello", client=client) == "Hello"
    assert snapshots == [body] and stream.closed
