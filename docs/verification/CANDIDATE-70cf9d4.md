# Verified candidate v0.1.0-rc.1 — November 4, 2026

Annotated tag v0.1.0-rc.1 points to source 70cf9d4. It is a local portfolio
release candidate, not a stable release, production certification, GitHub Release,
public inference service, website or recording.

## Bundle integrity and source identity

Source bundle: ActionGraph-70cf9d4-source.zip (245,456 bytes).
SHA-256: `6c9b022fc1b6348daae8f5afd13ca2b7b3b0980632a36e4b9ef1033afde4070a`.

Verification compared the existing ZIP byte-for-byte with a fresh git archive of
70cf9d4, not only with its adjacent checksum file. ZIP CRC check passed. Entries
have the expected ActionGraph/ root without traversal; no .git/.venv, .env or
SQLite database patterns were included. This is not a general secret-scanner claim.
The source archive has no Git metadata; use the repository for evaluation commands
that collect git revision metadata.

## Executed checks on the extracted package

Extracted to /tmp/actiongraph-package-check-70cf9d4/ActionGraph. Commands ran from
that directory using the separate pinned Python 3.12 environment previously
installed and verified, not the repository's venv:

- pytest: 346 passed.
- Ruff app/tests/evals: passed.
- pip check: no broken requirements.
- [Exact candidate CI test](https://github.com/AbhinavS-30/ActionGraph/actions/runs/41888776318/job/126780246799): completed successfully.

The application implementation is unchanged from 351b3a0; source/package revision
70cf9d4 adds candidate documentation. Prior integrated TCP and user-assisted
browser verification retain their recorded scope. No new real-model evaluation,
independent adjudication or browser recording occurred during bundle verification.

## Version and handoff

Annotated tag pushed: v0.1.0-rc.1. Its message records source, checksum and scoped
quality claims. No stable v0.1.0 tag or GitHub Release was created. Documentation
follow-ups may be later commits; the tag remains fixed to the verified package.

Next: final local-release walkthrough using the existing synthetic workflow,
review the five known misses and the provisional quality disclosure, then decide
stable release readiness. Independent adjudication is still pending. Do not
promise general meeting accuracy or convert known-set replay into fresh evidence.
The approved page and recorded demo remain deferred until product readiness.
