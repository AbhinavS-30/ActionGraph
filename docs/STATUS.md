# Project status

Updated October 31, 2026.

## Implemented

- FastAPI health endpoint reporting the extraction function and API as available, without probing model readiness.
- Pydantic action-item and extraction-result contracts.
- Transcript validation with explicit type and blank-input failures.
- JSON parsing followed by output schema validation.
- Exact evidence substring checking, including blank-evidence rejection.
- Standalone Ollama text client using existing HTTPX: nonstreaming requests, prompt checks, response-envelope checks, and propagated connection, timeout, and HTTP status errors. The caller supplies the client base URL and timeout.
- Optional JSON schema forwarding through Ollama’s `format` field; parser-boundary tests preserve malformed-JSON and schema-error behavior.
- Extraction policy and standalone prompt builder covering accepted commitments, unknown values, relative deadlines, exact evidence, and review status.

`extract_actions` connects input validation, prompt construction, schema-constrained generation, parsing, and exact evidence checks. Any unsupported evidence fails the entire call; generated items always return as `needs_review`. `POST /extract` exposes the flow with strict request fields, blank-input rejection, and actionable 422/502/503/504 responses.

- Ten labeled synthetic development cases and an evaluation rubric in `evals/`; first comparison collected and provisionally reviewed by Codex (human adjudication pending).
- Evaluation collector and narrow deterministic first-person baseline; saves per-case status, durations, raw model envelopes, and source/runtime metadata.

## Verification

122 test cases passed using `.venv/bin/python -m pytest`. Ruff lint passed using `.venv/bin/python -m ruff check app tests`. These checks do not measure extraction quality.

A live smoke check invoked `POST /extract` through HTTPX's in-process ASGI
transport with real local Ollama generation. The synthetic sentence “Maya: I will
send the report tomorrow.” returned HTTP 200 with one item, owner Maya, deadline
“tomorrow”, exact sentence evidence, and `needs_review`. This verified the route
through model, parser, and evidence checks; Uvicorn/browser interaction and broader
extraction quality were not evaluated by this check.

Read-only connectivity checks on October 30 confirmed that GitHub remote `main`
matches local commit `4e40ba6` at `https://github.com/AbhinavS-30/ActionGraph.git`.
The local Ollama service responded at `http://127.0.0.1:11434`, and its model
inventory includes `llama3.2:3b`. A live smoke request through the new client
returned `ready` for a prompt requesting that word. A small development-set comparison is now available; broader extraction quality remains unknown.

## Documentation

README now describes the architecture, contract, setup, terminology, design rationale, delivery phases, and limitations. Supporting documents describe the technical roadmap and validation design. Personal learning history is maintained outside project documentation.

## Remaining work

Human review of provisional evaluation decisions, an agreed response to observed semantic errors, and reproducible demonstration. Real-meeting quality remains unknown.

## Next task

Re-evaluate the stricter contract and bounded generation with explicit failure
counts; verify Uvicorn/browser behavior before release verification. Add untouched
cases before making broader quality claims. The approved presentation scope is a
public project page plus recorded local demo; extraction remains local. See
`docs/RELEASE.md`.

A manual structured-output smoke check combined the prompt builder, client, and parser on the synthetic sentence “Maya: I will send the report tomorrow.” The result contained one item with owner Maya, deadline “tomorrow”, exact sentence evidence, and `needs_review`. This is one smoke example, not extraction-quality evaluation or an integrated service.

Dataset integrity check: ten unique case IDs, eight labeled items validated against `ExtractionResult`, all labeled evidence present exactly, and all labeled items marked `needs_review`. These checks validate fixture integrity, not model quality.

Collector checks: baseline-only CLI smoke produced metadata plus ten successful attempt records in `/tmp`; no semantic scores calculated. Ruff also passed on `evals`. The first full comparison is now retained under `evals/results/`.

First comparison: clean source `8dc8253`, ten successful attempts per system. Provisional Codex review: baseline task TP/FP/FN = 6/0/2; Ollama = 6/4/2. Fully correct matched items: baseline 4/8 labels, model 3/8. Model median/max extraction durations: 1.139/2.585 seconds, including loading. All model responses passed schema and quote-presence checks despite semantic errors. See `evals/results/REPORT-8dc8253.md` for per-case decisions, denominators, runtime, raw outputs, and limitations. Human adjudication is pending.

Added an explicit refusal instruction and a synthetic refusal example to the
prompt. Unit checks remain 89 passing tests and passing Ruff. This is development-set prompt tuning, not an
independent validation. No model settings, schema, labels, or parser behavior were
changed for this experiment.

Refusal-example rerun from clean source `99f2cf6`: all ten model attempts
completed, but the refused request was still extracted. Provisional task TP/FP/FN
= 6/3/2 (precision 66.7%, recall 75%); fully correct matched items 4/8 labels.
Model median/max duration 1.022/2.098 seconds. An unrelated meeting-end time was
incorrectly used as a task deadline. No causal improvement claim is justified by
one stochastic rerun. Original artifacts remain unchanged; see
`evals/results/REPORT-99f2cf6.md`. This application is not production ready or
publicly hosted.

Unknown-value hardening: owner/deadline string-null placeholders are rejected with `ValidationError`, including case and surrounding-whitespace variants. Genuine JSON null and other strings are preserved. API regression tests verify HTTP 502 with no returned items. Current checks: 98 tests and Ruff pass. No new live quality results are claimed for this contract change.

Local runtime hardening: validated cached exported settings for loopback URL, model, per-operation timeout (0–120 seconds, exclusive of zero), and generation tokens (1–4096, default 1024). Invalid settings fail startup; local clients ignore proxy environment variables. Input is capped at 12,000 original characters with API 422; generation stopped for length fails with API 502. These are not raw body-size, total-duration, concurrency, or upstream response-byte limits. Collector now records effective settings. Baseline-only CLI smoke passed; 120 tests and Ruff pass. No new model quality measurements claimed.

Concurrency hardening: one active API extraction per process; overlapping valid requests receive 503 with `Retry-After: 1` without invoking the model. A `finally` block releases the slot on success or failure. Tests verify real request overlap, responsive health, reuse after success, and reuse after timeout. Use one Uvicorn worker; standalone calls and other processes are outside this guard. Current checks: 122 tests, Ruff, and diff checks pass. No new extraction-quality claim.

Continuous integration: `.github/workflows/tests.yml` runs Python 3.12 pytest and
Ruff on pushes/pull requests, including `evals/`, with a ten-minute job timeout.
GitHub runs for `ae8de66`, `d555b6f`, and `bc49c70` passed, including clean Ubuntu
installation from the lockfile. Local verification remains 122 passing tests and
passing Ruff. CI runs no model downloads or inference. The `bc49c70` run reported
deprecated action runtimes; checkout and setup-python were updated to official
releases v7.0.1/v7.1.0, pinned to immutable commit hashes. Verification of that
action-version update is pending.
