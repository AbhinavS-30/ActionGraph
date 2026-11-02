import json

import httpx
import pytest

from app.config import Settings
from app.provenance import UnsupportedFieldError
from evals.concise import extract_concise_actions


@pytest.mark.parametrize("owner", ["Nina", "InventedName"])
def test_candidate_retains_public_field_and_review_enforcement(owner):
    quote = "Nina: I will send the budget by Monday."

    def handler(request):
        item = {
            "action": "Send budget",
            "owner": owner,
            "deadline": "Monday",
            "evidence": quote,
            "review_status": "confirmed",
        }
        return httpx.Response(
            200, json={"done": True, "response": json.dumps({"items": [item]})}
        )

    with httpx.Client(
        base_url="http://ollama.test", transport=httpx.MockTransport(handler)
    ) as client:
        if owner == "InventedName":
            with pytest.raises(UnsupportedFieldError):
                extract_concise_actions(quote, client=client, settings=Settings())
        else:
            assert (
                extract_concise_actions(quote, client=client, settings=Settings())
                .items[0]
                .review_status
                == "needs_review"
            )
