import pytest

from app.rules import extract_rule_actions


@pytest.mark.parametrize("promise", ["I will", "I'll", "I’ll"])
def test_explicit_commitment_preserves_evidence_and_recipient_is_not_owner(promise):
    line = f"  Asha: {promise} send Ben the revised agenda by Thursday.  "
    item = extract_rule_actions(line).items[0]
    assert item.action == "Send Ben the revised agenda"
    assert item.owner == "Asha"
    assert item.deadline == "Thursday"
    assert item.evidence == line
    assert item.review_status == "needs_review"


@pytest.mark.parametrize("deadline", ["tomorrow", "next Wednesday", "2026-11-03"])
def test_supported_deadline_is_preserved_without_calendar_conversion(deadline):
    item = extract_rule_actions(f"Ben: I will review the checklist {deadline}.").items[
        0
    ]
    assert item.action == "Review the checklist"
    assert item.deadline == deadline


def test_dependency_deadline_is_not_borrowed():
    item = extract_rule_actions(
        "Asha: I will test the patch after Ben sends the build by Friday."
    ).items[0]
    assert item.action == "Test the patch after Ben sends the build by Friday"
    assert item.deadline is None


@pytest.mark.parametrize(
    "line",
    [
        "Ben: I will not send the checklist.",
        "Ben: I will send nothing.",
        "Ben: I will send the checklist if approved.",
        "Ben: I will maybe review the checklist.",
        "Ben: We should send the checklist.",
        "Asha: Ben, could you send the checklist?",
        "Ben: I will send the checklist and review logs.",
        "Ben: I will send the checklist by 5 pm.",
        "Ben: I will send the checklist on 2026-02-30.",
        "Ben: I will send the checklist. Other work is pending.",
        "Ben: I will send.",
        "Ben: I will review it.",
    ],
)
def test_out_of_scope_or_ambiguous_lines_are_skipped(line):
    assert extract_rule_actions(line).items == []


def test_multiple_supported_lines_are_independent():
    result = extract_rule_actions(
        "Asha: I will send the checklist.\nBen: I'll review the logs tomorrow."
    )
    assert len(result.items) == 2
    assert result.items[0].deadline is None
    assert result.items[1].owner == "Ben"


def test_accepted_requests_remain_outside_this_explicit_grammar():
    result = extract_rule_actions(
        "Asha: Ben, can you review the checklist?\nBen: Yes, I will review it."
    )
    assert result.items == []
