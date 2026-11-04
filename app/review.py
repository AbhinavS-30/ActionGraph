"""Stateless caller-directed review, preserving submitted proposal snapshots."""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.config import MAX_TRANSCRIPT_CHARS
from app.evidence import evidence_matches
from app.provenance import UnsupportedFieldError, validate_field_evidence
from app.schemas import ActionItem
from app.validation import validate_transcript


class ReviewDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposal_index: int = Field(ge=0, strict=True)
    decision: Literal["confirm", "reject"]
    replacement: ActionItem | None = None

    @model_validator(mode="after")
    def validate_replacement(self) -> Self:
        if self.decision == "reject" and self.replacement is not None:
            raise ValueError("Rejected proposals cannot have replacement values.")
        if (
            self.replacement is not None
            and self.replacement.review_status != "needs_review"
        ):
            raise ValueError("Replacement values must be submitted as needs_review.")
        return self


class ReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transcript: str = Field(max_length=MAX_TRANSCRIPT_CHARS)
    proposals: list[ActionItem] = Field(max_length=100)
    decisions: list[ReviewDecision] = Field(max_length=100)

    @field_validator("transcript")
    @classmethod
    def validate_source(cls, value: str) -> str:
        validate_transcript(value)
        return value

    @model_validator(mode="after")
    def validate_batch(self) -> Self:
        indices = [decision.proposal_index for decision in self.decisions]
        if len(indices) != len(self.proposals) or set(indices) != set(
            range(len(self.proposals))
        ):
            raise ValueError("Provide exactly one decision for each proposal index.")
        for original in self.proposals:
            if original.review_status != "needs_review":
                raise ValueError("Proposals must be submitted as needs_review.")
            if not evidence_matches(self.transcript, original.evidence):
                raise ValueError("Proposal evidence must match the transcript exactly.")
        for decision in self.decisions:
            original = self.proposals[decision.proposal_index]
            candidate = decision.replacement or original
            if candidate.evidence != original.evidence:
                raise ValueError("Review cannot change source evidence.")
            if decision.decision == "confirm":
                try:
                    validate_field_evidence(candidate)
                except UnsupportedFieldError as exc:
                    raise ValueError(
                        "Confirmed owner/deadline must occur in preserved evidence."
                    ) from exc
        return self


class ReviewedProposal(BaseModel):
    proposal_index: int
    decision: Literal["confirm", "reject"]
    original: ActionItem
    reviewed: ActionItem | None


class ReviewResponse(BaseModel):
    records: list[ReviewedProposal]
    persisted: Literal[False] = False


def review_actions(request: ReviewRequest) -> ReviewResponse:
    """Return a complete review batch without mutating or storing caller input."""
    decisions = {decision.proposal_index: decision for decision in request.decisions}
    records = []
    for index, original in enumerate(request.proposals):
        decision = decisions[index]
        candidate = decision.replacement or original
        records.append(
            ReviewedProposal(
                proposal_index=index,
                decision=decision.decision,
                original=original.model_copy(deep=True),
                reviewed=(
                    candidate.model_copy(
                        update={"review_status": "confirmed"}, deep=True
                    )
                    if decision.decision == "confirm"
                    else None
                ),
            )
        )
    return ReviewResponse(records=records)
