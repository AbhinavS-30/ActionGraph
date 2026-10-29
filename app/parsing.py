"""Parse structured response text without calling a model."""

import json

from app.schemas import ExtractionResult


def parse_extraction_result(text: str) -> ExtractionResult:
    """Parse JSON, then validate its fields against the output contract.

    Malformed JSON raises json.JSONDecodeError. Data that does not match
    the contract raises pydantic.ValidationError.
    """
    if not isinstance(text, str):
        raise TypeError("Extraction response must be a string.")

    data = json.loads(text)
    return ExtractionResult.model_validate(data)
