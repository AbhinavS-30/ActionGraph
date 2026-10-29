import pytest

from app.validation import validate_transcript


def test_trims_edges_and_preserves_internal_whitespace():
    assert validate_transcript(" \nMaya: Review  the logs.\nLeo: Tomorrow.\t ") == (
        "Maya: Review  the logs.\nLeo: Tomorrow."
    )


@pytest.mark.parametrize("text", ["", "   ", "\n\t "])
def test_rejects_blank_transcripts(text):
    with pytest.raises(ValueError, match="Transcript must not be blank"):
        validate_transcript(text)


@pytest.mark.parametrize("text", [42, None, [], {}, True])
def test_rejects_non_string_input(text):
    with pytest.raises(TypeError, match="Transcript must be a string"):
        validate_transcript(text)


def test_accepts_numeric_text():
    assert validate_transcript("  17  ") == "17"
