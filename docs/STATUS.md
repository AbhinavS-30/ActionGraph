# Project status

Updated October 30, 2026.

## Implemented

- FastAPI health endpoint reporting extraction as not implemented.
- Pydantic action-item and extraction-result contracts.
- Transcript validation with explicit type and blank-input failures.
- JSON parsing followed by output schema validation.
- Exact evidence substring checking, including blank-evidence rejection.
- Standalone Ollama text client using existing HTTPX: nonstreaming requests, prompt checks, response-envelope checks, and propagated connection, timeout, and HTTP status errors. The caller supplies the client base URL and timeout.

These components are standalone; extraction is not implemented.

## Verification

56 test cases passed using `.venv/bin/python -m pytest`. Ruff lint passed using `.venv/bin/python -m ruff check app tests`. These checks do not measure extraction quality.

Read-only connectivity checks on October 30 confirmed that GitHub remote `main`
matches local commit `4e40ba6` at `https://github.com/AbhinavS-30/ActionGraph.git`.
The local Ollama service responded at `http://127.0.0.1:11434`, and its model
inventory includes `llama3.2:3b`. A live smoke request through the new client
returned `ready` for a prompt requesting that word. Extraction quality has not
been evaluated.

## Documentation

README now describes the architecture, contract, setup, terminology, design rationale, delivery phases, and limitations. Supporting documents describe the technical roadmap and validation design. Personal learning history is maintained outside project documentation.

## Remaining work

Extraction instructions and structured model output, connected extraction flow, failure and review policies, extraction API, relative-date handling decisions, labeled evaluation, and reproducible demonstration.

## Next task

Define extraction instructions, ambiguity and relative-date rules, and structured output handling before connecting the client to parsing and evidence checks.
