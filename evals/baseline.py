"""Deliberately narrow, deterministic first-person commitment baseline."""

import re

from app.schemas import ActionItem, ExtractionResult
from app.validation import validate_transcript


def extract_baseline(transcript: str) -> ExtractionResult:
    validate_transcript(transcript)
    items = []
    for line in transcript.splitlines():
        match = re.fullmatch(r"([^:\n]+): I will (.+?)\.", line)
        if match is None:
            continue
        owner, work = match.groups()
        action, separator, deadline = work.partition(" by ")
        items.append(
            ActionItem(
                action=action[0].upper() + action[1:],
                owner=owner,
                deadline=deadline if separator else None,
                evidence=line,
            )
        )
    return ExtractionResult(items=items)
