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

89 test cases passed using `.venv/bin/python -m pytest`. Ruff lint passed using `.venv/bin/python -m ruff check app tests`. These checks do not measure extraction quality.

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

Run and review the isolated refusal-prompt experiment, then agree on the next
quality or application-hardening change. Public deployment mode remains undecided;
release requirements are listed in `docs/RELEASE.md`.

A manual structured-output smoke check combined the prompt builder, client, and parser on the synthetic sentence “Maya: I will send the report tomorrow.” The result contained one item with owner Maya, deadline “tomorrow”, exact sentence evidence, and `needs_review`. This is one smoke example, not extraction-quality evaluation or an integrated service.

Dataset integrity check: ten unique case IDs, eight labeled items validated against `ExtractionResult`, all labeled evidence present exactly, and all labeled items marked `needs_review`. These checks validate fixture integrity, not model quality.

Collector checks: baseline-only CLI smoke produced metadata plus ten successful attempt records in `/tmp`; no semantic scores calculated. Ruff also passed on `evals`. The first full comparison is now retained under `evals/results/`.

First comparison: clean source `8dc8253`, ten successful attempts per system. Provisional Codex review: baseline task TP/FP/FN = 6/0/2; Ollama = 6/4/2. Fully correct matched items: baseline 4/8 labels, model 3/8. Model median/max extraction durations: 1.139/2.585 seconds, including loading. All model responses passed schema and quote-presence checks despite semantic errors. See `evals/results/REPORT-8dc8253.md` for per-case decisions, denominators, runtime, raw outputs, and limitations. Human adjudication is pending.

Added an explicit refusal instruction and a synthetic refusal example to the
prompt. Unit checks remain 89 passing tests and passing Ruff; model behavior after
this change is not yet measured. This is development-set prompt tuning, not an
independent validation. No model settings, schema, labels, or parser behavior were
changed for this experiment.
