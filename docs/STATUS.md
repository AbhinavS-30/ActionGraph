# Project status

Updated November 4, 2026.

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
- Rules v4 grammar, contractions, supported trailing dates, dependency preservation,
  original-source evidence, and conservative exclusions. Requests outside the adjacent acceptance policy,
  ownerless work, unsupported compounds and broader dialogue interpretation remain limited.
  Explicit same-speaker, matching-task cancellations now remove earlier items.
- Validated local runtime settings, generated-token caps, model error mapping,
  and one active API model extraction per process. Rules requests use no model.
- Synthetic datasets, a preserved simple baseline, collection tooling, raw outputs,
  and provisional Codex semantic reviews. No independent adjudication is claimed.
- CI on pushes/pull requests: pinned official actions, Python 3.12, pytest and Ruff
  including evals. Existing rules checkpoint `dc9e85d` passed GitHub CI.

## Latest implementation

Rules v4 adds exactly two independently parseable direct-promise clauses joined
by and. Both retain the full source line and speaker, in clause order. Unsupported
halves reject the whole pair. Ambiguous final-only dates, dependencies, three-task
lists, compound requests and compound negations are excluded. Explicit per-clause
dates remain local; a later single cancellation removes only its matching item.
233 tests and Ruff pass; no dependencies or model calls added. The v4 replay is recorded below; prior reports remain historical.

## Previous implementation

Rules v3 supports adjacent named can/could-you requests followed by the addressed
speaker's explicit Yes + first-person promise + matching verb + it/them. Both
original lines form the evidence. Dates and dependencies use the existing parser.
Bare yes, mismatching speakers/verbs, intervening lines and conditional replies
are excluded. Cancellation still applies. API coverage verifies no model call.
No dependencies added. The v3 replay is recorded below; earlier results remain historical.

## Current verification

303 tests pass locally with `.venv/bin/python -m pytest`; Ruff passes with
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

Rules v3 replay is recorded with original labels and preserved earlier results.
First frozen-v4 validation and the release audit are recorded. Blank output-field validation is complete. The stateless extract-to-review TCP verification and storage policy are complete.
Opt-in saved rules sessions are now implemented under docs/STORAGE.md.
Next verify current saved-session browser interaction and finish release checks,
then address the remaining agreed release gates. The user deferred public page
work and demo recording until the product is ready; neither is in progress.


Real-meeting quality, independent human evaluation, cross-line semantic consistency,
raw HTTP body/response byte limits, total-duration limits and distributed concurrency
are not established. Optional saved rules sessions and stateless caller-directed confirmation are available. Audio,
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

## Rules v3 observed-case replay

Clean source `c9e5e64`: one additional correctly accepted request per dataset;
all other outputs unchanged. Development and observed validation each score
7 TP, 0 FP, 1 FN (seven fully correct of eight labels); rules-focused scores
5 TP, 0 FP, 4 FN (five fully correct of nine). All 32 rules attempts succeeded
without model calls. Original labels and baseline remain unchanged. These are
known-case regression results, not independent quality estimates.
[Report and audit artifacts](../evals/results/REPORT-rules-v3-c9e5e64.md).

## Rules v4 observed-case replay

Clean source `aa3c999`: rules-check-11 now returns both compound tasks exactly
as labeled; all other rules and baseline outputs remain unchanged. Development
and observed validation each remain 7 TP, 0 FP, 1 FN; rules-focused improves
to 7 TP, 0 FP, 2 FN. All paired rule items are fully correct under provisional
review. All 32 rules attempts succeeded without model calls. These are known-case
regression results, not independent validation. Ownerless work and unsupported
verb/time remain missed. [Report and artifacts](../evals/results/REPORT-rules-v4-aa3c999.md).

## Frozen v4 validation plan

Fourteen new synthetic cases with eleven labeled tasks are fixed before the
first extraction run. Source app/rules.py remains unchanged. Cases include
supported commitments, acceptance, compound dates and cancellation, plus genuine
out-of-scope work and broader withdrawal wording. Author knows the grammar and
prior failures; this is not independent or blind evaluation. Preserve all first
outputs and labels, score all cases under the existing rubric, and do not tune
the extractor during this run. Collection choice: rules-v4-validation.

## First frozen-v4 validation result

Clean source `486fcb5`, unchanged rules v4, fourteen new cases and eleven labels:
rules 6 TP, 1 FP, 5 FN, precision 6/7 (85.7%), recall 6/11 (54.5%), six fully
correct items; baseline 5/6/6, two fully correct. All 14 attempts per engine
succeeded without model calls. Paraphrased withdrawal remained a false positive;
ownerless work, clock/verb, object list and two shared-date tasks were missed.
Labels were committed before extraction and not changed afterward. Author knew
the grammar; review is provisional, not independent or real-meeting validation.
The set is now observed. 234 tests and Ruff pass.
[Full report and audit artifacts](../evals/results/REPORT-rules-v4-fresh-486fcb5.md).

## Release audit — November 4

See [readiness audit and ordered work](RELEASE.md). Current verdict: not finished.
234 tests, Ruff and pip check pass. A fresh isolated Uvicorn TCP check verifies
health/docs/OpenAPI, rules acceptance/compound/cancellation, and blank/oversized/
unknown-engine 422. This is not rendered-browser verification. Latest queried CI
runs through 6088aa2 are queued; no current CI pass is claimed. Clean-install
verification, current browser interaction, human adjudication, review workflow,
blank output-field validation and release packaging remain. No page/video built.

## Nonblank output fields completed

ActionItem now rejects blank action/evidence and blank non-null owner/deadline
strings, preserving valid text and genuine nulls. Schema/parser/API tests cover
Unicode whitespace and whole-result failure; blank model output returns 502
without partial results. Earlier evidence/provenance tests now expect schema
failure first for blank fields. 259 tests and Ruff pass. No dependencies added;
no extraction-quality measurement changed. Next define local review/correction/
confirmation policy before implementing storage or endpoints.

## Stateless review implemented

POST /review supports confirming, correcting or rejecting a complete submitted
batch (up to 100 proposals), preserving original snapshots and exact evidence.
Corrections must pass the output contract and field-text checks; no evidence
edits. Rejections retain the original with reviewed=null. Server sets confirmed
only on reviewed copies. Invalid/incomplete batches return 422 without partial
records; no model, storage, identity or authenticated provenance is involved.
284 tests and Ruff pass. [Contract and example](REVIEW.md). Next verify the
extract-to-review workflow over real TCP, then define persistence/retention and
review identity/version requirements before adding storage. Quality findings
remain unchanged; this workflow does not repair extraction automatically.

## Review TCP verification and storage policy

Clean source 5acb10e passed actual loopback HTTP extract-to-review checks: confirm,
correction, rejection, original preservation/order, no partial invalid batches,
unchanged repeated extraction and OpenAPI presence. See DEMO.md and its recorded
observations. Browser verification remains separate and pending.

[Storage policy](STORAGE.md) now defines optional local sqlite3 sessions, immutable
server-generated rules proposals, revisions/conflicts, atomic reviews/deletion,
explicit retention and no authenticated reviewer/history guarantees. This is a
design only: no database, persistence setting or saved-session route implemented.
Next implement and test saved-session storage under that policy. Public page and
recording remain deferred; 284 tests and Ruff pass.

## Saved local sessions implemented

ACTIONGRAPH_DB_PATH opts into sqlite3 storage; unset means disabled and no database
creation. New session routes create server-generated rules snapshots and stable
proposal UUIDs, retrieve saved state, save complete reviewed batches and delete
with expected_revision checks. Transactions prevent partial writes; stale changes
return 409, lock contention 503, missing IDs 404, invalid reviews 422, other storage
errors sanitized 500. Source proposals/evidence stay unchanged. Latest review
only; no authentication, list/search, TTL, backup or full history. Stateless routes
remain unchanged. Database and sidecar patterns ignored in Git; no deps added.

303 tests and Ruff pass. Real loopback TCP smoke across two Uvicorn processes
verified saved review after restart, conflicts and deletion using a disposable
database. These observations used the implementation working tree based on
52788a8, not an earlier committed source. No persistent user database was created.
See STORAGE.md. Next browser verification and release-check reconciliation;
semantic extraction failures remain unchanged. Public page/video still deferred.

## Release verification checkpoint for 252c776

Clean committed-source export and fresh Python 3.12.13 environment installed from
requirements.lock.txt: 303 tests, Ruff and pip check pass. Current storage commit
CI job is queued (exact check-runs API), not passed. Earlier 5acb10e CI passed.
Browser host unavailable; native Safari access timed out, so current rendered
Swagger interaction remains unverified. [Evidence](verification/RELEASE-252c776.md)
and [isolated manual browser procedure](SWAGGER_CHECK.md). No user database
modified; no page/video created. Next complete browser/CI verification and
resolve local resource/semantic release scope.

## Current CI follow-up

Storage source 252c776 GitHub test check now completed successfully (run
41880913838, job 126752847840). Earlier queued entries are historical. Browser
automation remains unavailable and native Chrome reports noWindowsAvailable.
An isolated disposable server on port 8001 is ready for user-assisted Swagger
checks; health/docs/OpenAPI 200 is confirmed, visual execution still pending.
