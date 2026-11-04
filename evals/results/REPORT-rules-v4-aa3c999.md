# Rules v4 observed-case replay — November 4, 2026

Clean source `aa3c999`, rules_version=4. Original datasets, labels and matching
rubric are unchanged. These cases were known during implementation; this is
regression evidence, not independent validation or general meeting accuracy.
Review remains provisional Codex review pending human adjudication.

| Dataset | Cases / labels | v3 TP / FP / FN | v4 TP / FP / FN | Fully correct / labels | Correct empty-label cases |
| --- | --- | --- | --- | --- | --- |
| Development | 10 / 8 | 7 / 0 / 1 | 7 / 0 / 1 | 7 / 8 | 3 / 3 |
| Validation (observed) | 10 / 8 | 7 / 0 / 1 | 7 / 0 / 1 | 7 / 8 | 3 / 3 |
| Rules-focused (observed) | 12 / 9 | 5 / 0 / 4 | 7 / 0 / 2 | 7 / 9 | 4 / 4 |

Only rules-check-11 changes. The promise to prepare release notes and upload the
package now produces two separate items, exactly matching the original labels
including owner, null deadlines, full-line evidence and needs_review status.
Every other rules output and every baseline output is identical to v3.
Baseline TP/FP/FN remains 6/0/2, 5/0/3 and 4/3/5 respectively.

All 32 rules attempts and 32 baseline attempts succeeded without model calls.
Every returned quote matched its transcript and all non-null fields passed
text-presence checks. Those checks alone do not prove semantic correctness.
All paired rules fields remain correct under the preserved review. The first
two sets still miss ownerless work; the third misses ownerless work and an
unsupported verb/clock-time form. No new negative-case outputs appeared.
Precision is 7/7 on each tiny observed set; recall is 7/8, 7/8 and 7/9. These
fractions do not establish real-meeting reliability or production readiness.
Per-attempt durations are direct in-process timings, not API/browser latency;
no speedup claim is made.

## Audit artifacts

- [Development raw attempts](rules-v4-aa3c999-development.jsonl)
- [Observed validation raw attempts](rules-v4-aa3c999-validation.jsonl)
- [Rules-focused raw attempts](rules-v4-aa3c999-rules-validation.jsonl)
- [Pairings and decisions](review-rules-v4-aa3c999.json)
- [Preserved v3 report](REPORT-rules-v3-c9e5e64.md)

Metadata records clean source, dataset hashes, rules version, runtime/platform
and model_used=false. Run command for each DATASET (development, validation,
rules-validation), using a separate OUTPUT file:

```bash
.venv/bin/python -m evals.run --contract rules --dataset DATASET --output OUTPUT
```

No labels, baseline or implementation were changed after collection. Only the
two newly matched compound labels change review pairings. Next evaluate frozen
rules v4 on new pre-labeled cases that include supported and unsupported forms;
do not keep expanding grammar merely to fit these observed examples. Independent
human review and broader release checks remain pending. Public page and recording
remain deferred until the agreed readiness gates are met.
