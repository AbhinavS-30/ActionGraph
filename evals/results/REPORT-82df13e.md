# Two-stage decision experiment — November 1, 2026

Clean source `82df13e`; ten existing development cases; `--contract decisions`.
The public API is unchanged. First, a schema-constrained model call classifies
candidate work as committed, declined, suggested, unanswered, or ambiguous and
provides evidence. Every candidate quote is checked. Only committed candidates
reach a second call for list-valued owner/deadline fields. Final evidence must
exactly retain selected quotes with one item per selected candidate.

This experiment changes the prompt and call structure; it is not a controlled
test of one word or an independent benchmark. Provisional Codex semantic review
uses the unchanged rubric; independent human adjudication is pending. Default
sampling, a 1,024-token cap per call, and no warmup/retries were used.

## Delivered results

| Measure | Baseline | Two-stage model |
| --- | --- | --- |
| Successful attempts | 10/10 | 8/10 |
| Task TP / FP / FN | 6 / 0 / 2 | 4 / 1 / 4 |
| Task precision | 6/6 = 100% | 4/5 = 80% |
| Task recall | 6/8 = 75% | 4/8 = 50% |
| Owner errors on paired tasks | 0/6 | 4/4 |
| Deadline errors on paired tasks | 2/6 | 2/4 |
| Evidence-support errors for paired task meaning | 0/6 | 0/4 |
| Fully correct paired items | 4/8 labels | 0/8 labels |
| Correct empty-label cases | 3/3 | 3/3 |

The negative cases were excluded in this run, but that did not produce a usable
overall improvement. Every returned item used owner "Maya", even though no Maya
appears in any dataset transcript. The field prompt contains Maya as a format
example. This output is consistent with example leakage, but one run does not
prove its cause. Repeated decisions on the same quote also contradict one another
in several raw responses. Structured labels did not establish semantic truth.

## Per-case review

Task counts are TP/FP/FN. Field errors are separate from task matching.

| Case / category | Baseline | Model | Observation |
| --- | --- | --- | --- |
| 01 explicit commitment | 1/0/0 | 1/0/0 | Task matched; wrong owner Maya instead of Nina. |
| 02 accepted request | 0/0/1 | 0/0/1 | Fabricated first-stage candidate quotes rejected. |
| 03 refused request | 0/0/0 | 0/0/0 | Correct empty result; no second call. |
| 04 unanswered request | 0/0/0 | 0/0/0 | Correct empty result; no second call. |
| 05 suggestion | 0/0/0 | 0/0/0 | Correct empty result; no second call. |
| 06 unknown owner | 0/0/1 | 0/0/1 | Committed work incorrectly excluded; no second call. |
| 07 unspecified deadline | 1/0/0 | 1/0/0 | Owner/deadline both Maya, not Priya/null. |
| 08 dependency | 1/0/0 | 0/0/1 | Fabricated first-stage candidates fail whole attempt. |
| 09 relative deadline | 1/0/0 | 1/0/0 | Owner/deadline both Maya, not Nina/tomorrow. |
| 10 mixed discussion | 2/0/0 | 1/1/1 | First task matched with wrong owner; FAQ request extracted and second commitment missed. |

Candidate evidence supports the work for each paired task, but does not support
the erroneous owner/deadline values. Those defects are counted in the field
columns and prevent full correctness; they are not evidence of supported fields.

## Failures, diagnostics, and timing

All ten first-stage responses parsed and passed the decision schema. They
contained 29 candidates; eight candidate evidence quotes were absent from the
transcripts. The corresponding two attempts (cases 02 and 08) failed before the
second call. Four attempts invoked stage two, and all four field responses parsed
and passed list/public conversion validation. All five delivered quotes were
retained exact selected quotes. Candidate hallucinations and wrong field values
were still possible. There were 14 total generation calls, not ten.

No connection failures, timeouts, string-null failures, or generation-length
stops occurred. Model successful-attempt median/max durations: 1.877/4.406
seconds. Failed attempts: case 02 3.982 s, case 08 3.391 s. Baseline median/max:
0.000049/0.000349 seconds with no failures. Durations cover the entire direct
attempt and all model calls, including loading and HTTP; not browser/API latency.

Runtime was local `llama3.2:3b`, Ollama 0.33.3, Python 3.12.13, macOS ARM64.
Model digest, exact settings, hashes, unknown initial warmth, per-response load
durations and full responses in call order are in
[the raw run](comparison-82df13e.jsonl).
[Pairings and reasons](review-82df13e.json) preserve review decisions.

Decision: do not adopt in the public API. The adapter remains an isolated
experiment. Next constrain and validate field provenance against source evidence
before considering additional inference stages. New untouched cases and repeated
runs are still needed; these ten cases are development data.
