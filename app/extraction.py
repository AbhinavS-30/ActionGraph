"""Connect local generation to validation and exact evidence checks."""

import httpx

from app.config import Settings, get_settings
from app.evidence import evidence_matches
from app.ollama import generate_text
from app.parsing import parse_extraction_result
from app.prompts import build_extraction_prompt
from app.schemas import ExtractionResult


class UnsupportedEvidenceError(ValueError):
    """A proposed item's evidence is absent from the original transcript."""


def extract_actions(
    transcript: str, *, client: httpx.Client, settings: Settings | None = None
) -> ExtractionResult:
    """Return reviewable items, or fail without returning a partial result.

    Prompt construction validates input before any model request. Transport and
    parser errors propagate. Exact evidence presence does not prove semantic
    correctness, attribution, or completeness.
    """
    prompt = build_extraction_prompt(transcript)
    settings = settings if settings is not None else get_settings()
    text = generate_text(
        prompt,
        client=client,
        response_schema=ExtractionResult.model_json_schema(),
        model=settings.ollama_model,
        num_predict=settings.ollama_num_predict,
    )
    result = parse_extraction_result(text)
    for index, item in enumerate(result.items):
        if not evidence_matches(transcript, item.evidence):
            raise UnsupportedEvidenceError(
                f"Item {index} evidence does not match the transcript."
            )
        # A model cannot perform human confirmation, even if it emits confirmed.
        item.review_status = "needs_review"
    return result
