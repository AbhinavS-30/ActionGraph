# Rules v2 observed-case replay — November 3, 2026

Clean source `5a696b4`; rules_version=2. Original labels and matching rubric
are unchanged. These datasets were already inspected and informed the change:
this measures a targeted regression fix, not independent validation or general
meeting accuracy. Review is provisional Codex review; human adjudication pending.

| Dataset | Cases / labeled tasks | Rules TP / FP / FN | Fully correct items | Correct empty-label cases |
| --- | --- | --- | --- | --- |
| Development | 10 / 8 | 6 / 0 / 2 | 6 / 8 | 3 / 3 |
| Validation (now observed) | 10 / 8 | 6 / 0 / 2 | 6 / 8 | 3 / 3 |
| Rules-focused (now observed) | 12 / 9 | 4 / 0 / 5 | 4 / 9 | 4 / 4 |

All 32 rules attempts and 32 baseline attempts succeeded without model calls.
The only output change from v1 is rules-check-12: the cancelled promise is now
removed. All baseline outputs and every other rules output are identical to the
preserved previous runs. On the rules-focused set, task precision changes from
4/5 to 4/4; recall remains 4/9. These small, known-case fractions do not establish
production readiness. Five misses remain: unsupported verb/time, ownerless work,
accepted request, and two compound tasks. All paired rule fields remain correct
under the original review; exact quotes alone do not establish correctness.

Earlier task pairings and judgments apply unchanged to the first two sets:
[original review](review-rules-45bdcb3.json) and
[report](REPORT-rules-45bdcb3.md). For the third set, the
[updated review](review-rules-v2-5a696b4.json) changes only the cancellation
judgment; the [first v1 result](REPORT-rules-validation-042cf19.md) is preserved.
Baseline scores remain 6/0/2, 5/0/3, and 4/3/5 respectively.

Raw artifacts record source, clean tree, dataset hashes, runtime settings,
per-attempt durations and model_used=false:

- [Development](rules-v2-5a696b4-development.jsonl)
- [Validation](rules-v2-5a696b4-validation.jsonl)
- [Rules-focused](rules-v2-5a696b4-rules-validation.jsonl)

Commands: `.venv/bin/python -m evals.run --contract rules --dataset DATASET --output OUTPUT`
with DATASET `development`, `validation`, or `rules-validation`. Timings are
in-process calls, not API/browser latency; no speedup claim is made.

Cancellation support is bounded to the documented same-speaker/task grammar.
Broader correction, paraphrase and attribution remain unsupported. Public page
creation and recording remain deferred until the remaining release gates pass.
