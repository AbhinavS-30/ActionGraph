# ActionGraph status

## October 29, 2026

- Built by Codex: `app/validation.py` with `validate_transcript(text)`. It rejects non-string input with TypeError, rejects blank input with ValueError, and returns trimmed text while preserving internal whitespace. Added focused validation tests. The validator is not yet connected to an API route; extraction is not implemented.
- Checks: 13 tests passed using `.venv/bin/python -m pytest`; Ruff checks passed for app and tests.
- Demonstrated by the learner: manually identified three supported transcript actions; distinguished a suggestion from a commitment, a dependency from a deadline, and numeric strings from numbers; selected contextual exact evidence; correctly wrote the non-string check with guidance and identified the blank-input check.
- Still needing practice: independently writing a complete function, indentation, type hints, exceptions, and tracing execution. The learner requested worked implementations followed by explanations and questions; this validator was not independently implemented by the learner.
- Limitations: no model calls, extraction, evidence checking, date normalization, or extraction evaluation. Input validity does not establish that a transcript contains an action.
- Next small task: trace one successful and one failing validator call, then attempt a small independent variation with hints before solutions. Continue one concept at a time before adding parsing or model calls.
- Weekdays remain project learning and building; interview preparation is weekends only.

### JSON parsing step

- Built by Codex after learner agreement: `app/parsing.py` adds `parse_extraction_result(text)`, using JSON parsing followed by the existing ExtractionResult schema. Non-string input raises TypeError, malformed JSON raises JSONDecodeError, and schema mismatches raise ValidationError. No automatic repair is attempted.
- Checks: all 26 tests passed; Ruff lint and formatting checks passed for the new files after formatting the tests. Cases include valid items, null values, no actions, malformed JSON, missing fields, wrong shapes, empty evidence, invalid review status, and non-string input.
- Learner independently wrote a correct trimming assertion and a JSON object with a string owner and null deadline. Demonstrated understanding that JSON null becomes Python None and that parsing and schema validation reject different failures. Expected-error tests required guided practice.
- Still needing practice: tracing the new parser and independently writing functions; the parser and its tests were implemented by Codex.
- Current limitations: parser is not connected to an API or model. Extraction remains unimplemented. Schema validity does not verify evidence against the transcript or establish extraction correctness.
- Next small task: trace the parser's two stages with an empty items list and a missing items field; explain the difference before any model integration.

### Exact evidence check

- Built by Codex after learner agreement: `app/evidence.py` adds `evidence_matches(transcript, evidence)`. It validates transcript input, rejects non-string evidence, returns False for blank evidence, and checks exact substring presence against the original transcript. Matching preserves case, punctuation, spacing, and boundaries; no automatic repair or normalization is applied.
- Checks: all 41 tests passed; Ruff lint passed for app and tests; formatting checks passed for the new evidence files. Evidence tests cover matches, changed words/case/spacing/punctuation, blank quotes, original boundaries, and invalid input types.
- Demonstrated by learner: identified missing action/deadline/evidence fields, correctly predicted that a changed day fails exact matching, that matching evidence does not prove the deadline interpretation, and that omitted words prevent a substring match. The learner initially expected schema validation to catch fabricated evidence; this distinction was explained. Grouping multiple fields into one JSON object still needs independent practice.
- Codex implemented this checker and tests; no independent evidence-check implementation by the learner has been claimed.
- Current limitations: evidence checking is a standalone helper, not connected to parsing, an API, or a model; review status is not automatically changed. Exact presence alone does not verify attribution, interpretation, or completeness. Extraction remains unimplemented.
- Next small task: trace the blank-evidence guard and the final substring check, then write a small independent assertion with hints if needed.
