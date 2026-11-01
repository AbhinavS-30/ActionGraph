import json

import httpx
import pytest

from app.config import Settings
from app.extraction import UnsupportedEvidenceError
from evals.decisions import extract_decided_actions


def client_for(responses, calls):
    def handler(request):
        calls.append(json.loads(request.content))
        return httpx.Response(
            200, json={"done": True, "response": json.dumps(responses[len(calls) - 1])}
        )

    return httpx.Client(
        base_url="http://ollama.test", transport=httpx.MockTransport(handler)
    )


@pytest.mark.parametrize(
    "decision", ["declined", "suggested", "unanswered", "ambiguous"]
)
def test_noncommitted_decisions_do_not_call_field_generation(decision):
    calls = []
    responses = [
        {
            "candidates": [
                {
                    "action": "Review logs",
                    "decision": decision,
                    "evidence": "Maya: Could you review logs?",
                }
            ]
        }
    ]
    with client_for(responses, calls) as client:
        result = extract_decided_actions(
            "Maya: Could you review logs?", client=client, settings=Settings()
        )
    assert result.items == []
    assert len(calls) == 1


def test_committed_quote_passes_to_second_stage_and_public_validation():
    quote = "Maya: I will review logs tomorrow."
    calls = []
    responses = [
        {
            "candidates": [
                {"action": "Review logs", "decision": "committed", "evidence": quote}
            ]
        },
        {
            "items": [
                {
                    "action": "Review logs",
                    "owner": ["Maya"],
                    "deadline": ["tomorrow"],
                    "evidence": quote,
                }
            ]
        },
    ]
    with client_for(responses, calls) as client:
        result = extract_decided_actions(quote, client=client, settings=Settings())
    assert result.items[0].owner == "Maya"
    assert result.items[0].review_status == "needs_review"
    assert len(calls) == 2


def test_invented_decision_evidence_fails_before_field_generation():
    calls = []
    responses = [
        {
            "candidates": [
                {
                    "action": "Review logs",
                    "decision": "committed",
                    "evidence": "Invented quote",
                }
            ]
        }
    ]
    with (
        client_for(responses, calls) as client,
        pytest.raises(UnsupportedEvidenceError),
    ):
        extract_decided_actions("Maya: Hello.", client=client, settings=Settings())
    assert len(calls) == 1


@pytest.mark.parametrize(
    "items",
    [
        [],
        [
            {
                "action": "Other task",
                "owner": [],
                "deadline": [],
                "evidence": "Omar: Other task.",
            }
        ],
    ],
)
def test_second_stage_cannot_drop_candidate_or_use_unselected_quote(items):
    quote = "Maya: I will review logs."
    calls = []
    responses = [
        {
            "candidates": [
                {"action": "Review logs", "decision": "committed", "evidence": quote}
            ]
        },
        {"items": items},
    ]
    with client_for(responses, calls) as client, pytest.raises(ValueError):
        extract_decided_actions(
            quote + "\nOmar: Other task.", client=client, settings=Settings()
        )
