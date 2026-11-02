# Project status

Updated November 2, 2026.

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

147 test cases passed using `.venv/bin/python -m pytest`. Ruff lint passed using `.venv/bin/python -m ruff check app tests`. These checks do not measure extraction quality.

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

Complete the manual browser check in `docs/DEMO.md`, then add untouched evaluation
cases and measure field-provenance enforcement with explicit rejection rates.
Experimental list/two-stage paths remain outside the API.
Add untouched
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
releases v7.0.1/v7.1.0, pinned to immutable commit hashes. GitHub run
41241775468 passed for source `b7bf4c4`, verifying that action-version update.

Strict-contract evaluation on November 1 from clean `b7bf4c4`: ten model attempts, four successful and six ValidationError failures for string-null fields. Provisional delivered task TP/FP/FN = 5/0/3; precision 5/5 (100%) must be read with 4/10 call success and 5/8 (62.5%) recall. Five fully correct matched items; no correct empty-label cases. Model successful-call median/max 1.481/2.995 seconds; failed-call times are reported separately. No token-limit stop occurred. Raw refusal/suggestion errors remain in rejected responses. See `evals/results/REPORT-b7bf4c4.md`; human adjudication and untouched evaluation remain pending. No prompt or application behavior was changed during this measurement.

Repository visibility was changed to public at the user’s request on November 1. The extraction service remains local; no hosted inference or project page has been deployed.

JSON-null prompt experiment: explicitly distinguishes unquoted JSON null from
the invalid string placeholder and adds one synthetic accepted-work example with
unknown owner and deadline. Validator, schema, dataset, and generation settings
were unchanged for the experiment; results are now recorded below.

JSON-null candidate `fcc91ec` is not adopted: 6/10 calls completed (three string-null validation failures and one evidence rejection), but delivered task TP/FP/FN fell to 3/3/5; precision 50%, recall 37.5%, fully correct 3/8 labels. One raw result copied a prompt example into an unrelated transcript and was rejected. The previous prompt is restored; no schema or validator weakening. See `evals/results/REPORT-fcc91ec.md` and immutable raw run/review artifacts. This remains one stochastic development comparison, not independent validation.

List-contract experiment implemented only under `evals/`: model owner/deadline use required zero-or-one-string lists, deterministically mapped to public strings/null and checked by existing validation and evidence helpers. The production endpoint is unchanged. Tests cover conversion, invalid/multiple values, string-null rejection, and evidence enforcement. 128 tests and Ruff pass; the live experiment is recorded below.

List-contract run from clean `2ccb473`: 9/10 calls completed; one prompt-example quote failed evidence validation. Provisional delivered TP/FP/FN = 6/4/2 (precision 60%, recall 75%); five fully correct matched items out of eight labels. No string-null failures, but refusals, suggestions, unanswered requests, invented deadlines and wrong ownership persisted. The adapter remains evaluation-only; public API behavior is unchanged. Model successful-call median/max 1.083/1.707 seconds; failed call 0.868 seconds. See `evals/results/REPORT-2ccb473.md`.

Evaluation-only two-stage commitment adapter implemented: classify candidates with exact evidence, then generate fields only for committed candidates. No selected candidates skips the second call. Final evidence references and item counts must match selected candidates; failures propagate. Public API unchanged. 136 tests and Ruff pass; live results are recorded below.

Two-stage decision run `82df13e`: 8/10 attempts completed, with 14 total generation calls. Provisional TP/FP/FN = 4/1/4 (80% precision, 50% recall); all three negative cases correctly excluded, but zero fully correct items out of eight labels. All five returned owners were Maya despite no Maya in the dataset; three returned deadlines were also Maya. Two attempts failed on fabricated first-stage evidence. Paired owner errors 4/4 and deadline errors 2/4. Successful-attempt median/max duration 1.877/4.406 seconds. Public API unchanged; experiment not adopted. See `evals/results/REPORT-82df13e.md`.

Field provenance implemented in the public extraction flow: non-null owner/deadline must occur verbatim at word boundaries in item evidence; blanks, absent names/dates, and partial-name matches fail. Errors propagate as 502 and return no partial result. Prompt now requests verbatim values. Tests explicitly show that quote presence does not establish owner attribution. 147 tests and Ruff pass; no new live model quality measurements claimed. Deterministic replay only: the guard rejects all five formerly delivered items from the two-stage experiment and two of ten delivered list-contract items. These are archived-output checks, not new inference results or revised historical scores.

November 2 demo smoke: launched the documented Uvicorn reload command and checked
the actual TCP server. Health, Swagger markup, and OpenAPI returned 200. Blank
transcript returned 422; the synthetic Maya report commitment returned 200 with
the expected fields, exact evidence, and needs_review through real Ollama. Browser
automation host was unavailable and native browser access timed out; visual
rendering and Try it out remain unverified. See `docs/DEMO.md` for reproducible
steps and limits. No video or public project page exists yet. Current checks:
147 tests and Ruff pass.
