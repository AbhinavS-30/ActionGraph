# First fresh-set validation — November 2, 2026

Clean source `d21e6b6`; default public extraction function, not an experimental
adapter. Ten validation cases and eight expected commitments were committed
before this first model run. No prompt, settings, labels, or rubric changes were
made after inspecting results. Cases were authored with knowledge of development
failures, so this is fresh synthetic validation, not an independent external or
real-world benchmark. They are no longer untouched after this run. Semantic
review is provisional Codex adjudication pending independent human review.

## Delivered results

| Measure | Baseline | Model |
| --- | --- | --- |
| Successful attempts | 10/10 | 5/10 |
| Task TP / FP / FN | 5 / 0 / 3 | 2 / 2 / 6 |
| Task precision | 5/5 = 100% | 2/4 = 50% |
| Task recall | 5/8 = 62.5% | 2/8 = 25% |
| Owner errors on paired tasks | 0/5 | 0/2 |
| Deadline errors on paired tasks | 2/5 | 0/2 |
| Evidence-support errors on paired tasks | 0/5 | 0/2 |
| Fully correct paired items | 3/8 labels | 2/8 labels |
| Correct empty-label cases | 3/3 | 1/3 |

Failures count as missing delivered labels and never as correct empty results.
Field denominators cover matched tasks only; raw errors on rejected outputs are
not hidden, but are outside those denominators. The baseline outperformed the
model on task precision, recall, successful-call rate, and fully correct items
in this run. No production-quality or generalization claim is justified.

## Per-case review

Task counts are TP/FP/FN under the existing rubric.

| Case / category | Baseline | Model | Model observation |
| --- | --- | --- | --- |
| 01 contraction/recipient | 0/0/1 | 0/0/1 | Changed quote escape/apostrophe representation rejected; raw owner was recipient Jules. |
| 02 accepted request | 0/0/1 | 0/0/1 | String-null deadline rejected. |
| 03 refusal | 0/0/0 | 0/1/0 | Negated commitment extracted as accepted work. |
| 04 unanswered request | 0/0/0 | 0/1/0 | No acceptance, but task extracted. |
| 05 suggestion | 0/0/0 | 0/0/0 | Correct empty response. |
| 06 ownerless commitment | 0/0/1 | 0/0/1 | Prompt example copied; absent quote rejected. |
| 07 dependency/recipient | 1/0/0 | 0/0/1 | String-null deadline rejected; dependency also omitted in raw task. |
| 08 relative deadline | 1/0/0 | 1/0/0 | Correct original next Wednesday deadline. |
| 09 multiple commitments | 2/0/0 | 1/0/1 | First commitment correct; second missed. |
| 10 recipient/owner | 1/0/0 | 0/0/1 | String-null deadline rejected. |

The baseline retains relative-time wording in action text but leaves deadlines
null in cases 08 and the second item of 09. Tasks still match by meaning; those
two deadline fields are wrong. The baseline misses contractions, accepted
requests using other wording, and ownerless commitments.

## Failures and structural diagnostics

All ten model responses parsed as JSON. Seven passed current output-schema
validation; three failed on string-null deadlines (02, 07, 10). The seven
schema-valid responses contained six items, two with nonmatching evidence (2/6):
case 01 altered quote spelling/escaping and case 06 copied a prompt example.
Those two calls failed evidence validation. Four items were delivered; all passed
quote and owner/deadline text-presence checks. Two were still false commitments.
No field-provenance error occurred in this run, and no connection, timeout, or
generation-length failure occurred. This does not imply those paths cannot fail.

Successful model-attempt median/max: 1.239/1.272 seconds. Failed attempts:
01 2.909 s, 02 1.246 s, 06 0.993 s, 07 1.151 s, 10 1.047 s. Baseline median/max:
0.000025/0.000094 seconds, with no failures. These are direct extraction-function
timings including loading and local HTTP, not Uvicorn/browser latency.

## Reproduction and release implication

```bash
.venv/bin/python -m evals.run --dataset validation --output /tmp/actiongraph-validation-new.jsonl
```

The recorded run used local `llama3.2:3b`, 1,024 generated-token cap and other
Ollama defaults. Full model digest, Ollama version, Python version, platform,
hashes, initial model warmth recorded as unknown, loading times and exact
durations are in [the raw run](validation-d21e6b6.jsonl).
[Pairings and reasons](review-validation-d21e6b6.json) preserve decisions.
There were no retries or warmup calls.

The demonstrated browser flow works, but current extraction reliability is a
release blocker for production-quality claims. Keep this first validation run
immutable. Further tuning makes these cases development data; create another
separately frozen set before claiming independent validation. Prioritize a clear
generation/policy improvement and repeated measurement over additional pipeline
complexity or presentation claims unsupported by these results.
