# Project status

Updated November 3, 2026.

## Current product

ActionGraph is a local text-transcript API. The default `rules` engine supports a
limited first-person commitment grammar; `ollama` explicitly selects experimental
local `llama3.2:3b` inference. Successful responses identify the engine, scope
limitations, and proposed items requiring review. No automatic fallback occurs.
The repository is public; the extraction service is local. A public project page
and recorded demo are planned but have not been built or published. This is not
claimed as a production-ready general meeting extractor.

## Implemented

- FastAPI health and extraction endpoints with Swagger interactive documentation.
- Explicit input errors, 12,000-character transcript cap, output contracts, and
  JSON parsing. Unknown owner/deadline use genuine null; string-null is rejected.
- Exact transcript-quote validation and verbatim owner/deadline text-presence
  checks in the model path. These do not establish semantic attribution.
- Rules v2 grammar, contractions, supported trailing dates, dependency preservation,
  original-line evidence, and conservative exclusions. Accepted requests,
  ownerless work, compound tasks and broader dialogue interpretation remain limited.
  Explicit same-speaker, matching-task cancellations now remove earlier items.
- Validated local runtime settings, generated-token caps, model error mapping,
  and one active API model extraction per process. Rules requests use no model.
- Synthetic datasets, a preserved simple baseline, collection tooling, raw outputs,
  and provisional Codex semantic reviews. No independent adjudication is claimed.
- CI on pushes/pull requests: pinned official actions, Python 3.12, pytest and Ruff
  including evals. Existing rules checkpoint `dc9e85d` passed GitHub CI.

## Current verification

192 tests pass locally with `.venv/bin/python -m pytest`; Ruff passes with
`.venv/bin/python -m ruff check app tests evals`. Unit/fixture checks are not
extraction-quality measurements. No new dependencies or model downloads were added.

The user verified Swagger rendering and real model 200/blank-input 422 responses
through screenshots on November 2. After the rules pivot, an actual Uvicorn TCP
smoke check returned default `engine=rules`, expected task/owner/deadline/evidence,
a scope notice, and blank-input 422. The updated engine-label browser interaction
has not been reverified; no video recording is complete. See `docs/DEMO.md`.

## Evaluation evidence

- Rules v1 on the two previously observed ten-case sets: 6 TP, 0 FP, 2 FN and
  six fully correct items out of eight labels on each. Both sets were known during
  implementation; these are development results, not held-out accuracy.
  [Report](../evals/results/REPORT-rules-45bdcb3.md).
- First fresh model validation: 5/10 successful calls, task precision 50% (2/4),
  recall 25% (2/8), two fully correct items out of eight. The baseline exceeded the
  model in that run. [Report](../evals/results/REPORT-validation-d21e6b6.md).
- String-null, list-valued, two-stage, and concise-prompt experiments remain
  preserved under `evals/results/`; unsuccessful candidates were not adopted.
  [Evaluation design and artifact guide](../evals/README.md).

A new rules-focused set, `evals/rules-validation-v1.json`, contains twelve cases
and nine labeled tasks, fixed before extraction on that set. It includes known
out-of-scope forms and later cancellation. It was authored with knowledge of the
grammar and prior failure modes, not independently or blindly. The first-run result is now recorded below; labels and implementation were not
changed after inspection. These cases are now observed.

## Remaining limits and next task

Rules v2 replay is recorded with original labels and preserved v1 results.
Next define a bounded accepted-request policy before implementing support,
then address the remaining agreed release gates. The user deferred public page
work and demo recording until the product is ready; neither is in progress.


Real-meeting quality, independent human evaluation, cross-line semantic consistency,
raw HTTP body/response byte limits, total-duration limits and distributed concurrency
are not established. No persistence or human confirmation endpoint exists. Audio,
calendar integration, cross-meeting memory and elaborate dashboards remain deferred.
See `docs/RELEASE.md` and `docs/RULES.md` for release requirements and exact scope.

## First rules-focused validation

Clean source `042cf19`, twelve cases and nine labels: rules completed 12/12
attempts with 4 TP, 1 FP and 5 FN; task precision 4/5 (80%), recall 4/9 (44.4%),
four fully correct items. A later-cancelled promise was the false positive;
accepted requests, ownerless work, unsupported verb/time, and compound tasks
were missed. Baseline: 4/3/5, one fully correct item. All delivered quotes and
fields passed text-presence checks despite cancellation being semantically wrong.
No model calls or execution failures occurred. See
[full report](../evals/results/REPORT-rules-validation-042cf19.md) for category
counts, review decisions and timing limits. This is a small synthetic set authored
with implementation knowledge, not independent human validation or real-meeting
accuracy. 175 tests and Ruff pass.

Rules v2 explicit cancellation handling implemented under the policy in `docs/RULES.md`. Tests cover negative forms, exact speaker identity, task/date/dependency separation, vague/conditional targets, unqualified removal, and later recommitment with original evidence. API returns only surviving items; no model call added. 192 tests and Ruff pass. The [observed-case replay](../evals/results/REPORT-rules-v2-5a696b4.md) changes only the cancelled-task output: rules-focused scores are 4 TP, 0 FP, 5 FN; earlier two sets remain 6/0/2 each. These are regression results, not independent validation.
