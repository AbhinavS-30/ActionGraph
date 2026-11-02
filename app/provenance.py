"""Check field text presence without claiming semantic attribution."""

import re

from app.schemas import ActionItem


class UnsupportedFieldError(ValueError):
    """An owner or deadline has no verbatim support in its item's evidence."""


def validate_field_evidence(item: ActionItem) -> None:
    """Require non-null fields to appear verbatim at word boundaries.

    No case folding, trimming, date conversion, or guessing is performed.
    Matching prevents invented text, but cannot prove that a mentioned person
    owns the action or that a mentioned time is its deadline.
    """
    for field in ("owner", "deadline"):
        value = getattr(item, field)
        if value is None:
            continue
        if not value.strip() or not re.search(
            r"(?<!\w)" + re.escape(value) + r"(?!\w)", item.evidence
        ):
            raise UnsupportedFieldError(
                f"The {field} is not supported by item evidence."
            )
