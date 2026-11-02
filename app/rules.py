"""Conservative, explicitly limited first-person commitment extraction."""

import re
from datetime import date

from app.provenance import validate_field_evidence
from app.schemas import ActionItem, ExtractionResult
from app.validation import validate_transcript

RULES_SCOPE = (
    "Rules mode supports one explicit first-person task per speaker-labelled line. "
    "Accepted requests, ownerless work, cross-line interpretation and unsupported "
    "phrasing may be missed. Empty output does not prove no commitments exist."
)
COMMITMENT = re.compile(r"(?P<owner>[^:\n]{1,80}):\s+I(?: will|['’]ll) (?P<work>.+)")
VERBS = frozenset(
    [
        "send",
        "email",
        "review",
        "export",
        "update",
        "investigate",
        "notify",
        "publish",
        "upload",
        "check",
        "prepare",
        "validate",
        "test",
        "archive",
        "refresh",
        "revise",
        "deploy",
        "migrate",
        "inspect",
        "document",
        "share",
        "write",
    ]
)
UNSUPPORTED = re.compile(
    r"\b(?:not|no|nothing|never|unless|if|maybe|might|probably|but|and|or|cannot)\b|[.!?;]",
    re.IGNORECASE,
)
DEADLINE = re.compile(
    r"\s+(?:(?:by|on)\s+)?(?P<deadline>today|tomorrow|(?:next\s+)?"
    r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)|\d{4}-\d{2}-\d{2})$",
    re.IGNORECASE,
)


def extract_rule_actions(transcript: str) -> ExtractionResult:
    """Extract supported lines without a model, guesses, or hidden fallback.

    Original lines are evidence. Dependencies stay in actions. Only supported
    trailing date forms before an optional after-clause become deadlines.
    This is a bounded grammar, not a natural-language understanding guarantee.
    """
    validate_transcript(transcript)
    items = []
    for original_line in transcript.splitlines():
        match = COMMITMENT.fullmatch(original_line.strip())
        if match is None:
            continue
        owner = match["owner"].strip()
        work = match["work"].removesuffix(".").strip()
        if (
            not owner
            or owner.casefold() == "null"
            or not work
            or UNSUPPORTED.search(work)
        ):
            continue
        if work.split()[0].lower() not in VERBS:
            continue
        # Do not borrow a deadline from somebody else's prerequisite.
        dependency = re.search(r"\s+after\s+", work, re.IGNORECASE)
        main_work = work[: dependency.start()] if dependency else work
        suffix = work[dependency.start() :] if dependency else ""
        if re.search(
            r"\b(?:it|them|this|that|these|those)\b", main_work, re.IGNORECASE
        ):
            continue
        deadline_match = DEADLINE.search(main_work)
        deadline = deadline_match["deadline"] if deadline_match else None
        if deadline and re.fullmatch(r"\d{4}-\d{2}-\d{2}", deadline):
            try:
                date.fromisoformat(deadline)
            except ValueError:
                continue
        if deadline_match:
            main_work = main_work[: deadline_match.start()]
        elif re.search(
            r"\b(?:by|on|at|within|before|until)\b", main_work, re.IGNORECASE
        ):
            # Explicit but unsupported timing forms are outside this grammar.
            continue
        if len(main_work.split()) < 2:
            continue
        item = ActionItem(
            action=main_work[0].upper() + main_work[1:] + suffix,
            owner=owner,
            deadline=deadline,
            evidence=original_line,
        )
        validate_field_evidence(item)
        items.append(item)
    return ExtractionResult(items=items)
