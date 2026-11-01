# JSON-null prompt experiment — November 1, 2026

Candidate source: clean commit `fcc91ec`. Added an explicit distinction between
unquoted null and string-null plus one synthetic example with unknown owner and
deadline. Validator, schema, dataset, and generation settings were unchanged.
This candidate is **not adopted**: the previous prompt is restored after the run.
This single stochastic development comparison cannot establish causality or
generalization. Semantic pairings are provisional Codex review pending human
adjudication.

| Measure | Previous strict run | JSON-null candidate |
| --- | --- | --- |
| Successful calls | 4/10 | 6/10 |
| String-null validation failures | 6/10 | 3/10 |
| Evidence-rejection failures | 0/10 | 1/10 |
| Delivered task TP / FP / FN | 5 / 0 / 3 | 3 / 3 / 5 |
| Delivered task precision | 5/5 = 100% | 3/6 = 50% |
| Delivered task recall | 5/8 = 62.5% | 3/8 = 37.5% |
| Fully correct matched items | 5/8 labels | 3/8 labels |
| Correct empty-label cases | 0/3 | 0/3 |

No owner, deadline, or evidence-support errors occurred on the three paired
candidate tasks. Incorrect unmatched items and failures remain in task counts;
they are not omitted to improve field scores. The unchanged baseline yielded
6 TP, 0 FP, 2 FN and four fully correct items, with 10/10 successful calls and
3/3 correct empty-label cases.

## Per-case review

Task counts are TP/FP/FN on delivered items; failures yield no delivered FP and
do not count as correct negatives.

| Case / category | Baseline | Candidate model | Outcome |
| --- | --- | --- | --- |
| 01 explicit commitment | 1/0/0 | 1/0/0 | Correct. |
| 02 accepted request | 0/0/1 | 0/0/1 | String-null deadline rejected. |
| 03 refused request | 0/0/0 | 0/0/0 | String-null deadline rejected; refusal still proposed. |
| 04 unanswered request | 0/0/0 | 0/1/0 | Extracted unanswered task with unrelated meeting-end quote. |
| 05 suggestion | 0/0/0 | 0/0/0 | Copied Maya report prompt example; rejected for absent evidence. |
| 06 unknown owner | 0/0/1 | 1/0/0 | Correct. |
| 07 unspecified deadline | 1/0/0 | 0/0/1 | String-null deadline rejected. |
| 08 dependency | 1/0/0 | 0/1/1 | Dependency omitted from task; cannot match under rubric. |
| 09 relative deadline | 1/0/0 | 1/0/0 | Correct. |
| 10 mixed discussion | 2/0/0 | 0/1/2 | Extracted unanswered FAQ request; missed both commitments. |

All 10 model texts were valid JSON; 7/10 passed current schema validators.
Those schema-valid responses contained seven items: one nonmatching evidence
quote (1/7), rejected by the service. That quote copied the report example from
the prompt, demonstrating example leakage despite explicit instructions. Six
items were delivered, three of which were task false positives. Exact quote
presence therefore still did not establish semantic support.

Successful model-call median/max: 1.076/2.692 seconds. Failed calls: case 02
1.371 s, 03 1.248 s, 05 1.004 s, 07 1.084 s. Baseline median/max:
0.000059/0.000396 seconds (no baseline failures). Times are direct extraction
calls including model loading and HTTP, not hosted or browser latency.

Runtime was Python 3.12.13, Ollama 0.33.3, macOS ARM64, local `llama3.2:3b`,
Q4_K_M. Model digest, effective settings (`num_predict=1024`, other options at
defaults), initial warmth recorded as unknown, load times, and exact durations
are retained in [the raw run](comparison-fcc91ec.jsonl). There were no retries,
warmup, connection failures, timeouts, or generation-length stops. Model identity
and dataset hash match the preceding run.
[Pairings and reasons](review-fcc91ec.json) use the unchanged matching rubric.

Decision: preserve the failed experiment and restore the preceding prompt.
Do not describe fewer string-null failures or more completed calls as an overall
quality improvement. Next investigate the structured generation contract and
measure a focused alternative before further prompt accumulation; independent
cases and repeated runs remain necessary.
