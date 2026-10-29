# Validation design

## Input boundary

`validate_transcript(text)` requires a string. Non-string input raises TypeError. Leading and trailing whitespace is removed; blank results raise ValueError. Internal whitespace is preserved. This check does not decide whether the transcript contains a commitment.

## Structured response boundary

`parse_extraction_result(text)` requires response text, parses JSON, and validates the resulting data with ExtractionResult. Malformed JSON raises JSONDecodeError. Data that violates the contract raises Pydantic ValidationError. The parser does not call a model, repair output, or check evidence.

## Evidence boundary

`evidence_matches(transcript, evidence)` validates transcript input and requires string evidence. Blank evidence returns False. Nonblank evidence is compared exactly against the original transcript without changing either string. This preserves quote boundaries, case, spacing, and punctuation.

An exact match establishes quote presence only. It does not establish that an action, owner, deadline, or commitment was interpreted correctly. Human review and extraction evaluation remain separate responsibilities.

## Review boundary

The current schema defaults review_status to needs_review and also permits confirmed. No confirmation workflow, persistence, or automatic unsupported-evidence flagging is implemented.
