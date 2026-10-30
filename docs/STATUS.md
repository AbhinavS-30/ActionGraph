# Project status

Updated October 30, 2026.

## Implemented

- FastAPI health endpoint reporting extraction as not implemented.
- Pydantic action-item and extraction-result contracts.
- Transcript validation with explicit type and blank-input failures.
- JSON parsing followed by output schema validation.
- Exact evidence substring checking, including blank-evidence rejection.
- Standalone Ollama text client using existing HTTPX: nonstreaming requests, prompt checks, response-envelope checks, and propagated connection, timeout, and HTTP status errors. The caller supplies the client base URL and timeout.
- Optional JSON schema forwarding through Ollama’s `format` field; parser-boundary tests preserve malformed-JSON and schema-error behavior.
- Extraction policy and standalone prompt builder covering accepted commitments, unknown values, relative deadlines, exact evidence, and review status.

These components are standalone; a reusable extraction pipeline and extraction endpoint are not implemented.

## Verification

62 test cases passed using `.venv/bin/python -m pytest`. Ruff lint passed using `.venv/bin/python -m ruff check app tests`. These checks do not measure extraction quality.

Read-only connectivity checks on October 30 confirmed that GitHub remote `main`
matches local commit `4e40ba6` at `https://github.com/AbhinavS-30/ActionGraph.git`.
The local Ollama service responded at `http://127.0.0.1:11434`, and its model
inventory includes `llama3.2:3b`. A live smoke request through the new client
returned `ready` for a prompt requesting that word. Extraction quality has not
been evaluated.

## Documentation

README now describes the architecture, contract, setup, terminology, design rationale, delivery phases, and limitations. Supporting documents describe the technical roadmap and validation design. Personal learning history is maintained outside project documentation.

## Remaining work

Connected extraction flow and enforcement of agreed policies, extraction API, labeled evaluation, and reproducible demonstration. Broader prompt compliance and extraction quality are unverified.

## Next task

Connect prompt construction, schema-constrained generation, parsing, and evidence checks in a reusable extraction function. Reject unsupported evidence and ensure generated items remain needs_review.

A manual structured-output smoke check combined the prompt builder, client, and parser on the synthetic sentence “Maya: I will send the report tomorrow.” The result contained one item with owner Maya, deadline “tomorrow”, exact sentence evidence, and `needs_review`. This is one smoke example, not extraction-quality evaluation or an integrated service.
