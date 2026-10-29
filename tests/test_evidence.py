import pytest

from app.evidence import evidence_matches


def test_matches_exact_quote_inside_transcript():
    assert evidence_matches(
        "Nina: Send the budget.\nOmar: I will review it.",
        "Omar: I will review it.",
    )


@pytest.mark.parametrize(
    "evidence",
    ["review logs", "Review the logs", "review  the logs", "review the logs!"],
)
def test_rejects_changed_words_case_spacing_or_punctuation(evidence):
    assert not evidence_matches("Leo: I will review the logs.", evidence)


@pytest.mark.parametrize("evidence", ["", " ", "\n\t"])
def test_blank_evidence_does_not_match(evidence):
    assert not evidence_matches("Leo: Review logs.\n\t", evidence)


def test_does_not_trim_evidence_to_force_a_match():
    assert not evidence_matches("Leo: Review logs.", " Review logs. ")


def test_preserves_original_transcript_boundaries():
    assert evidence_matches("  Leo: Review logs.\n", "  Leo: Review logs.\n")


@pytest.mark.parametrize("evidence", [None, 42])
def test_rejects_non_string_evidence(evidence):
    with pytest.raises(TypeError, match="Evidence must be a string"):
        evidence_matches("Review logs.", evidence)


@pytest.mark.parametrize("transcript", ["", " \n"])
def test_rejects_blank_transcript(transcript):
    with pytest.raises(ValueError, match="Transcript must not be blank"):
        evidence_matches(transcript, "Review logs.")


def test_rejects_non_string_transcript():
    with pytest.raises(TypeError, match="Transcript must be a string"):
        evidence_matches(42, "Review logs.")
