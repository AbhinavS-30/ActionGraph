# Rules v3 observed-case replay — November 3, 2026

Clean source `c9e5e64`, rules_version=3. The three datasets and rubric are unchanged.
These cases were known during implementation, including the accepted requests:
this is regression evidence, not held-out accuracy. Semantic review is provisional
Codex review; independent human adjudication remains pending.

| Dataset | Cases / labels | v2 TP / FP / FN | v3 TP / FP / FN | v3 fully correct / labels | Correct empty-label cases |
| --- | --- | --- | --- | --- | --- |
| Development | 10 / 8 | 6 / 0 / 2 | 7 / 0 / 1 | 7 / 8 | 3 / 3 |
| Validation (observed) | 10 / 8 | 6 / 0 / 2 | 7 / 0 / 1 | 7 / 8 | 3 / 3 |
| Rules-focused (observed) | 12 / 9 | 4 / 0 / 5 | 5 / 0 / 4 | 5 / 9 | 4 / 4 |

Only eval-02, validation-02 and rules-check-07 change: each now returns the
single explicitly accepted task with exactly the labeled action, owner, null
deadline, two-line evidence and needs_review status. Every other rules output
and every baseline output is identical to v2. Cancellation remains excluded.
Task recall is 7/8, 7/8 and 5/9 respectively. Delivered task precision is 7/7,
7/7 and 5/5 on these small observed sets, not a general reliability estimate.
The first two sets each still miss ownerless work. The third misses ownerless
work, unsupported verb/time and two compound tasks. No new negative-case outputs
appeared. Baseline TP/FP/FN remains 6/0/2, 5/0/3 and 4/3/5 respectively.

All 32 rules attempts and 32 baseline attempts succeeded; no model calls occurred.
Every returned quote matched the transcript exactly and non-null fields passed
text-presence checks. Those checks alone do not prove semantic correctness.
All paired rules items have correct fields under the preserved rubric. Timings
are direct in-process calls stored per attempt; no API latency or speedup claim.

## Audit artifacts

- [Development raw records](rules-v3-c9e5e64-development.jsonl)
- [Validation raw records](rules-v3-c9e5e64-validation.jsonl)
- [Rules-focused raw records](rules-v3-c9e5e64-rules-validation.jsonl)
- [Pairings and decisions for all three sets](review-rules-v3-c9e5e64.json)
- [Preserved v2 comparison](REPORT-rules-v2-5a696b4.md)

Metadata records clean source, dataset hash, rules version, platform/settings and
model_used=false. Collection command for each dataset:

```bash
.venv/bin/python -m evals.run --contract rules --dataset DATASET --output OUTPUT
```

DATASET is development, validation or rules-validation. Original review pairings
are retained except the newly matched request in each set. No labels, baseline,
or extractor were changed after this run. Broader dialogue interpretation remains
unsupported; the public page and recording remain deferred until release gates.
