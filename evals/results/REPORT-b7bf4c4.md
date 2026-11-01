# Strict-contract comparison — November 1, 2026

One ten-case development run from clean source
`b7bf4c451aeb28ea92fc09ec0fd268d5cd914732`. Same model and refusal prompt as the
second experiment; the current flow rejects string-null fields and uses a
1,024-token generation cap. Other generation options remain Ollama defaults.
Initial model warmth was unknown; no warmup or retry was performed. Counts and
semantic pairings below are provisional Codex review, not independent human
adjudication. This is not untouched evaluation or a real-world benchmark.

## Delivered-result comparison

| Measure | Baseline | Model |
| --- | --- | --- |
| Successful attempts | 10/10 | 4/10 |
| Failed attempts | 0/10 | 6/10 |
| Task TP / FP / FN | 6 / 0 / 2 | 5 / 0 / 3 |
| Task precision | 6/6 = 100% | 5/5 = 100% |
| Task recall | 6/8 = 75% | 5/8 = 62.5% |
| Owner errors on paired tasks | 0/6 | 0/5 |
| Deadline errors on paired tasks | 2/6 | 0/5 |
| Evidence-support errors on paired tasks | 0/6 | 0/5 |
| Fully correct matched items | 4/8 labels | 5/8 labels |
| Correct empty-label cases | 3/3 | 0/3 |
| Successful-call duration median / maximum | 0.000065 / 0.000119 s | 1.481 / 2.995 s |

**100% delivered task precision is not evidence of reliable extraction here.**
Six model calls failed. Rejection removed proposed false positives but also
withheld real commitments. No failed call is counted as a correct empty result;
its labels remain false negatives. The model now delivers five fully correct
items versus four in each earlier run, but stochastic generation and multiple
runtime changes prevent attributing that difference to any one change.

## Per-case outcomes

Task counts are TP/FP/FN on delivered items.

| Case / category | Baseline counts | Model counts | Model outcome |
| --- | --- | --- | --- |
| 01 explicit commitment | 1/0/0 | 1/0/0 | Correct. |
| 02 accepted request | 0/0/1 | 0/0/1 | String-null deadline rejected. |
| 03 refused request | 0/0/0 | 0/0/0 | String-null deadline rejected; not a correct negative. |
| 04 unanswered request | 0/0/0 | 0/0/0 | String-null deadline rejected; raw quote also reordered lines. |
| 05 suggestion | 0/0/0 | 0/0/0 | String-null deadline rejected; not a correct negative. |
| 06 unknown owner | 0/0/1 | 0/0/1 | String-null owner rejected. |
| 07 unspecified deadline | 1/0/0 | 1/0/0 | Correct JSON null and other fields. |
| 08 dependency | 1/0/0 | 0/0/1 | String-null deadline rejected; raw task omitted dependency. |
| 09 relative deadline | 1/0/0 | 1/0/0 | Correct. |
| 10 mixed discussion | 2/0/0 | 2/0/0 | Both expected commitments correct this run. |

Failed-call durations: case 02 1.260 s; 03 1.225 s; 04 1.258 s; 05 1.053 s;
06 1.033 s; 08 1.051 s. All six failures were Pydantic ValidationError for a
string-null owner/deadline, not connection errors, timeouts, or token-limit stops.

## Raw generation diagnostics

All 10 generated texts were valid JSON; only 4/10 responses passed the current
output schema's Python validators. There were five items in those schema-valid
responses, all with exact nonblank evidence substrings: nonmatching evidence
0/5. The six rejected responses are preserved and are not counted in that
denominator. Case 04's raw evidence visibly reorders transcript lines; schema
failure happened first, so the service never reached its evidence check.

The string-null guard prevents invalid field delivery but does not teach the
model to produce genuine null values or detect refusals. The schema sent to
Ollama does not encode the custom Python string-null validator. This mismatch
needs a focused generation-contract change and further measurement; do not
silently replace placeholders with null or claim refusal handling is fixed.

## Reproducibility

[Raw run](comparison-b7bf4c4.jsonl) contains effective runtime settings, instruction
and dataset hashes, model digest, Ollama version, platform, per-case durations,
and complete model envelopes. [Review](review-b7bf4c4.json) records zero-based
pairings and semantic decisions. Runtime was Python 3.12.13, Ollama 0.33.3,
`llama3.2:3b` Q4_K_M, macOS ARM64. Model digest:
`a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72`.
Times cover direct extraction calls, including loading and local HTTP, not API
server or browser overhead. Baseline timings are noisy in-process measurements.

Next: explicitly teach JSON null representation in the generation prompt and
compare a new run, preserving this one. Then test untouched cases and repeated
runs before making broader quality claims. Prompt tuning on these ten cases
remains development, not independent validation.
