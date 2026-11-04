# Release readiness

The current application is a local text extraction prototype with tested API
failure handling and an initial synthetic evaluation. It is not a production
service. The November 3, 2026 target is an initial demonstration, not a guaranteed
production deployment date.

## Local demonstration release

- Review provisional semantic scores and record any adjudication changes.
- Investigate refusals, unanswered requests, suggestions, missing dependencies,
  missing items, string-null fields, and incomplete evidence support observed in
  the first run. Preserve unsuccessful experiments as well as improvements.
- Evaluate agreed changes with repeated development runs and new untouched cases;
  report counts, failures, and timing limitations without generalizing tiny samples.
- Finish bounded input/output validation, explicit runtime configuration, and
  tests for resource limits appropriate to the local demo.
- Run automated checks in CI, verify installation from pinned dependencies, and
  verify the actual Uvicorn and interactive API workflow.
- Prepare a versioned release with setup instructions, a synthetic demonstration,
  reproducible evaluation artifacts, architecture, and disclosed limitations.

## Approved presentation scope

The user selected a public project page plus a recorded local demonstration.
Extraction stays local. The presentation should show a clear transcript-to-action
story, traceable evidence, architecture, measured results, and disclosed limitations.
The project page and recording are not built or published yet. A live extraction service needs an
approved host for both FastAPI and model compute; a hosted API cannot reach a
developer's `127.0.0.1`. Hosting, hardware, operating cost, and availability have
not been selected or validated.

Before exposing live inference, define the intended users and synthetic/public
data boundary, access control, TLS, request size limits, concurrency limits,
overload behavior, generation limits, readiness checks, privacy-conscious
operational logging, deployment configuration, monitoring, and rollback. Test
those controls and the deployed end-to-end path. No claim of production readiness
or public service availability should precede those checks.

## Public communication

An engineering portfolio release should state what was built, how it was tested,
what was measured, where it fails, and how to reproduce it. Distinguish a project
page, recorded local demo, and live inference deployment. Do not claim users,
production operation, broad accuracy, or speedups without evidence. A LinkedIn
draft may be prepared after the release artifacts are verified; publishing
requires the user's explicit instruction.

## Readiness audit — November 4, 2026

Audited source `6088aa2`. Verdict: continue implementation; local portfolio
release is not complete. Public page and recording remain deferred. A small
scoped demonstration is technically possible, but is not evidence of completion
or general meeting quality. The original November 3 demo target has passed;
no replacement delivery date is asserted by this audit.

| Gate | Evidence and current state | Remaining work |
| --- | --- | --- |
| Local API and failures | Implemented; 234 tests, Ruff app/tests/evals and pip check pass | Keep checks passing for subsequent changes. |
| Current TCP behavior | Fresh isolated Uvicorn on loopback: health/docs/OpenAPI 200; accepted request 1 item, compound 2, cancellation 0; blank/overlong/unknown engine 422 | Recheck browser Try it out with the current response fields before recording. TCP markup does not prove rendered interaction. |
| Source evidence and contract | Exact quotes, nullable fields, text-presence checks and needs_review enforced in extraction | Action/evidence whitespace-only schema values are still possible; close this validation gap. Review transport/output limits for local scope. |
| Semantic quality | First frozen-v4 run: 6 TP, 1 FP, 5 FN on eleven labels; full artifacts preserved | Withdrawal outside grammar remains wrong. Explicitly settle acceptable product scope; do not present this as general accurate meeting extraction. |
| Human review | Items marked needs_review; no correction, confirmation, or persistence interface | Define and implement a bounded local review workflow if releasing the intended reviewable product. Schema allowing confirmed is not a workflow. |
| Evaluation adjudication | Labels frozen before first runs; provisional Codex pairings disclosed | Independent human review remains pending. It cannot be replaced by more schema tests. |
| CI | Latest queried runs for aa3c999, 12cc5ec and 6088aa2 are queued | Obtain completed successful CI for release source. Queued is neither success nor failure; cause not diagnosed. |
| Installation | Pinned dependencies and CI install step exist; current venv pip check passes | Verify a clean install on Python 3.12; current environment health does not prove reproducible installation. |
| Release packaging | Setup, architecture, scope and evaluation docs exist | Reconcile stale README phase/concurrency/example descriptions, create versioned release notes, verify synthetic demo sequence. No tag/release created. |
| Presentation | Public repository exists; approved public page and local video planned | After product gates, build page and record current workflow, then prepare LinkedIn draft. Do not publish automatically. |

CI observations: [6088aa2 run](https://github.com/AbhinavS-30/ActionGraph/actions/runs/41878439233),
[12cc5ec run](https://github.com/AbhinavS-30/ActionGraph/actions/runs/41877959140),
[aa3c999 run](https://github.com/AbhinavS-30/ActionGraph/actions/runs/41877641473).
These are snapshots of queued state, not claims about their later outcome.

### Recommended implementation order

1. Close blank output-field validation with focused parser/API failure tests.
2. Define a local human-review contract: how proposed values are edited, rejected
   or confirmed, and what is stored. Preserve original evidence and distinguish
   human edits from extraction. Implement only after that policy is settled.
3. Address withdrawal behavior under an explicit bounded policy, and decide
   whether missing forms stay disclosed limitations. Preserve original scores;
   any tuning now uses observed cases.
4. Complete clean-install, current browser, CI, resource-limit and documentation
   verification; reconcile audit status and assemble a versioned local release.
5. Build the approved project page and record the demo after product readiness.

No new dependency, service, model download, public endpoint, website or recording
was introduced by this audit. Production hosting controls in this document remain
future requirements, not additional blockers for a loopback-only portfolio demo.

### Audit follow-up: nonblank fields complete

November 4: the blank output-field gap is closed. Action/evidence and non-null
owner/deadline must contain non-whitespace text; valid strings stay unchanged.
Parser and model API fail the whole result for invalid fields (502 for model
output). 259 tests and Ruff pass. The table above is the preserved audit snapshot;
its blank-field work item is now complete. Resource limits, review workflow and
other release requirements remain open. Next define review policy.

### Audit follow-up: stateless review available

POST /review now implements caller-directed confirmation/correction/rejection
with original snapshots and unchanged evidence. 284 tests and Ruff pass. It
does not implement saved reviews, authenticated identity or extraction provenance,
a custom UI, conflict handling or task additions. Next verify the current
extract-to-review TCP flow and define storage semantics before persistence.

### Audit follow-up: saved rules sessions implemented

Opt-in SQLite storage now preserves server-generated original proposals and latest
review across restarts, with atomic revision checks and deletion. 303 tests and
Ruff pass; a disposable actual TCP restart smoke passes. No authenticated reviewer,
full review history, listing or backup. See STORAGE.md for configured path,
retention and limitations. Current browser interaction and other release gates
remain open. No extraction-quality score changed through storage implementation.

### Audit follow-up: clean install verified; browser/CI pending

Source 252c776 passed 303 tests, Ruff and pip check from a committed-source export
and fresh Python 3.12.13 environment. Storage commit CI is queued, not successful
yet. Browser automation unavailable; no current rendered workflow claimed.
See [verification checkpoint](verification/RELEASE-252c776.md) and the
[disposable Swagger procedure](SWAGGER_CHECK.md). These remaining checks do not
require more feature scope. Resource/semantic policy and independent review
remain separate release requirements.

### Audit follow-up: user-assisted browser workflow passed

November 4 screenshots verify the saved-session Swagger sequence, including
confirmation preservation, stale writes/deletes, actual restart persistence,
deletion and blank rejection. See SWAGGER_CHECK.md for precise observation scope.
Storage source CI and clean installation passed. Port-8001 test server stopped.
Custom error declarations in Swagger, local resource policy, semantic scope and
independent adjudication remain separate work before release packaging; no
public page or video created.

### Audit follow-up: custom OpenAPI responses documented

The existing saved-session and experimental model errors are now declared with
JSON models in OpenAPI, including 404/409 and saved-review 422 string/list shapes.
305 tests and Ruff pass. No runtime/status behavior changed, and the updated
Swagger rendering has not been visually rechecked. Next quality work is a bounded
withdrawal policy addressing the recorded false positive; original metrics remain
preserved. Local resource policy and independent review remain open.
