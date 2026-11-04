# Release verification checkpoint — November 4, 2026

Source `252c776`. This is a local verification checkpoint, not a release tag or
production-readiness claim. No extraction-quality dataset was rerun or relabeled.

## Clean installation — passed

Created a separate Python 3.12.13 virtual environment at
/tmp/actiongraph-release-252c776-venv. Installed requirements.lock.txt with pip,
without reusing the project venv or adding dependencies. Exported committed
source with git archive to /tmp/actiongraph-release-252c776-src. From that source
directory, using the fresh interpreter:

- pytest: 303 passed.
- Ruff app/tests/evals: passed.
- pip check: no broken requirements.
- app.main import resolves to the archived source, not the working repository.

This checks macOS arm64 and the pinned dependencies; it does not establish
installation on every platform. Temporary environments are verification artifacts,
not project files or a new runtime configuration. The user's existing venv and
saved databases were not modified.

## GitHub CI — pending

Exact commit check-runs API reports test=queued, conclusion=null:
[storage commit job](https://github.com/AbhinavS-30/ActionGraph/actions/runs/41880913838/job/126752847840).
Workflow ActionGraph checks is active. Earlier review commit 5acb10e completed
successfully: [run](https://github.com/AbhinavS-30/ActionGraph/actions/runs/41879602968).
Do not substitute that earlier pass for storage-commit success. The filtered run
list returned no result while the check-runs endpoint supplied the queued job;
these observations do not diagnose scheduling or runner availability.

## Browser — blocked by automation availability

Computer-use inventory reports browser access host unavailable. Native Safari
selection then timed out. No page interaction or rendered Swagger verification
was completed. Prior HTTP/TCP checks are still valid at their recorded revisions,
but do not establish visual rendering. The saved-session workflow needs the
manual sequence in ../SWAGGER_CHECK.md or restored browser automation.

## Remaining release gates

Complete current rendered Swagger workflow and current CI. Reconcile local
resource-limit policy, known semantic false positives/misses and independent
human review before versioned release messaging. Page/video remain deferred.
Clean install and TCP persistence do not close these separate gates.

## CI follow-up — passed

On recheck, the exact 252c776 test check is completed with conclusion=success:
https://github.com/AbhinavS-30/ActionGraph/actions/runs/41880913838/job/126752847840
The queued observation above is historical. Current browser automation remains
unavailable; native Chrome additionally reports noWindowsAvailable. A disposable
loopback server was started on port 8001 for user-assisted Swagger verification.
Health/docs/OpenAPI return 200; that does not establish rendered interaction.
