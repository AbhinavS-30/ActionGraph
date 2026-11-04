import asyncio
from copy import deepcopy

import httpx
import pytest
from pydantic import ValidationError

from app.main import app
from app.review import ReviewRequest, review_actions

SOURCE = "Maya: I will send Leo the report by Friday."
PROPOSAL = {
    "action": "Send Leo the report",
    "owner": "Leo",
    "deadline": "Friday",
    "evidence": SOURCE,
    "review_status": "needs_review",
}


def batch():
    return {
        "transcript": SOURCE,
        "proposals": [deepcopy(PROPOSAL)],
        "decisions": [
            {
                "proposal_index": 0,
                "decision": "confirm",
                "replacement": {**PROPOSAL, "owner": "Maya"},
            }
        ],
    }


def test_correction_preserves_original_and_does_not_mutate_request():
    request = ReviewRequest.model_validate(batch())
    before = request.model_dump()
    result = review_actions(request)
    record = result.records[0]
    assert record.original.owner == "Leo"
    assert record.original.review_status == "needs_review"
    assert record.reviewed.owner == "Maya"
    assert record.reviewed.review_status == "confirmed"
    assert record.reviewed.evidence == SOURCE
    assert not result.persisted
    record.original.owner = "Changed"
    assert request.model_dump() == before


def test_confirm_unchanged_and_reject_out_of_order():
    data = batch()
    data["proposals"].append({**PROPOSAL, "owner": "Absent"})
    data["decisions"] = [
        {"proposal_index": 1, "decision": "reject"},
        {"proposal_index": 0, "decision": "confirm"},
    ]
    records = review_actions(ReviewRequest.model_validate(data)).records
    assert [r.proposal_index for r in records] == [0, 1]
    assert records[0].reviewed.owner == "Leo"  # Presence does not prove attribution.
    assert records[1].original.owner == "Absent"
    assert records[1].reviewed is None


def test_corrected_unknown_fields_stay_null():
    data = batch()
    data["decisions"][0]["replacement"].update(owner=None, deadline=None)
    reviewed = review_actions(ReviewRequest.model_validate(data)).records[0].reviewed
    assert reviewed.owner is None and reviewed.deadline is None


@pytest.mark.parametrize(
    "decisions",
    [
        [],
        [{"proposal_index": 1, "decision": "confirm"}],
        [{"proposal_index": -1, "decision": "reject"}],
        [{"proposal_index": True, "decision": "reject"}],
        [{"proposal_index": "0", "decision": "confirm"}],
        [
            {"proposal_index": 0, "decision": "confirm"},
            {"proposal_index": 0, "decision": "reject"},
        ],
        [{"proposal_index": 0, "decision": "maybe"}],
    ],
)
def test_invalid_or_incomplete_decision_batch_is_rejected(decisions):
    data = batch()
    data["decisions"] = decisions
    with pytest.raises(ValidationError):
        ReviewRequest.model_validate(data)


@pytest.mark.parametrize(
    "field,value",
    [
        ("evidence", "Invented quote"),
        ("owner", "Absent"),
        ("deadline", "Monday"),
        ("action", "   "),
        ("review_status", "confirmed"),
    ],
)
def test_invalid_correction_fails_batch(field, value):
    data = batch()
    data["decisions"][0]["replacement"][field] = value
    with pytest.raises(ValidationError):
        ReviewRequest.model_validate(data)


def test_other_real_quote_cannot_replace_original_evidence():
    data = batch()
    data["transcript"] += "\nMaya: I will review the logs."
    data["decisions"][0]["replacement"]["evidence"] = "Maya: I will review the logs."
    with pytest.raises(ValidationError, match="cannot change"):
        ReviewRequest.model_validate(data)


@pytest.mark.parametrize(
    "change",
    [
        "confirmed_original",
        "invented_original",
        "rejected_replacement",
        "extra",
        "overlong",
        "blank",
        "too_many",
    ],
)
def test_invalid_review_request_is_rejected(change):
    data = batch()
    if change == "confirmed_original":
        data["proposals"][0]["review_status"] = "confirmed"
    elif change == "invented_original":
        data["proposals"][0]["evidence"] = "Invented quote"
    elif change == "rejected_replacement":
        data["decisions"][0]["decision"] = "reject"
    elif change == "extra":
        data["engine"] = "rules"
    elif change == "overlong":
        data["transcript"] = "x" * 12001
    elif change == "blank":
        data["transcript"] = "  "
    else:
        data["proposals"] *= 101
    with pytest.raises(ValidationError):
        ReviewRequest.model_validate(data)


def test_empty_batch_is_valid():
    assert (
        review_actions(
            ReviewRequest(transcript=SOURCE, proposals=[], decisions=[])
        ).records
        == []
    )


def test_review_api_never_calls_model_and_invalid_batch_has_no_partial_records(
    monkeypatch,
):
    def fail(*args, **kwargs):
        pytest.fail("Review must not create a model client")

    monkeypatch.setattr("app.main.httpx.Client", fail)

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post("/review", json=batch())
            assert response.status_code == 200
            assert (
                response.json()["records"][0]["reviewed"]["review_status"]
                == "confirmed"
            )
            invalid = batch()
            invalid["proposals"].append(PROPOSAL)
            response = await client.post("/review", json=invalid)
            assert response.status_code == 422
            assert "records" not in response.json()

    asyncio.run(run())
