# ActionGraph local release candidate

Verified candidate for a local engineering portfolio release, November 4, 2026.
Annotated tag v0.1.0-rc.1 points to verified source package 70cf9d4; application
implementation checkpoint is 351b3a0. No stable tag or GitHub Release exists. Public page and recording remain deferred under the user's plan.

## Product contract

A local text API proposes action items using rules v5, retains exact source
quotes and nullable unknown values, and supports caller-directed review. Optional
SQLite sessions preserve original server-generated proposals and latest reviewed
results across restarts. Every extracted item needs review. Experimental local
Ollama is explicitly opt-in; failed inference never silently becomes rules output.

The initial interface is Swagger. This candidate does not add a dashboard, audio,
calendar integration, cloud inference, authentication or cross-meeting memory.
Only synthetic/public inputs are supported by the project data policy.

## Verified checklist

| Check | Evidence |
| --- | --- |
| Current unit/integration suite | 346 tests pass at 351b3a0; Ruff app/tests/evals passes. |
| Current CI | [351b3a0 test job passed](https://github.com/AbhinavS-30/ActionGraph/actions/runs/41888197752/job/126778229790). |
| Reproducible environment | Fresh Python 3.12.13 install previously verified at 252c776; lockfile is byte-identical. Archived 351b3a0 source passes all 346 tests/Ruff using that separate environment; import path checked. pip check passes. macOS arm64 only locally verified. |
| Saved-session integration | Latest code rechecked over real loopback HTTP: create/review, restart with identical saved state, stale changes 409, delete 204 and missing GET 404. Disposable database/processes cleaned up. |
| Browser workflow | User-executed screenshots verify saved-session create, confirmation, conflicts, actual restart persistence, deletion and blank rejection; see SWAGGER_CHECK.md for revision and observation scope. Later error-doc/resource changes have schema/protocol checks, not a new browser recording. |
| Request limits | Latest code rechecked over TCP: fixed and chunked oversized requests 413; normal extraction afterward 200. 413 declared in OpenAPI. |
| Upstream limits | Tests verify 1 MiB generation cap, stream close, compression rejection, bounded eval capture and 502/slot reuse. These are simulated responses, not a new real-model run. |
| Evidence and evaluations | First results, failed experiments, raw attempts, labels and provisional pairings retained. Known-set v5 replay changes only the targeted withdrawal output. |

Lockfile SHA-256:
`ef10afcd03c0657378433aaa1baff51c27d7a34abde555711af482905596a823`.
No new dependency, model download or paid service was introduced.

## Quality disclosure to ship with the candidate

The first fourteen-case frozen-v4 validation had 6 correct tasks, 1 withdrawn-task
false positive and 5 missed labels out of eleven tasks. After targeted v5 tuning,
replay on those now-observed cases has 6 correct, 0 extras and the same 5 misses.
This is not fresh independent validation or general zero-error extraction.
Ownerless work, unsupported verb/clock time, object-list and shared-date forms
remain missed. Broader dialogue, nonadjacent withdrawals and ambiguity remain
limited. The model also underperformed the simple baseline in earlier evaluation.

Evaluation review is provisional Codex review; independent human adjudication is
not complete. A local engineering demo can disclose provisional evaluation, but
must not claim independent validation, production users or broad meeting accuracy.
Reviewing a task through the API is not independent adjudication of the benchmark.
See [first result](../evals/results/REPORT-rules-v4-fresh-486fcb5.md) and
[v5 replay](../evals/results/REPORT-rules-v5-fa37f4e.md).

## Resource and storage scope

Enforced: 12,000 transcript characters; 2 MiB raw HTTP body; 1 MiB identity-only
Ollama generation envelope; generated-token cap; per-network-operation timeout;
one API model call per process; SQLite lock timeout; revision-checked atomic
review/delete; up to 100 review/saved-session proposals.

Not established: hard total wall-clock deadline, API output-byte cap, hostile JSON
complexity protection, multi-process admission, disk quota or automatic retention.
These are disclosed limits of a loopback-only synthetic-data tool, not silently
completed public-hosting controls. SQLite stores originals and latest review,
not full review history; IDs are not authorization. Manual deletion is not secure
erasure from backups or filesystem remnants. See LIMITS.md and STORAGE.md.

## Candidate usage and packaging

Follow README setup, then docs/STORAGE.md for optional persistence. Keep the API
on loopback with one worker. Rules mode needs no Ollama. Use the synthetic flow
in SWAGGER_CHECK.md; it shows successful review plus conflict and deletion paths.
Present a missed example alongside the supported path. Do not hide failures.

A source bundle is prepared from this committed candidate with git archive.
It excludes ignored virtualenv/model/database files by construction; it is a
source export, not a self-contained installer or a hosted service. Record its
commit and SHA-256 separately. No release tag/publication is implied by a bundle.

## Remaining delivery work

1. Review the candidate scope and provisional-quality disclosure; address any
   concrete defect found during review. Independent adjudication remains open.
2. Final local-release walkthrough and review of draft stable v0.1.0 notes.
   The candidate bundle and exact package CI passed; see verification/CANDIDATE-70cf9d4.md.
   A stable release is not implied by the release-candidate tag.
3. After product readiness, create the approved project page and record the
   local demo, then prepare the LinkedIn draft. Do not publish posts automatically.

Do not add public-service controls or expand grammar just to make this checklist
look complete. A broader product claim requires separately agreed engineering
and evaluation work.
