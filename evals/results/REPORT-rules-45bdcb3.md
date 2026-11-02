# Limited rules engine v1 — November 2, 2026

Clean source `45bdcb3`. The user approved a rule-based default demo mode after
local-model experiments failed to establish reliable quality. The historical
baseline and experimental model paths are retained, not silently replaced in
their reports. The public API now labels its selected engine and scope limits.

Both existing synthetic datasets were known during rule implementation. The
following is a known-case development comparison, not held-out validation or
evidence of real-meeting accuracy. No new model inference occurred.

| Measure | Development baseline | Development rules | Previously observed validation baseline | Previously observed validation rules |
| --- | --- | --- | --- | --- |
| Successful attempts | 10/10 | 10/10 | 10/10 | 10/10 |
| Task TP / FP / FN | 6/0/2 | 6/0/2 | 5/0/3 | 6/0/2 |
| Task precision | 6/6 = 100% | 6/6 = 100% | 5/5 = 100% | 6/6 = 100% |
| Task recall | 6/8 = 75% | 6/8 = 75% | 5/8 = 62.5% | 6/8 = 75% |
| Fully correct paired items | 4/8 labels | 6/8 labels | 3/8 labels | 6/8 labels |
| Owner errors on paired tasks | 0/6 | 0/6 | 0/5 | 0/6 |
| Deadline errors on paired tasks | 2/6 | 0/6 | 2/5 | 0/6 |
| Evidence-support errors on paired tasks | 0/6 | 0/6 | 0/5 | 0/6 |
| Correct empty-label cases | 3/3 | 3/3 | 3/3 | 3/3 |

Every paired rules item exactly equals the labeled item, including evidence and
review status. The rubric and labels were unchanged. All rule outputs passed
schema, evidence, and field-text checks; nonmatching evidence was 0/6 generated
items on each set. No calls failed, so no failed-call durations exist. A successful
rules attempt means the grammar ran, not that every transcript commitment was found.

## Case coverage

| Set | Cases found by rules | Cases with missed labeled work | Correct empty negatives |
| --- | --- | --- | --- |
| Development | 01, 07, 08, 09, both items in 10 | 02 accepted request; 06 ownerless work | 03, 04, 05 |
| Previously observed validation | 01, 07, 08, both items in 09, 10 | 02 accepted request; 06 ownerless work | 03, 04, 05 |

The new mode handles first-person contractions, speaker-versus-recipient owner
selection, supported trailing deadlines, and dependency preservation within its
grammar. It intentionally does not resolve cross-line acceptance or ownerless
work. Unsupported verbs, indirect/compound tasks, unresolved pronouns and timing
forms may be missed. Cross-line corrections, sarcasm, or semantic conflicts can
still invalidate a matched line. Every item requires human review.

## Timing and artifacts

Rules direct-call median/max: development 0.000013/0.000115 seconds; previously
observed validation 0.000007/0.000118 seconds. Baseline median/max:
0.000005/0.000090 and 0.000005/0.000052 seconds respectively. These in-process
microsecond measurements are noisy, not browser/hosted latency or a meaningful
speedup claim. No Ollama inventory/generation requests or downloads occurred.

- [Development raw run](rules-45bdcb3-development.jsonl)
- [Previously observed validation raw run](rules-45bdcb3-validation.jsonl)
- [Pairings and field review](review-rules-45bdcb3.json)

Metadata records clean source, dataset name/hash, `model_used=false`, Python and
platform; the rules descriptor hash is not a model prompt. Source commit records
the grammar implementation. Baseline outputs and all historical model results
remain available. A separately frozen new set is required for future validation.

## Live API smoke

The actual local Uvicorn server returned HTTP 200 for a default-engine request:

```json
{"transcript": "Asha: I'll email Ben the agenda by Thursday."}
```

Observed: action Email Ben the agenda; owner Asha; deadline Thursday; exact
sentence evidence; needs_review; `engine: rules`; a nonempty scope notice in
`limitations`. Blank input returned 422. OpenAPI exposes rules/ollama selection
with rules as default. This was an HTTP check, not a new browser interaction or
video recording. Unit tests additionally assert no Ollama client is constructed
for default rules requests and no silent fallback after explicit model failures.
