"""Check quote presence without judging the extracted interpretation."""

from app.validation import validate_transcript


def evidence_matches(transcript: str, evidence: str) -> bool:
    """Return whether nonblank evidence appears exactly in the original text.

    Invalid transcripts and non-string evidence raise input errors. Blank
    evidence returns False. Neither string is normalized for matching.
    """
    validate_transcript(transcript)
    if not isinstance(evidence, str):
        raise TypeError("Evidence must be a string.")
    if not evidence.strip():
        return False

    return evidence in transcript
