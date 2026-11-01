# List-contract experiment — November 1, 2026

Clean source `2ccb473`; ten existing synthetic development cases; system recorded
as `ollama_lists`. This is an evaluation-only path, not the public API. Owner and
deadline use zero-or-one-string lists, translated to the existing public
string-or-null output with strict validation. Review status is assigned by the
application. Prompt field wording and examples are adapted to this representation.
These changes form one contract experiment, not an isolated wording change.
Model, sampling defaults, 1,024-token output cap, and labels are unchanged.

## Provisional delivered results

| Measure | Public strict run | Experimental lists | Baseline |
| --- | --- | --- | --- |
| Successful attempts | 4/10 | 9/10 | 10/10 |
| Task TP / FP / FN | 5 / 0 / 3 | 6 / 4 / 2 | 6 / 0 / 2 |
| Task precision | 5/5 = 100% | 6/10 = 60% | 6/6 = 100% |
| Task recall | 5/8 = 62.5% | 6/8 = 75% | 6/8 = 75% |
| Fully correct matched items | 5/8 labels | 5/8 labels | 4/8 labels |
| Owner errors on paired tasks | 0/5 | 0/6 | 0/6 |
| Deadline errors on paired tasks | 0/5 | 1/6 | 2/6 |
| Evidence-support errors on paired tasks | 0/5 | 0/6 | 0/6 |
| Correct empty-label cases | 0/3 | 0/3 | 3/3 |

The list variant eliminated string-null failures in this run but exposed more
semantically invalid outputs to callers. Its single failure was unsupported
evidence in case 06, where the model copied the Maya report prompt example.
It is **not adopted in the API**. One stochastic development run does not establish
reliable improvement; independent human adjudication and untouched cases remain
pending. Comparing only completion rates would conceal the four false positives.

## Per-case task counts and decisions

Counts are TP/FP/FN under the unchanged matching rubric.

| Case / category | Baseline | Lists | Observation |
| --- | --- | --- | --- |
| 01 explicit commitment | 1/0/0 | 1/0/0 | Correct. |
| 02 accepted request | 0/0/1 | 1/0/0 | Correct task; invented Friday deadline instead of null. |
| 03 refused request | 0/0/0 | 0/1/0 | Declined work extracted, also with invented Friday deadline. |
| 04 unanswered request | 0/0/0 | 0/1/0 | Unaccepted work extracted with meeting-end noon as deadline. |
| 05 suggestion | 0/0/0 | 0/1/0 | Suggestion treated as a commitment. |
| 06 unknown owner | 0/0/1 | 0/0/1 | Prompt example copied; absent evidence rejected. |
| 07 unspecified deadline | 1/0/0 | 1/0/0 | Correct. |
| 08 dependency | 1/0/0 | 0/1/1 | Dependency omitted from action; also wrong owner Nina. |
| 09 relative deadline | 1/0/0 | 1/0/0 | Correct. |
| 10 mixed discussion | 2/0/0 | 2/0/0 | Both actual commitments correct. |

The owner error in case 08 and deadlines in unmatched false positives are visible
in outputs but are outside the paired-task field denominators above. The failed
case yields a false negative, not a successful empty response.

## Diagnostics and reproduction

All ten responses passed JSON parsing, the list schema, and public conversion
validation. Their eleven generated items included one nonmatching evidence quote
(1/11), rejected by the evidence check. Ten items were delivered; quote presence
did not prevent false commitments. No token-limit stops, string-null failures,
connection failures, or timeouts occurred.

Successful model-call median/max: 1.083/1.707 seconds. Failed case 06: 0.868
seconds. Baseline median/max: 0.000050/0.000253 seconds with no failures. These
are direct-call wall-clock durations including loading/HTTP where applicable,
not browser or hosted API latency; baseline microsecond timings are noisy.

The experiment used local `llama3.2:3b`, Ollama 0.33.3, Python 3.12.13, macOS
ARM64, default sampling, and no warmup/retries. Initial model warmth was unknown.
Complete durations, loading, digest, runtime settings, and actual instruction
hash are in [the raw run](comparison-2ccb473.jsonl).
[Review pairings](review-2ccb473.json) are provisional Codex judgments.

Run command:

```bash
.venv/bin/python -m evals.run --contract lists --output /tmp/actiongraph-lists-new.jsonl
```

Decision: retain as an isolated experiment. The remaining bottleneck is deciding
whether a commitment exists and attributing its fields; formatting alone is not
enough. Next investigate a focused commitment-decision stage before generating
final action items, without weakening public validation or silently dropping
failures. Keep changes and later measurements separate from this report.
