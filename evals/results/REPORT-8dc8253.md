# First development comparison — October 31, 2026

This is one run on ten short synthetic development cases, not a held-out or
real-world benchmark. Semantic pairings were reviewed by Codex using the rubric
written before the run; independent human adjudication remains pending. The
following scores are provisional. No prompt, label, or generation settings were
changed after seeing the outputs.

Source: clean commit `8dc82530ca5024f6b0d7ef4a321d938dd9109c63`.
Runtime: Python 3.12.13, Ollama 0.33.3, macOS 26.6.2, ARM64.
Model: `llama3.2:3b`, Q4_K_M, digest
`a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72`.
Generation: Ollama defaults, schema-constrained format, nonstreaming; no retries
or warmup. Initial model residency was unknown. The first response reported
1.320 seconds loading; subsequent reported load times were at most 0.012 seconds.
Loading is included in wall-clock durations. Exact settings, hashes, envelopes,
per-case durations, and metadata are in [the raw run](comparison-8dc8253.jsonl).
Zero-based pairings and reasons are in [the review](review-8dc8253.json).

## Delivered results

| Measure | Baseline | Ollama |
| --- | --- | --- |
| Successful attempts | 10/10 | 10/10 |
| Task TP / FP / FN | 6 / 0 / 2 | 6 / 4 / 2 |
| Task precision | 6/6 = 100% | 6/10 = 60% |
| Task recall | 6/8 = 75% | 6/8 = 75% |
| Owner errors among matched tasks | 0/6 | 1/6 |
| Deadline errors among matched tasks | 2/6 | 1/6 |
| Evidence-support errors among matched tasks | 0/6 | 1/6 |
| Fully correct matched items | 4/8 labels | 3/8 labels |
| Correct empty-label cases | 3/3 | 0/3 |
| Successful-call median duration | 0.000035 s | 1.139 s |
| Successful-call maximum duration | 0.000493 s | 2.585 s |

No failed-call durations exist in this run. Baseline timings are in-process
microsecond measurements dominated by runtime noise; they are not API latency.
Model timings cover the extraction function including HTTP, loading, validation,
and evidence checks, not Uvicorn or browser overhead.

## Per-case review

Task counts below are TP/FP/FN. Each category contains just one case, so aggregate
counts are more meaningful than category percentages.

| Case / category | Baseline | Ollama | Material observation |
| --- | --- | --- | --- |
| 01 explicit commitment | 1/0/0 | 1/0/0 | Both correct. |
| 02 accepted request | 0/0/1 | 1/0/0 | Model found task but evidence omitted the identifying request. |
| 03 refused request | 0/0/0 | 0/1/0 | Model extracted explicitly declined work. |
| 04 unanswered request | 0/0/0 | 0/1/0 | Model treated unanswered request as accepted. |
| 05 suggestion | 0/0/0 | 0/1/0 | Model extracted a tentative suggestion. |
| 06 unknown owner | 0/0/1 | 1/0/0 | Model used string `"null"` instead of JSON `null`. |
| 07 unspecified deadline | 1/0/0 | 1/0/0 | Model deadline was string `"null"`. |
| 08 dependency | 1/0/0 | 0/1/1 | Model omitted dependency from action; rubric forbids matching. |
| 09 relative deadline | 1/0/0 | 1/0/0 | Baseline left tomorrow in task; model deadline correct. |
| 10 mixed discussion | 2/0/0 | 1/0/1 | Baseline missed second deadline; model missed second task. |

The baseline's tasks with `tomorrow` left in their descriptions retain the work
and object, so they are paired by meaning; missing deadline fields are scored
separately. The dependency omission in case 08 changes required scope and fails
task matching under the predefined rule.

## Structural diagnostics and limitations

All 10/10 model responses parsed and passed the existing schema. All 10 generated
items had evidence present as exact nonblank transcript substrings: fabricated
(nonmatching) evidence was 0/10. These numbers did not prevent semantic errors.
The current string-or-null schema permits the literal string `"null"`; it does
not automatically convert it to null. That string appeared in four generated
fields across cases 03, 06, 07, and 08. Only paired task fields enter the field
error denominators above; the remaining errors are visible in the review.

All returned items were `needs_review`. This run contains no model-call failures;
failure behavior is covered by unit tests, not quality measurements here.
Default sampling, a small development set, and Codex adjudication limit the
conclusions. The baseline outperformed this particular model run on task
precision and fully correct items. Do not claim that the model improves overall
quality on the basis of this run. Independent review and broader cases are needed.

Next: review the refused-request error and string-null behavior with the user,
then agree on a focused improvement before changing implementation or prompt.
Preserve this run for comparison; new runs need distinct filenames.
