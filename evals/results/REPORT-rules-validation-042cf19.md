# First rules-focused validation — November 3, 2026

Clean source `042cf19`. Twelve new synthetic cases with nine labeled tasks were
committed before the first rules/baseline run. Implementation, labels, and rubric
were not changed after inspection. The cases include supported constructions and
known limitations: accepted requests, ownerless work, compound tasks, unsupported
verbs/times, and later cancellation. They were authored with knowledge of rules
v1, not independently or blindly. Results are provisional Codex review pending
human adjudication, not real-world accuracy or production certification.

## Delivered results

| Measure | Historical baseline | Rules v1 |
| --- | --- | --- |
| Successful attempts | 12/12 | 12/12 |
| Task TP / FP / FN | 4/3/5 | 4/1/5 |
| Task precision | 4/7 = 57.1% | 4/5 = 80% |
| Task recall | 4/9 = 44.4% | 4/9 = 44.4% |
| Fully correct paired items | 1/9 labels | 4/9 labels |
| Owner errors on paired tasks | 0/4 | 0/4 |
| Deadline errors on paired tasks | 3/4 | 0/4 |
| Evidence-support errors on paired tasks | 0/4 | 0/4 |
| Correct empty-label cases | 2/4 | 3/4 |

Rules returned an earlier promise that was explicitly cancelled in a later line.
That is a false positive even though cross-line cancellation is a documented
limitation. Five real tasks were missed outside the supported grammar. Neither
successful execution nor perfect quote presence proves complete meeting
understanding. Do not advertise the earlier known-case zero-FP results alone.

## Per-case review

Task counts are TP/FP/FN; field scoring is separate.

| Case / category | Baseline | Rules | Observation |
| --- | --- | --- | --- |
| 01 speaker/recipient | 1/0/0 | 1/0/0 | Both correct. |
| 02 contraction/relative | 0/0/1 | 1/0/0 | Rules supports contraction and next Friday. |
| 03 prerequisite date | 1/0/0 | 1/0/0 | Baseline promotes prerequisite Monday to task deadline; rules retains dependency and null task deadline. |
| 04 absolute date | 1/0/0 | 1/0/0 | Baseline leaves date in action and null deadline; rules correct. |
| 05 unsupported verb/time | 1/0/0 | 0/0/1 | Genuine work missed by rules; baseline misses clock deadline. |
| 06 ownerless agreement | 0/0/1 | 0/0/1 | Both miss agreed work. |
| 07 accepted request | 0/0/1 | 0/0/1 | Both miss cross-line acceptance. |
| 08 negation | 0/1/0 | 0/0/0 | Baseline extracts negated work; rules excludes it. |
| 09 uncertainty | 0/0/0 | 0/0/0 | Both correctly exclude tentative offer. |
| 10 unanswered request | 0/0/0 | 0/0/0 | Both correctly return empty. |
| 11 compound tasks | 0/1/2 | 0/0/2 | Baseline bundles two task scopes into one; rules skips compound line. |
| 12 later cancellation | 0/1/0 | 0/1/0 | Both return the cancelled promise. |

Case 03 pairs the same core task and prerequisite event for both systems; the
misplaced prerequisite date is scored as a deadline error. Case 11's bundled
action is broader than either atomic label, so it is unmatched under the scope
rule. These judgment calls are explicit in the review and should receive human
adjudication. They are not automatic string-similarity scores.

## Execution and audit

No failures or model calls occurred. All outputs passed schema, exact evidence,
and field-text checks: nonmatching evidence 0/7 baseline items and 0/5 rules items.
The cancellation false positive still passes those checks. Baseline direct-call
median/max: 0.000004/0.000088 seconds. Rules: 0.000003/0.000113 seconds. These are
noisy in-process timings, not browser/API latency or a meaningful speedup claim.

- [Raw attempts and metadata](rules-validation-042cf19.jsonl)
- [Pairings and decisions](review-rules-validation-042cf19.json)

Metadata records clean source, dataset hash, Python/platform and model_used=false.
Command used:

```bash
.venv/bin/python -m evals.run --contract rules --dataset rules-validation --output /tmp/actiongraph-rules-validation-new.jsonl
```

Preserve this first result. The set is now observed; tuning against it makes it
development data for later versions. Keep the public demo explicitly scoped to
line-based proposals requiring human review, and disclose cancellation and missed
forms. No general production-ready extraction claim is supported. Next prepare
the project page and recorded demo around these measured capabilities and limits;
any cancellation support should be a separate agreed, tested change.
