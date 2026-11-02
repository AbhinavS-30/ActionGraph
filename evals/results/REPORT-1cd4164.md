# Paired example-free prompt comparison — November 2, 2026

Clean source `1cd4164`; development cases only. Two repetitions in the
pre-recorded order public-1, concise-1, public-2, concise-2. Each run includes
the unchanged baseline. Prompt text is the only intended extraction difference:
same public schema, parser, evidence/provenance guards, review-state enforcement,
model and settings. The candidate has no illustrative names/tasks/dates and
places exclusion rules first. It remains outside the API.

Selection criteria were committed before outputs were inspected: zero delivered
FP in both candidate runs, fully correct items at least as high as paired public
runs, no more failed calls, and a strict fully-correct-item improvement in one
pair. These are experiment selection criteria, not production accuracy guarantees.
The candidate **fails selection and is not adopted**.

## Provisional semantic results

| Measure | Public 1 | Concise 1 | Public 2 | Concise 2 |
| --- | --- | --- | --- | --- |
| Successful attempts | 2/10 | 5/10 | 5/10 | 6/10 |
| Task TP / FP / FN | 2/0/6 | 1/4/7 | 6/0/2 | 5/1/3 |
| Task precision | 2/2 = 100% | 1/5 = 20% | 6/6 = 100% | 5/6 = 83.3% |
| Task recall | 2/8 = 25% | 1/8 = 12.5% | 6/8 = 75% | 5/8 = 62.5% |
| Fully correct paired items | 2/8 | 1/8 | 5/8 | 4/8 |
| Owner errors on paired tasks | 0/2 | 0/1 | 1/6 | 0/5 |
| Deadline errors on paired tasks | 0/2 | 0/1 | 0/6 | 1/5 |
| Evidence-support errors on paired tasks | 0/2 | 0/1 | 0/6 | 0/5 |
| Correct empty-label cases | 0/3 | 0/3 | 0/3 | 0/3 |

Baseline counts in every run remain TP/FP/FN 6/0/2, four fully correct items,
10/10 successful attempts and 3/3 correct negative cases. Semantic decisions are
provisional Codex review pending independent human adjudication. These repeatedly
used development cases are not held-out validation. No validation run was added.

Concise-1 often emitted only a verb ("send", "investigate") or "Established
commitment" as the action. These omit task object/scope and cannot match the
labels under the existing rubric, even when the quote contains the missing
information. Concise-2 extracted declined work and used an acceptance sentence
as a deadline. Public-2 found both mixed-case tasks but left the second owner null.
More completed calls did not mean more fully correct items in either pair.

## Per-category task counts

Each entry is TP/FP/FN. Categories contain one case each.

| Case | Public 1 | Concise 1 | Public 2 | Concise 2 |
| --- | --- | --- | --- | --- |
| 01 explicit | 1/0/0 | 0/1/1 | 1/0/0 | 1/0/0 |
| 02 accepted | 0/0/1 | 0/0/1 | 0/0/1 | 1/0/0 |
| 03 refused | 0/0/0 | 0/0/0 | 0/0/0 | 0/1/0 |
| 04 unanswered | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| 05 suggestion | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| 06 ownerless | 0/0/1 | 0/1/1 | 1/0/0 | 1/0/0 |
| 07 no deadline | 0/0/1 | 0/1/1 | 1/0/0 | 0/0/1 |
| 08 dependency | 0/0/1 | 0/0/1 | 0/0/1 | 0/0/1 |
| 09 relative | 1/0/0 | 1/0/0 | 1/0/0 | 1/0/0 |
| 10 mixed | 0/0/2 | 0/1/2 | 2/0/0 | 1/0/1 |

Failed empty-label cases receive no correct-negative credit. Their zero task
counts must be read alongside failure status in raw outputs, not as correct
empty results.

## Timing and failures

All 40 response texts parsed as JSON. Schema-valid responses were 3/10, 6/10,
6/10, and 7/10 for public-1, concise-1, public-2, concise-2 respectively.
Nonmatching evidence among schema-valid generated items was public-1 1/3,
concise-1 0/6, public-2 3/9, concise-2 0/7. Candidate outputs with zero fabricated
quotes still had wrong task meaning or unsupported fields. These diagnostic
denominators include items rejected by the service and differ from delivered
task counts.

Successful direct-call median/max seconds: public-1 1.849/2.650; concise-1
1.084/1.304; public-2 1.045/1.905; concise-2 1.099/1.624. Failed-call durations
remain separate in each raw run, including failures longer than those successful
maxima. No silent retry, warmup, timeout, connection failure, or token-limit stop
occurred. Public-1 had seven ValidationError and one UnsupportedEvidenceError;
public-2 four ValidationError and one UnsupportedEvidenceError; concise-1 four
ValidationError and one UnsupportedFieldError; concise-2 three ValidationError
and one UnsupportedFieldError. Values are extraction-function timings, not
browser/hosted API latency; loading and initial residency may affect comparisons.

All four runs used local `llama3.2:3b`, 1,024 output-token cap and other default
sampling settings. Initial model warmth was unknown, and later runs reuse a
running model. Two repetitions, fixed order, and non-deterministic sampling do
not establish causal effects or generalization. The wide public-run variation
is itself a reliability concern. The successful-call precision values conceal
many rejected attempts and must not be advertised alone.

## Audit artifacts

- [Public 1](comparison-1cd4164-public-r1.jsonl)
- [Concise 1](comparison-1cd4164-concise-r1.jsonl)
- [Public 2](comparison-1cd4164-public-r2.jsonl)
- [Concise 2](comparison-1cd4164-concise-r2.jsonl)
- [Pairings and reasons](review-1cd4164.json)

Raw files include complete outputs, all durations, failures, instruction and data
hashes, model digest, version, platform, settings and load durations. Preserve all
four runs. Do not adopt the candidate or claim overall quality improvement.
Before further prompt tuning, reassess whether a clearly limited deterministic
mode is a more dependable demonstration path, while retaining local-model
extraction as explicitly experimental. That product change requires agreement.
