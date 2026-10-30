import json

import httpx
import pytest
from pydantic import ValidationError

from app.extraction import UnsupportedEvidenceError, extract_actions

TRANSCRIPT = "  Maya: I will send the report tomorrow.\n"


def model_item(**changes):
    return {
        "action": "Send the report",
        "owner": "Maya",
        "deadline": "tomorrow",
        "evidence": TRANSCRIPT,
        "review_status": "confirmed",
        **changes,
    }


def client_returning(text):
    return httpx.Client(
        base_url="http://ollama.test",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json={"done": True, "response": text})
        ),
    )


def test_preserves_original_evidence_and_requires_human_review():
    with client_returning(json.dumps({"items": [model_item()]})) as client:
        result = extract_actions(TRANSCRIPT, client=client)
    assert result.items[0].evidence == TRANSCRIPT
    assert result.items[0].deadline == "tomorrow"
    assert result.items[0].review_status == "needs_review"


def test_accepts_empty_result():
    with client_returning('{"items": []}') as client:
        assert extract_actions("Maya: Good morning.", client=client).items == []


@pytest.mark.parametrize("evidence", ["Invented quote", " \n"])
def test_any_unsupported_item_fails_entire_result(evidence):
    text = json.dumps({"items": [model_item(), model_item(evidence=evidence)]})
    with client_returning(text) as client, pytest.raises(UnsupportedEvidenceError):
        extract_actions(TRANSCRIPT, client=client)


@pytest.mark.parametrize(
    "text, error",
    [("Hello!", json.JSONDecodeError), ('{"items": 42}', ValidationError)],
)
def test_propagates_parser_failures(text, error):
    with client_returning(text) as client, pytest.raises(error):
        extract_actions(TRANSCRIPT, client=client)


@pytest.mark.parametrize("error", [httpx.ConnectError, httpx.ReadTimeout])
def test_propagates_model_failures(error):
    def handler(request):
        raise error("Simulated failure", request=request)

    with (
        httpx.Client(
            base_url="http://ollama.test", transport=httpx.MockTransport(handler)
        ) as client,
        pytest.raises(error),
    ):
        extract_actions(TRANSCRIPT, client=client)


@pytest.mark.parametrize("transcript, error", [(" \n", ValueError), (None, TypeError)])
def test_invalid_input_never_calls_model(transcript, error):
    def handler(request):
        pytest.fail("Invalid input must not reach Ollama")

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(error),
    ):
        extract_actions(transcript, client=client)
