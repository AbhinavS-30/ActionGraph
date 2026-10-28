import asyncio

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from app.main import app
from app.schemas import ActionItem


def test_health_does_not_claim_extraction_exists():
    async def request_health():
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            return await client.get("/health")

    response = asyncio.run(request_health())
    assert response.status_code == 200
    assert response.json()["extraction"] == "not_implemented"


def test_missing_owner_can_be_explicitly_unknown():
    item = ActionItem(
        action="Review draft", owner=None, deadline=None, evidence="Review draft"
    )
    assert item.owner is None
    assert item.review_status == "needs_review"


def test_empty_evidence_is_rejected():
    with pytest.raises(ValidationError):
        ActionItem(action="Review draft", owner=None, deadline=None, evidence="")
