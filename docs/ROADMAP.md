# Delivery roadmap

Updated November 4, 2026. Initial demo target was November 3; it is not evidence
of delivery or production readiness. Current implementation checkpoint: 351b3a0.

| Phase | Current state | Remaining delivery work |
| --- | --- | --- |
| Validation and local API | Implemented; 346 tests, Ruff and current CI pass | Preserve contracts/checks during release fixes. |
| Experimental local model | Implemented and measured; quality failures preserved | Remains opt-in; no broad reliability claim. |
| Rules extraction and evaluation | Rules v5 implemented; first-run and observed-case replay reports recorded | Semantic misses/unsupported forms disclosed; independent adjudication pending. |
| Human review and local persistence | Stateless and saved-session paths implemented; TCP restart and user-assisted Swagger checks pass | Latest-review-only/local-access limitations disclosed. |
| Local resource boundary | Request/upstream generation buffering, token/operation/concurrency/write-lock bounds implemented | Total duration, API output size, disk growth and distributed controls not established; not public hosting. |
| Local release candidate | Scope and verified evidence consolidated in RELEASE_CANDIDATE.md | Finalize versioned notes and source package with exact commit/checks; not yet tagged/released. |
| Public presentation | Approved project page plus recorded local demo; not started | Begin after product readiness; extraction stays local. LinkedIn draft afterward; no automatic posting. |

The candidate is a local engineering portfolio tool with provisional evaluation.
It is not a general accurate meeting extractor or production service. Keep known
failures visible; do not use tuned-case results as fresh validation. See STATUS.md,
RELEASE_CANDIDATE.md, RELEASE.md, RULES.md and LIMITS.md for evidence and scope.

Audio, calendar integration, elaborate dashboards, public inference hosting and
cross-meeting memory remain outside this delivery scope. A broader capability or
reliability claim needs separately agreed work and supporting evaluation.
