"""Validate transcript text before any extraction is attempted."""


def validate_transcript(text: str) -> str:
    """Return trimmed text, rejecting non-string and blank input."""
    if not isinstance(text, str):
        raise TypeError("Transcript must be a string.")

    trimmed_text = text.strip()
    if not trimmed_text:
        raise ValueError("Transcript must not be blank.")

    return trimmed_text
