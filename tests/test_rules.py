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


def test_adjacent_explicit_acceptance_resolves_request_task():
    result = extract_rule_actions(
        "Asha: Ben, can you review the checklist?\nBen: Yes, I will review it."
    )
    assert result.items[0].action == "Review the checklist"
    assert result.items[0].owner == "Ben"


@pytest.mark.parametrize(
    "negation", ["I will not", "I won't", "I won’t", "Correction, I will not"]
)
def test_later_explicit_cancellation_removes_matching_prior_commitment(negation):
    transcript = f"Ben: I will publish the access guide tomorrow.\nBen: {negation} publish the access guide."
    assert extract_rule_actions(transcript).items == []


@pytest.mark.parametrize(
    "cancellation",
    [
        "Asha: I will not review the budget.",
        "Ben: I will not review the checklist.",
        "Ben: I will not review the budget by Friday.",
        "Ben: I will not review the budget if approval is missing.",
        "Ben: Never mind.",
        "Ben: I won't review it.",
        "Ben: I won't review the budget at noon.",
    ],
)
def test_unrelated_or_unsupported_cancellation_does_not_remove_task(cancellation):
    promise = "Ben: I will review the budget tomorrow."
    items = extract_rule_actions(promise + "\n" + cancellation).items
    assert len(items) == 1
    assert items[0].evidence == promise


def test_dated_cancellation_removes_only_that_deadline():
    transcript = "Ben: I will review the budget by Monday.\nBen: I will review the budget by Friday.\nBen: I will not review the budget on Monday."
    items = extract_rule_actions(transcript).items
    assert len(items) == 1
    assert items[0].deadline == "Friday"


def test_undated_cancellation_removes_all_prior_matching_dates():
    transcript = "Ben: I will review the budget by Monday.\nBen: I will review the budget by Friday.\nBen: I won't review the budget."
    assert extract_rule_actions(transcript).items == []


def test_recommitment_after_cancellation_is_kept_with_original_evidence():
    promise = "  Ben: I'll review the budget tomorrow.  "
    items = extract_rule_actions(
        "Ben: I will review the budget by Monday.\nBen: I will not review the budget.\n"
        + promise
    ).items
    assert len(items) == 1
    assert items[0].evidence == promise


def test_cancellation_compares_task_case_and_spacing_but_not_speaker_identity():
    transcript = (
        "Ben: I will review the budget tomorrow.\nBen: I will not REVIEW  THE BUDGET."
    )
    assert extract_rule_actions(transcript).items == []
    transcript = (
        "Ben: I will review the budget tomorrow.\nBEN: I will not review the budget."
    )
    assert len(extract_rule_actions(transcript).items) == 1


def test_dependency_must_match_and_cannot_cancel_unqualified_task():
    promise = "Ben: I will test the patch after Asha sends the build."
    result = extract_rule_actions(promise + "\nBen: I will not test the patch.")
    assert len(result.items) == 1
    result = extract_rule_actions(
        promise + "\nBen: I will not test the patch after Asha sends the build."
    )
    assert result.items == []


@pytest.mark.parametrize("promise", ["I will", "I'll", "I’ll"])
@pytest.mark.parametrize("separator", ["\n", "\r\n"])
def test_accepted_request_preserves_contiguous_evidence_and_date(promise, separator):
    transcript = f"  Asha: Ben, could you review the checklist by Friday?  {separator} Ben: Yes, {promise} review it. "
    item = extract_rule_actions(transcript).items[0]
    assert item.action == "Review the checklist"
    assert item.owner == "Ben"
    assert item.deadline == "Friday"
    assert item.evidence == transcript
    assert item.review_status == "needs_review"


@pytest.mark.parametrize("reply", [
    "Ben: Yes.",
    "Ben: Yes, I will review it if approved.",
    "Ben: Yes, I will publish it.",
    "BEN: Yes, I will review it.",
    "Cara: Yes, I will review it.",
    "Ben: No, I will not review it.",
    "Ben: Yes, I will review it tomorrow.",
    "Ben: Yes, I will review it and send it.",
])
def test_ambiguous_or_mismatching_acceptance_is_not_inferred(reply):
    assert extract_rule_actions("Asha: Ben, can you review the checklist?\n" + reply).items == []


@pytest.mark.parametrize("middle", ["\n", "Cara: The meeting is ending.\n"])
def test_acceptance_must_be_immediately_adjacent(middle):
    assert extract_rule_actions("Asha: Ben, can you review the checklist?\n" + middle + "Ben: Yes, I will review it.").items == []


@pytest.mark.parametrize("work", ["review it", "review the checklist and send logs", "review the checklist at noon", "review the checklist if approved"])
def test_request_task_must_pass_existing_grammar(work):
    assert extract_rule_actions(f"Asha: Ben, can you {work}?\nBen: Yes, I will review it.").items == []


def test_accepted_request_can_be_cancelled_and_dependency_is_preserved():
    pair = "Asha: Ben, can you review the checklist after Cara sends the build?\nBen: Yes, I'll review it."
    item = extract_rule_actions(pair).items[0]
    assert item.action == "Review the checklist after Cara sends the build"
    assert item.deadline is None
    assert extract_rule_actions(pair + "\nBen: I won't review the checklist after Cara sends the build.").items == []


@pytest.mark.parametrize("promise", ["I will", "I'll", "I’ll"])
def test_two_task_promise_preserves_full_evidence_and_order(promise):
    line = f"  Ben: {promise} review the checklist and send the report.  "
    items = extract_rule_actions(line).items
    assert [item.action for item in items] == ["Review the checklist", "Send the report"]
    assert all(item.owner == "Ben" and item.deadline is None for item in items)
    assert all(item.evidence == line and item.review_status == "needs_review" for item in items)


@pytest.mark.parametrize("work,deadlines", [
    ("review the checklist by Monday and send the report by Friday", ["Monday", "Friday"]),
    ("review the checklist tomorrow and send the report", ["tomorrow", None]),
])
def test_two_tasks_keep_only_locally_stated_deadlines(work, deadlines):
    assert [i.deadline for i in extract_rule_actions(f"Ben: I will {work}.").items] == deadlines


@pytest.mark.parametrize("work", [
    "review the checklist and send the report by Friday",
    "review the checklist and send it",
    "review the checklist and dance outside",
    "review the checklist and send the report if approved",
    "review the checklist and not send the report",
    "review the checklist and send the report at noon",
    "review the checklist and send the report and archive logs",
    "review the checklist and I will send the report",
    "review the checklist or send the report",
    "review the checklist and the report",
    "review the checklist after Asha sends notes and send the report",
    "review the checklist and send the report after Asha sends notes",
])
def test_ambiguous_or_partly_unsupported_compound_returns_no_partial_items(work):
    assert extract_rule_actions(f"Ben: I will {work}.").items == []


def test_single_task_cancellation_removes_only_one_split_task():
    line = "Ben: I will review the checklist and send the report."
    items = extract_rule_actions(line + "\nBen: I won't review the checklist.").items
    assert len(items) == 1
    assert items[0].action == "Send the report"
    assert items[0].evidence == line


def test_compound_cancellation_is_not_interpreted():
    line = "Ben: I will review the checklist and send the report."
    assert len(extract_rule_actions(line + "\nBen: I won't review the checklist and send the report.").items) == 2


@pytest.mark.parametrize('verb,kind', [('publish','publication'),('review','review'),('upload','upload'),('export','export')])
def test_adjacent_explicit_withdrawal_removes_its_single_task(verb,kind):
    source=f"Dev: I'll {verb} the audit report tomorrow.\nDev: Cancel that {kind}; I am withdrawing the commitment."
    assert extract_rule_actions(source).items == []


@pytest.mark.parametrize('withdrawal', [
    'Other: Cancel that publication; I am withdrawing the commitment.',
    'DEV: Cancel that publication; I am withdrawing the commitment.',
    'Dev: Cancel that review; I am withdrawing the commitment.',
    'Dev: Cancel that publication; I am withdrawing the commitment if approved.',
    'Dev: Maybe cancel that publication; I am withdrawing the commitment.',
    'Dev: "Cancel that publication; I am withdrawing the commitment."',
    'Dev: Never mind.',
])
def test_unsupported_or_mismatched_withdrawal_preserves_task(withdrawal):
    promise='Dev: I will publish the audit report tomorrow.'
    items=extract_rule_actions(promise+'\n'+withdrawal).items
    assert len(items)==1 and items[0].evidence==promise


@pytest.mark.parametrize('middle', ['\n','Other: Good morning.\n'])
def test_withdrawal_does_not_resolve_over_intervening_lines(middle):
    source='Dev: I will publish the audit report tomorrow.\n'+middle+'Dev: Cancel that publication; I am withdrawing the commitment.'
    assert len(extract_rule_actions(source).items)==1


def test_withdrawal_preserves_other_dates_speakers_tasks_and_future_promise():
    source='Dev: I will publish the audit report by Monday.\nOther: I will publish the audit report tomorrow.\nDev: I will review the checklist.\nDev: I will publish the audit report tomorrow.\nDev: Cancel that publication; I am withdrawing the commitment.\nDev: I will publish the audit report by Friday.'
    items=extract_rule_actions(source).items
    assert [(i.owner,i.deadline) for i in items]==[('Dev','Monday'),('Other','tomorrow'),('Dev',None),('Dev','Friday')]


def test_compound_previous_promise_is_not_withdrawn_by_singular_reference():
    source='Dev: I will publish the audit report and review the checklist.\nDev: Cancel that publication; I am withdrawing the commitment.'
    assert len(extract_rule_actions(source).items)==2


def test_withdrawal_matches_null_deadline_duplicates_but_preserves_dependency():
    promise='Dev: I will review the checklist after Other sends the build.'
    source='Dev: I will review the checklist.\n'+promise+'\n'+promise+'\nDev: Cancel that review; I am withdrawing the commitment'
    items=extract_rule_actions(source).items
    assert len(items)==1 and items[0].action=='Review the checklist'
