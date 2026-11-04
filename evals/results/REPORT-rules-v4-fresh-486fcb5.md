# First frozen-v4 validation — November 4, 2026

Fourteen new synthetic cases and eleven labeled tasks were committed as `486fcb5`
before extraction. Rules v4 application source is unchanged from `aa3c999`.
No post-run label, rubric, or extractor changes occurred. Authoring used knowledge
of implementation and prior failures; this is not independent or blind validation,
real-meeting accuracy, or production certification. Semantic review is provisional
Codex review pending independent human adjudication. The set is now observed.

| Measure | Historical baseline | Rules v4 |
| --- | --- | --- |
| Successful calls | 14/14 | 14/14 |
| Task TP / FP / FN | 5 / 6 / 6 | 6 / 1 / 5 |
| Task precision | 5/11 = 45.5% | 6/7 = 85.7% |
| Task recall | 5/11 = 45.5% | 6/11 = 54.5% |
| Fully correct paired items / labels | 2/11 | 6/11 |
| Owner errors / paired tasks | 0/5 | 0/6 |
| Deadline errors / paired tasks | 3/5 | 0/6 |
| Correct empty-label cases | 2/5 | 4/5 |

## Case-level decisions

Counts are TP/FP/FN; paired field errors are scored separately.

| Case | Baseline | Rules | Finding |
| --- | --- | --- | --- |
| 01 contraction | 0/0/1 | 1/0/0 | Rules preserves owner and Thursday. |
| 02 accepted request | 0/0/1 | 1/0/0 | Rules retains two-line evidence and tomorrow. |
| 03 two local deadlines | 1/0/1 | 2/0/0 | Baseline pairs first task with erroneous combined deadline; rules exact. |
| 04 explicit cancellation | 0/1/0 | 0/0/0 | Baseline returns cancelled promise. |
| 05 recommitment | 1/2/0 | 1/0/0 | Only later Friday promise matches; cancelled Monday and negated work are baseline extras. |
| 06 dependency date | 1/0/0 | 1/0/0 | Baseline incorrectly promotes prerequisite Tuesday to task deadline. |
| 07 ownerless work | 0/0/1 | 0/0/1 | Both miss genuine work. |
| 08 clock/verb | 1/0/0 | 0/0/1 | Baseline task matches but clock deadline field is absent; rules misses work. |
| 09 object list | 1/0/0 | 0/0/1 | One review task, two objects; rules skips it. |
| 10 explicit shared date | 0/1/2 | 0/0/2 | Both is explicit shared scope; rules skips, baseline bundles both tasks. |
| 11 unanswered request | 0/0/0 | 0/0/0 | Both empty. |
| 12 negation | 0/1/0 | 0/0/0 | Baseline extracts negated work. |
| 13 paraphrased withdrawal | 0/1/0 | 0/1/0 | Both return a withdrawn promise despite exact source evidence. |
| 14 declined request | 0/0/0 | 0/0/0 | Both empty. |

Cases 03, 06 and 08 pair the same core task and score field mistakes separately.
Case 10 bundles two atomic scopes and is unmatched, consistent with the earlier
compound rubric. Case 13 is a false positive even though its wording is outside
the documented cancellation grammar. These judgments are exposed for adjudication.

## Execution and audit

No failures or model calls occurred. All delivered quotes and non-null fields
passed source-text checks: 11/11 baseline items and 7/7 rules items. That does not
establish semantic support; withdrawn work passes these checks too. Direct-call
median/max seconds: baseline 0.000005/0.000058, rules 0.000035/0.000135. These are
noisy in-process timings, not API/browser latency or a speedup claim.

- [Raw attempts and metadata](rules-v4-fresh-486fcb5.jsonl)
- [Pairings and decisions](review-rules-v4-fresh-486fcb5.json)
- [Frozen labels](../rules-validation-v4.json)

Command:

```bash
.venv/bin/python -m evals.run --contract rules --dataset rules-v4-validation --output /tmp/actiongraph-v4-fresh-486fcb5.jsonl
```

Metadata records clean committed source, dataset hash, rules version and
model_used=false. Preserve this first result. Further tuning uses an observed
set and must be described accordingly. Broad extraction quality remains a release
limitation. Next review release requirements against these findings and decide
whether bounded scope is sufficient or which missing behavior to address; no
new grammar change is implied by this report. Recording and public page remain
deferred under the user's instruction.
