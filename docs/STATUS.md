# Project status

Updated November 5, 2026. Implementation checkpoint: `351b3a0`.

## Current product

ActionGraph is a local text-transcript API with rules v5 by default and explicit
experimental local Ollama llama3.2:3b mode. Items contain action, nullable owner,
nullable deadline, exact evidence and needs_review. Schema/text checks do not
prove semantic interpretation or completeness. The repository is public; the
API is local. No production-ready/general-meeting-accuracy claim is supported.

Implemented:

- Health/extraction endpoints, Swagger, strict input/output validation, explicit
  transport/output failures and no automatic model-to-rules fallback.
- Bounded rules for direct promises, dates/dependencies, adjacent accepted
  requests, two-task promises, explicit cancellations and adjacent withdrawals.
  Exact scope and unsupported cases: [RULES.md](RULES.md).
- Stateless confirm/correct/reject review, preserving originals/evidence and
  returning separate reviewed copies: [REVIEW.md](REVIEW.md).
- Opt-in SQLite saved rules sessions, stable proposal IDs, restart persistence,
  atomic complete-batch review, revision conflicts and deletion. Latest review
  only; no authentication, full history, listing or backup: [STORAGE.md](STORAGE.md).
- 2 MiB raw request cap, 1 MiB identity-only generation envelope cap, token and
  per-operation network limits, process-local model slot and SQLite timeout.
  Hard total duration/API-output/disk/distributed limits remain open: [LIMITS.md](LIMITS.md).
- OpenAPI custom error declarations and preserved synthetic evaluation artifacts.

## Verification

346 tests pass with `.venv/bin/python -m pytest`. Ruff passes with
`.venv/bin/python -m ruff check app tests evals`. No new dependency/model download.
[351b3a0 CI test job passed](https://github.com/AbhinavS-30/ActionGraph/actions/runs/41888197752/job/126778229790).

Fresh Python 3.12.13 environment installed from pinned requirements at 252c776;
lockfile unchanged. Archived 351b3a0 source passes all 346 tests/Ruff using that
separate environment, with import path verified; pip check passes. Locally verified
on macOS arm64; CI uses Python 3.12 Linux.

Latest code also passes actual loopback TCP saved-session create/review/restart/
conflict/delete checks and fixed/chunked request-size checks with disposable
servers/databases. User screenshots verify the saved-session Swagger workflow,
including restart persistence and validation errors: [SWAGGER_CHECK.md](SWAGGER_CHECK.md).
Later OpenAPI/resource changes were checked by tests/protocol, not a new browser
recording. Automated browser access remains unavailable. A captioned API replay is now
available; no direct browser screen recording was made.

## Evaluation evidence

All results are small synthetic runs with provisional Codex semantic review;
independent human adjudication is pending. No real-meeting accuracy established.

| Evidence | Result and interpretation |
| --- | --- |
| [First model validation](../evals/results/REPORT-validation-d21e6b6.md) | 5/10 successful calls, 2 TP / 2 FP / 6 FN; baseline exceeded model. |
| [First frozen-v4 validation](../evals/results/REPORT-rules-v4-fresh-486fcb5.md) | 14 cases / 11 labels: 6 TP / 1 FP / 5 FN, six fully correct items. Withdrawn promise was a false positive. Labels fixed before extraction, author knew implementation. |
| [Observed-case v5 replay](../evals/results/REPORT-rules-v5-fa37f4e.md) | Only targeted withdrawal output changed: 6 TP / 0 FP / 5 FN on that now-observed set. Other sets remain 7/0/1, 7/0/1, 7/0/2. Not independent improvement evidence. |

Misses include ownerless work, unsupported verb/time, object lists and shared
final dates. Broader dialogue/withdrawal forms remain limited. Old raw outputs,
labels, decisions and rejected prompt experiments remain in evals/results.
Historical progress checkpoints are retained in Git and linked reports, rather
than treated as current open tasks.

## Release candidate and next task

[RELEASE_CANDIDATE.md](RELEASE_CANDIDATE.md) consolidates the proposed local
portfolio scope, verified gates and remaining limitations. Release-candidate tag v0.1.0-rc.1 points to verified package commit 70cf9d4.
No stable release tag or GitHub Release exists. The November 3 initial demo target has passed; no new
completion date is asserted. The project is not declared fully finished.

Draft v0.1.0 notes are prepared in RELEASE_NOTES.md. A source-only candidate
bundle is prepared from this documentation checkpoint, keeping quality review
explicitly provisional. Candidate ZIP exactly matches that Git source; extracted-package tests/Ruff/pip
check and exact candidate CI pass. See verification/CANDIDATE-70cf9d4.md. Next
perform the final local-release walkthrough and assess stable release readiness.
Independent human adjudication remains open; no independent-validation claim may
be made. Public page remains open. A captioned API replay and LinkedIn draft are now
prepared; no post has been published. Audio,
calendar integration, elaborate dashboards and cross-meeting memory stay deferred.

## Final walkthrough rehearsal

A mixed synthetic example ran through real HTTP session create, correction/
confirmation/rejection, stale update, restart persistence and deletion. The full
result survived restart; disposable resources were removed. It also exposed an
unsupported withdrawal requiring human rejection and ownerless work that the
current review API cannot add. This is illustrative, not a new quality benchmark.
[Engineering explanation](WALKTHROUGH.md) and [observations](verification/WALKTHROUGH-rc1.json).
Application code unchanged; candidate tag remains fixed. Next stable-release
readiness decision within disclosed scope, then presentation after readiness.

## Portfolio README and recording preparation — November 5

README rewritten with product overview, CI badge, extraction flowchart, saved
session sequence diagram, reproducible setup, API/error reference, measured
results and explicit limitations. RECORDING.md supplies a 2–3 minute storyboard
with actual request bodies and a known omission to show. No video, page or
LinkedIn post created/published. App behavior and fixed rc.1 tag unchanged.
Next record and review the local demo, then prepare the LinkedIn draft.

## Captioned demo and sharing package — November 5

Created a 123-second, 1280×720 H.264 silent captioned API replay using real
loopback HTTP calls and disposable SQLite storage. Captured creation, accepted
request extraction, confirmation, stale revision rejection, identical retrieval
after restart, blank-input rejection, a known ownerless omission and deletion.
No model was called. This is rendered response footage, not a browser capture.
Video decoded successfully at five sample timestamps; representative frames were
visually inspected. See [media provenance](media/README.md),
[narration](DEMO_NARRATION.md) and [LinkedIn draft](LINKEDIN_DRAFT.md).

Application behavior and rc.1 tag unchanged. Required pytest and Ruff checks pass
(346 tests). No LinkedIn post or separate public project page exists. Browser
control is unavailable, so uploading/posting requires the user's browser. Next:
user review of the video and draft, then upload the MP4 and publish the post.
Independent adjudication and stable-release readiness remain open.
