# Rules v5 observed-case replay — November 4, 2026

Clean source fa37f4e, rules_version=5. Original labels, datasets, baseline and
matching rubric are unchanged. The v4 validation set is now observed and informed
this targeted withdrawal fix. This is regression evidence, not fresh/independent
validation, broad meeting accuracy or production certification. Review remains
provisional Codex review; independent human adjudication is pending.

| Dataset | Cases / labels | v4 TP / FP / FN | v5 TP / FP / FN | Fully correct items / labels | Correct empty-label cases |
| --- | --- | --- | --- | --- | --- |
| Development | 10 / 8 | 7 / 0 / 1 | 7 / 0 / 1 | 7 / 8 | 3 / 3 |
| Validation (observed) | 10 / 8 | 7 / 0 / 1 | 7 / 0 / 1 | 7 / 8 | 3 / 3 |
| Rules-focused v1 (observed) | 12 / 9 | 7 / 0 / 2 | 7 / 0 / 2 | 7 / 9 | 4 / 4 |
| Frozen-v4 set (observed) | 14 / 11 | 6 / 1 / 5 | 6 / 0 / 5 | 6 / 11 | 5 / 5 |

Only v4-check-13 rules output changes: the withdrawn publish promise is removed,
matching the original empty label. Every other rules output and every baseline
output is identical to the preserved v4 runs. On the fourteen-case set precision
changes from 6/7 to 6/6, recall stays 6/11 (54.5%). The five misses remain:
ownerless work, unsupported verb/clock time, one task with an object list and two
explicit shared-deadline tasks. The narrow grammar still misses genuine work.
No result here supports a general zero-false-positive claim.

All 46 rules attempts and 46 baseline attempts succeeded without model calls.
Every returned evidence quote and non-null field passed text-presence checks;
those do not establish semantic support. Existing task pairings and field review
are retained, with only the withdrawal negative judgment updated. Baseline
TP/FP/FN remains 6/0/2, 5/0/3, 4/3/5 and 5/6/6 respectively. Timings are noisy
in-process durations recorded per attempt, not browser/API latency or speedup.

## Audit artifacts

- [Development](rules-v5-fa37f4e-development.jsonl)
- [Observed validation](rules-v5-fa37f4e-validation.jsonl)
- [Rules-focused v1](rules-v5-fa37f4e-rules-validation.jsonl)
- [Observed frozen-v4 set](rules-v5-fa37f4e-rules-v4-validation.jsonl)
- [Pairings and decisions](review-rules-v5-fa37f4e.json)
- [First v4 validation, including withdrawal failure](REPORT-rules-v4-fresh-486fcb5.md)
- [Earlier three-set v4 replay](REPORT-rules-v4-aa3c999.md)

Metadata records clean source, unchanged dataset hashes, Python/platform,
effective settings and model_used=false. Command per DATASET, separate OUTPUT:

```bash
.venv/bin/python -m evals.run --contract rules --dataset DATASET --output OUTPUT
```

DATASET: development, validation, rules-validation, rules-v4-validation.
No extractor or labels changed after collection. Broader cancellation phrasing,
nonadjacent references and compound antecedents remain unsupported. Existing
saved sessions retain their original rules version and snapshots; this change
only affects future extraction/session creation. Next reconcile remaining local
resource and release scope; do not describe observed-case tuning as independent
quality improvement. Public page and video remain deferred.
