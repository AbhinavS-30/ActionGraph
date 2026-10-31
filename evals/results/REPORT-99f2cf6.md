# Refusal-example experiment — October 31, 2026

One rerun of the same ten development cases from clean source `99f2cf6`.
The only behavior change was an explicit refusal rule and a synthetic refused
request example in the prompt. Labels, schema, model, and generation settings
were unchanged. Default sampling and unmeasured run-to-run variation prevent
causal attribution from this single comparison. These are development results,
not independent validation. Codex semantic decisions remain provisional pending
human review.

The refused-request case still produced a false positive: the targeted fix did
not work in this run. The suggestion case became a correct negative, and the
unknown owner became JSON null. The unanswered-request case still produced a
false positive and now incorrectly assigned the meeting-end time "noon" as a
deadline with an unrelated evidence excerpt. The missing dependency, missed
second commitment, incomplete acceptance evidence, and string-null deadline
problems remain.

| Measure | Original model run | Refusal-example model run |
| --- | --- | --- |
| Successful attempts | 10/10 | 10/10 |
| Task TP / FP / FN | 6 / 4 / 2 | 6 / 3 / 2 |
| Task precision | 6/10 = 60% | 6/9 = 66.7% |
| Task recall | 6/8 = 75% | 6/8 = 75% |
| Owner errors on matched tasks | 1/6 | 0/6 |
| Deadline errors on matched tasks | 1/6 | 1/6 |
| Evidence-support errors on matched tasks | 1/6 | 1/6 |
| Fully correct matched items | 3/8 labels | 4/8 labels |
| Correct empty-label cases | 0/3 | 1/3 |

Model extraction wall-clock median/max were 1.022/2.098 seconds, including loading
and local HTTP, parsing, and evidence checks. Baseline median/max were
0.000042/0.000446 seconds. These are function-call timings, not hosted API latency.
No attempts failed, and no failed-call durations exist for this run.

Baseline task counts remained 6/0/2, with four fully correct items. The baseline
still has higher task precision than the model in this small sample.
All 10 model responses passed parsing and schema validation; all nine generated
quotes were nonblank exact transcript substrings (nonmatching evidence 0/9).
This did not prevent unsupported interpretations. Literal string-null deadlines
occurred in cases 03, 07, and 08; only case 07 was paired for field scoring.

Per-category counts and pairings are unchanged from the first report except that
case 05 changes from 0/1/0 to 0/0/0. Full per-case outputs, durations, Ollama version,
model digest, loading times, platform, and hashes are preserved in
[the raw run](comparison-99f2cf6.jsonl). Reasons and field decisions are in
[the review](review-99f2cf6.json).

Next: decide whether to keep this prompt variant after further review. Do not
describe refusal handling as fixed. Reliability work and untouched evaluation
cases are needed before claiming readiness beyond a local demonstration.
