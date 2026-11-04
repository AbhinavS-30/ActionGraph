import asyncio

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from app.main import app
from app.schemas import ActionItem


def test_health_distinguishes_function_from_api():
    async def request_health():
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            return await client.get("/health")

    response = asyncio.run(request_health())
    assert response.status_code == 200
    assert response.json()["extraction"] == "function_available"
    assert response.json()["extraction_api"] == "available"


def test_missing_owner_can_be_explicitly_unknown():
    item = ActionItem(
        action="Review draft", owner=None, deadline=None, evidence="Review draft"
    )
    assert item.owner is None
    assert item.review_status == "needs_review"


def test_empty_evidence_is_rejected():
    with pytest.raises(ValidationError):
        ActionItem(action="Review draft", owner=None, deadline=None, evidence="")


@pytest.mark.parametrize("field", ["owner", "deadline"])
@pytest.mark.parametrize("value", ["null", "NULL", " \nNull\t"])
def test_string_null_placeholder_is_rejected(field, value):
    data = {
        "action": "Review draft",
        "owner": None,
        "deadline": None,
        "evidence": "Review draft",
    }
    data[field] = value
    with pytest.raises(ValidationError, match="Use JSON null"):
        ActionItem.model_validate(data)


def test_real_values_are_preserved_without_normalization():
    item = ActionItem(
        action="Review draft",
        owner="  Maya  ",
        deadline="Friday",
        evidence="Maya will review draft Friday.",
    )
    assert item.owner == "  Maya  "
    assert item.deadline == "Friday"


@pytest.mark.parametrize("field", ["action", "owner", "deadline", "evidence"])
@pytest.mark.parametrize("value", ["", "   ", "\t\r\n", "\u00a0\u2003"])
def test_output_text_cannot_be_blank(field, value):
    data = {"action": "Review draft", "owner": None, "deadline": None, "evidence": "Review draft"}
    data[field] = value
    with pytest.raises(ValidationError) as error:
        ActionItem.model_validate(data)
    assert error.value.errors()[0]["loc"] == (field,)


def test_valid_output_text_is_preserved_in_all_fields():
    data = {"action": "  Review draft\t", "owner": " Maya ", "deadline": " Friday ", "evidence": "  Maya: Review draft Friday.\n"}
    assert ActionItem.model_validate(data).model_dump(exclude={"review_status"}) == data
