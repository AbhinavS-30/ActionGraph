"""Experimental model-only contract; the public API does not use this path."""

import json

import httpx
from pydantic import BaseModel, ConfigDict, Field

from app.config import Settings
from app.evidence import evidence_matches
from app.extraction import UnsupportedEvidenceError
from app.ollama import generate_text
from app.parsing import parse_extraction_result
from app.prompts import EXTRACTION_INSTRUCTIONS
from app.schemas import ExtractionResult
from app.validation import validate_transcript

LIST_INSTRUCTIONS = (
    EXTRACTION_INSTRUCTIONS.replace(
        "owner (string or null), deadline (string or null),",
        "owner (list of zero or one string), deadline (list of zero or one string),",
    )
    .replace(
        'evidence (nonblank string), review_status (always "needs_review").',
        'evidence (nonblank string). The application assigns needs_review.',
    )
    .replace(',\n"review_status": "needs_review"', '')
    .replace("or null if unknown.", "or [] if unknown.")
    .replace(
        "Use null for an unspecified deadline.", "Use [] for an unspecified deadline."
    )
    .replace("description and use null unless", "description and use [] unless")
    .replace(
        '"owner": "Maya", "deadline": "Friday"',
        '"owner": ["Maya"], "deadline": ["Friday"]',
    )
    + "\nFor owner and deadline, unknown is []; known is one string in a list, "
    'such as ["Maya"] or ["Friday"]. Never return null or ["null"].\n'
)


class ListItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str = Field(min_length=1)
    owner: list[str] = Field(max_length=1)
    deadline: list[str] = Field(max_length=1)
    evidence: str = Field(min_length=1)


class ListResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[ListItem]


def parse_list_result(text: str) -> ExtractionResult:
    """Translate an explicit alternative representation, without repairing data."""
    generated = ListResult.model_validate(json.loads(text))
    items = []
    for item in generated.items:
        data = item.model_dump()
        data["owner"] = item.owner[0] if item.owner else None
        data["deadline"] = item.deadline[0] if item.deadline else None
        items.append(data)
    # Reuse all public output validation, including rejection of string null.
    return parse_extraction_result(json.dumps({"items": items}))


def extract_list_actions(
    transcript: str, *, client: httpx.Client, settings: Settings
) -> ExtractionResult:
    validate_transcript(transcript)
    text = generate_text(
        LIST_INSTRUCTIONS + json.dumps(transcript, ensure_ascii=False),
        client=client,
        model=settings.ollama_model,
        num_predict=settings.ollama_num_predict,
        response_schema=ListResult.model_json_schema(),
    )
    result = parse_list_result(text)
    for index, item in enumerate(result.items):
        if not evidence_matches(transcript, item.evidence):
            raise UnsupportedEvidenceError(
                f"Item {index} evidence does not match the transcript."
            )
    return result
