"""Output contract; an LLM response must be validated against this schema."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.config import MAX_TRANSCRIPT_CHARS
from app.validation import validate_transcript


class ExtractionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transcript: str = Field(max_length=MAX_TRANSCRIPT_CHARS)
    engine: Literal["rules", "ollama"] = Field(
        default="rules",
        description="rules: limited deterministic demo; ollama: experimental local inference.",
    )

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

    @field_validator("owner", "deadline")
    @classmethod
    def reject_string_null(cls, value: str | None) -> str | None:
        """Unknown values must be JSON null, never a string placeholder."""
        if isinstance(value, str) and value.strip().casefold() == "null":
            raise ValueError("Use JSON null for unknown values, not the string 'null'.")
        return value


class ExtractionResult(BaseModel):
    items: list[ActionItem]


class ExtractionResponse(ExtractionResult):
    engine: Literal["rules", "ollama"]
    limitations: list[str]
