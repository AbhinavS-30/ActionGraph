import json

import pytest
from pydantic import ValidationError

from app.parsing import parse_extraction_result


def test_parses_valid_item_with_unknown_fields():
    text = json.dumps(
        {
            "items": [
                {
                    "action": "Review logs",
                    "owner": None,
                    "deadline": None,
                    "evidence": "I will review logs.",
                }
            ]
        }
    )

    result = parse_extraction_result(text)

    assert result.items[0].action == "Review logs"
    assert result.items[0].owner is None
    assert result.items[0].deadline is None
    assert result.items[0].review_status == "needs_review"


def test_accepts_empty_action_list():
    assert parse_extraction_result('{"items": []}').items == []


@pytest.mark.parametrize("text", ["", '{"items": }', 'Here is JSON: {"items": []}'])
def test_rejects_malformed_json(text):
    with pytest.raises(json.JSONDecodeError):
        parse_extraction_result(text)


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"items": [{"owner": "Leo", "deadline": None}]},
        {"items": "Review logs"},
        {
            "items": [
                {
                    "action": "Review logs",
                    "owner": None,
                    "deadline": None,
                    "evidence": "",
                }
            ]
        },
        {
            "items": [
                {
                    "action": "Review logs",
                    "owner": None,
                    "deadline": None,
                    "evidence": "Review logs",
                    "review_status": "approved",
                }
            ]
        },
        [],
        None,
    ],
)
def test_rejects_json_that_fails_schema(data):
    with pytest.raises(ValidationError):
        parse_extraction_result(json.dumps(data))


def test_rejects_non_string_response():
    with pytest.raises(TypeError, match="Extraction response must be a string"):
        parse_extraction_result(42)
