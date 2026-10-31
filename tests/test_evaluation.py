import httpx

from evals.baseline import extract_baseline
from evals.run import collect_attempt


def test_baseline_extracts_explicit_by_deadline_but_not_unaccepted_request():
    result = extract_baseline(
        "Nina: I will send the budget by Monday.\nOmar: Can you check the logs?"
    )
    assert len(result.items) == 1
    assert result.items[0].action == "Send the budget"
    assert result.items[0].owner == "Nina"
    assert result.items[0].deadline == "Monday"
    assert result.items[0].evidence == "Nina: I will send the budget by Monday."


def test_baseline_has_documented_relative_deadline_limitation():
    item = extract_baseline("Nina: I will send the report tomorrow.").items[0]
    assert item.deadline is None
    assert item.action == "Send the report tomorrow"


def test_collector_distinguishes_successful_empty_result_from_failure():
    case = {"id": "test", "transcript": "Nina: Hello."}
    success = collect_attempt(case, "baseline", extract_baseline)
    assert success["status"] == "success"
    assert success["result"] == {"items": []}

    def fail(transcript):
        raise httpx.ReadTimeout("Simulated timeout")

    failure = collect_attempt(case, "ollama", fail)
    assert failure["status"] == "failure"
    assert failure["error_type"] == "ReadTimeout"
    assert "result" not in failure
    assert failure["duration_seconds"] >= 0
