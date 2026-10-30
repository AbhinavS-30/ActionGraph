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
