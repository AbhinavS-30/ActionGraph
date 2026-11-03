"""Conservative, explicitly limited first-person commitment extraction."""

import re
from datetime import date

from app.provenance import validate_field_evidence
from app.schemas import ActionItem, ExtractionResult
from app.validation import validate_transcript

RULES_SCOPE = (
    "Rules mode supports one explicit first-person task per speaker-labelled line. "
    "Explicit same-speaker cancellations with matching task wording are applied. "
    "Accepted requests, ownerless work, broader cross-line interpretation and unsupported "
    "phrasing may be missed. Empty output does not prove no commitments exist."
)
RULES_VERSION = "2"
COMMITMENT = re.compile(r"(?P<owner>[^:\n]{1,80}):\s+I(?: will|['’]ll) (?P<work>.+)")
CANCELLATION = re.compile(
    r"(?P<owner>[^:\n]{1,80}):\s+(?:Correction,\s+)?I(?: will not| won['’]t) (?P<work>.+)"
)
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


def _parse_work(work: str) -> tuple[str, str | None] | None:
    """Use the same bounded grammar for promises and cancellation targets."""
    work = work.removesuffix(".").strip()
    if not work or UNSUPPORTED.search(work) or work.split()[0].lower() not in VERBS:
        return None
    dependency = re.search(r"\s+after\s+", work, re.IGNORECASE)
    main_work = work[: dependency.start()] if dependency else work
    suffix = work[dependency.start() :] if dependency else ""
    if re.search(r"\b(?:it|them|this|that|these|those)\b", main_work, re.IGNORECASE):
        return None
    deadline_match = DEADLINE.search(main_work)
    deadline = deadline_match["deadline"] if deadline_match else None
    if deadline and re.fullmatch(r"\d{4}-\d{2}-\d{2}", deadline):
        try:
            date.fromisoformat(deadline)
        except ValueError:
            return None
    if deadline_match:
        main_work = main_work[: deadline_match.start()]
    elif re.search(r"\b(?:by|on|at|within|before|until)\b", main_work, re.IGNORECASE):
        return None
    if len(main_work.split()) < 2:
        return None
    return main_work[0].upper() + main_work[1:] + suffix, deadline


def _task_key(text: str) -> str:
    """Normalize comparison only; never rewrite returned evidence or fields."""
    return " ".join(text.split()).casefold()


def extract_rule_actions(transcript: str) -> ExtractionResult:
    """Process promises and explicit cancellations in transcript order.

    A cancellation must use the exact speaker label and matching task wording
    (ignoring case/whitespace). A stated cancellation deadline restricts removal
    to that same deadline; an omitted deadline removes all earlier matching tasks.
    Future recommitments remain possible. Other cancellation wording is skipped.
    """
    validate_transcript(transcript)
    items: list[ActionItem] = []
    for original_line in transcript.splitlines():
        cancellation = CANCELLATION.fullmatch(original_line.strip())
        match = cancellation or COMMITMENT.fullmatch(original_line.strip())
        if match is None:
            continue
        owner = match["owner"].strip()
        parsed = _parse_work(match["work"])
        if not owner or owner.casefold() == "null" or parsed is None:
            continue
        action, deadline = parsed
        if cancellation:
            items = [
                item
                for item in items
                if not (
                    item.owner == owner
                    and _task_key(item.action) == _task_key(action)
                    and (
                        deadline is None
                        or (
                            item.deadline is not None
                            and _task_key(item.deadline) == _task_key(deadline)
                        )
                    )
                )
            ]
            continue
        item = ActionItem(
            action=action,
            owner=owner,
            deadline=deadline,
            evidence=original_line,
        )
        validate_field_evidence(item)
        items.append(item)
    return ExtractionResult(items=items)
