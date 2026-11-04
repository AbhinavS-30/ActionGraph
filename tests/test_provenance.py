import pytest
from pydantic import ValidationError

from app.provenance import UnsupportedFieldError, validate_field_evidence
from app.schemas import ActionItem


def item(owner=None, deadline=None, evidence="Nina: I will send the report tomorrow."):
    return ActionItem(
        action="Send report", owner=owner, deadline=deadline, evidence=evidence
    )


def test_verbatim_fields_and_nulls_are_allowed():
    validate_field_evidence(item(owner="Nina", deadline="tomorrow"))
    validate_field_evidence(item())


@pytest.mark.parametrize(
    "fields, error",
    [({"owner": "Maya"}, UnsupportedFieldError), ({"deadline": "Friday"}, UnsupportedFieldError), ({"owner": "nina"}, UnsupportedFieldError), ({"deadline": " "}, ValidationError)],
)
def test_absent_or_blank_field_text_is_rejected(fields, error):
    with pytest.raises(error):
        validate_field_evidence(item(**fields))


def test_name_fragment_inside_another_name_is_rejected():
    with pytest.raises(UnsupportedFieldError):
        validate_field_evidence(
            item(owner="Ann", evidence="JoAnn: I will send report.")
        )


def test_presence_alone_does_not_prove_owner_attribution():
    # Both names exist; this guard cannot decide who owns the action.
    validate_field_evidence(
        item(owner="Leo", evidence="Nina: I will send Leo the report.")
    )
