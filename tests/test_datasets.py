import json
from pathlib import Path

import pytest

from app.evidence import evidence_matches
from app.provenance import validate_field_evidence
from app.schemas import ExtractionResult
from app.validation import validate_transcript


@pytest.mark.parametrize("filename", ["cases.json", "validation-cases.json"])
def test_frozen_labels_have_valid_inputs_contract_and_evidence(filename):
    root = Path(__file__).resolve().parents[1]
    cases = json.loads((root / "evals" / filename).read_text())
    assert len(cases) == 10
    assert len({case["id"] for case in cases}) == len(cases)
    for case in cases:
        validate_transcript(case["transcript"])
        assert case["rationale"].strip()
        result = ExtractionResult.model_validate(case["expected"])
        for item in result.items:
            assert evidence_matches(case["transcript"], item.evidence), case["id"]
            validate_field_evidence(item)
            assert item.review_status == "needs_review"
