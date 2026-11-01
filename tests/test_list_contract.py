import json

import httpx
import pytest
from pydantic import ValidationError

from app.config import Settings
from app.extraction import UnsupportedEvidenceError
from evals.list_contract import extract_list_actions, parse_list_result


def response_text(owner, deadline):
    return json.dumps(
        {
            "items": [
                {
                    "action": "Review logs",
                    "owner": owner,
                    "deadline": deadline,
                    "evidence": "I will review logs.",
                }
            ]
        }
    )


def test_known_and_unknown_lists_translate_to_public_contract():
    item = parse_list_result(response_text(["Maya"], [])).items[0]
    assert item.owner == "Maya"
    assert item.deadline is None
    assert item.review_status == "needs_review"


@pytest.mark.parametrize("owner", [["Maya", "Leo"], None, "Maya", ["null"]])
def test_invalid_representations_are_rejected_without_repair(owner):
    with pytest.raises(ValidationError):
        parse_list_result(response_text(owner, []))


def test_adapter_still_checks_evidence_against_original_transcript():
    def handler(request):
        schema = json.loads(request.content)["format"]
        assert "ListItem" in schema["$defs"]
        return httpx.Response(
            200, json={"done": True, "response": response_text([], [])}
        )

    with (
        httpx.Client(
            base_url="http://ollama.test", transport=httpx.MockTransport(handler)
        ) as client,
        pytest.raises(UnsupportedEvidenceError),
    ):
        extract_list_actions(
            "Different transcript.", client=client, settings=Settings()
        )
