"""Output contract; an LLM response must be validated against this schema."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ActionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str = Field(min_length=1)
    owner: str | None
    deadline: str | None
    evidence: str = Field(min_length=1)
    review_status: Literal["needs_review", "confirmed"] = "needs_review"


class ExtractionResult(BaseModel):
    items: list[ActionItem]
