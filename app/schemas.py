"""Output contract; an LLM response must be validated against this schema."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.validation import validate_transcript


class ExtractionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transcript: str

    @field_validator("transcript")
    @classmethod
    def reject_blank_transcript(cls, value: str) -> str:
        validate_transcript(value)
        return value


class ActionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str = Field(min_length=1)
    owner: str | None
    deadline: str | None
    evidence: str = Field(min_length=1)
    review_status: Literal["needs_review", "confirmed"] = "needs_review"


class ExtractionResult(BaseModel):
    items: list[ActionItem]
