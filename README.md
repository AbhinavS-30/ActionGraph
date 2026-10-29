# ActionGraph

Evidence-backed action items from meeting transcripts, designed for local inference and human review.

ActionGraph aims to turn meeting discussion into a structured list of commitments: what needs to happen, who owns it, when it is due, and the exact words supporting it. Unknown owners and deadlines remain explicit rather than being guessed.

**Development status:** input validation, JSON parsing, output schemas, exact evidence matching, and a health endpoint are implemented. These components are tested independently. Model extraction and the connected application flow are not implemented yet.

## Intended application

The MVP will accept a text transcript through a local API and return proposed action items for review. FastAPI's interactive API page will provide the initial submission interface. Each item will include an action, nullable owner and deadline, supporting evidence, and review status. A custom dashboard is outside the initial scope.

## Architecture

The diagram describes the target flow. Implemented helpers are labeled explicitly; the arrows represent planned integration, not an existing pipeline.

```mermaid
flowchart TD
    A[Text transcript] --> B[Input validation: implemented]
    B --> C[Local Ollama model: planned]
    C --> D[JSON parsing: implemented]
    D --> E[Pydantic output validation: implemented]
    E --> F[Exact evidence check: implemented]
    A --> F
    F --> G[Reviewable API response: planned]
    G --> H[Human review]
    B -. invalid input .-> X[Explicit failure handling: integration planned]
    C -. unavailable model .-> X
    D -. malformed JSON .-> X
    E -. invalid fields .-> X
    F -. unsupported quote .-> Y[Review flag policy: planned]
```

| Step | Purpose and design choice |
| --- | --- |
| Input validation | Reject non-string and blank input before further processing. Trim outside whitespace while retaining internal text. |
| Local inference | Planned use of Ollama with `llama3.2:3b` to propose items without a paid inference API. Model availability and behavior must be verified during integration. |
| JSON parsing | Convert response text into Python data. Reject malformed JSON rather than silently repairing it. |
| Output validation | Require a consistent structure and field types so downstream code can work with predictable data. |
| Evidence matching | Check quote presence against the original transcript. Preserve spelling, case, spacing, and punctuation. Reject blank evidence as a match. |
| Human review | Keep interpretation open to correction: an exact quote can still be assigned to the wrong action, owner, or deadline. |

## Output contract

An illustrative result follows. It demonstrates the contract, not output from an implemented extractor.

```json
{
  "items": [
    {
      "action": "Send the API specification",
      "owner": "Maya",
      "deadline": "Friday",
      "evidence": "Maya: I will send the API specification by Friday.",
      "review_status": "needs_review"
    }
  ]
}
```

| Field | Meaning and current rules |
| --- | --- |
| `items` | Required list of action items; an empty list is allowed. |
| `action` | Required string with at least one character describing the work. |
| `owner` | Required field containing a string or `null` when unknown. |
| `deadline` | Required field containing a string or `null` when unspecified. Date normalization is not implemented. |
| `evidence` | Required string with at least one character. The separate evidence helper rejects whitespace-only quotes and checks exact presence. |
| `review_status` | `needs_review` by default, or `confirmed`. A confirmation workflow is not implemented. |

Unexpected fields within an action item are rejected. Current minimum-length schema checks do not reject every whitespace-only field. Schema validity does not establish extraction correctness, and the parser does not invoke the evidence checker automatically.

## Available components

| Component | Location | Current behavior |
| --- | --- | --- |
| HTTP health endpoint | `app/main.py` | `GET /health` reports status and explicitly reports extraction as not implemented. |
| Transcript validator | `app/validation.py` | Returns trimmed text; raises `TypeError` for non-string input and `ValueError` for blank input. |
| Output models | `app/schemas.py` | Defines `ActionItem` and the enclosing `ExtractionResult`. |
| Response parser | `app/parsing.py` | Parses JSON, then validates the output contract. Malformed text raises `JSONDecodeError`; schema mismatches raise `ValidationError`. |
| Evidence checker | `app/evidence.py` | Returns a boolean for exact quote presence. Invalid input types and invalid transcripts raise errors. |

## Run locally

Prerequisite: Python 3.12. Run commands from the repository root.

For a new checkout, create an isolated Python environment and install pinned dependencies:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
```

Run the current API:

```bash
.venv/bin/python -m uvicorn app.main:app --reload
```

Open the [interactive API documentation](http://127.0.0.1:8000/docs). Currently it exposes the health endpoint, not extraction.

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status": "ok", "extraction": "not_implemented"}
```

The current helpers and tests do not require Ollama to run. Local model setup will be documented when model integration is implemented. No paid inference API is required by the planned architecture.

## Verification

```bash
.venv/bin/python -m pytest
.venv/bin/python -m ruff check app tests
```

The current suite contains 41 passing test cases covering the health response, output contract, transcript validation, JSON parsing, and exact evidence matching. This is a correctness check of these components, not a measurement of model accuracy.

## Delivery phases

| Phase | Status | Deliverable and completion criteria |
| --- | --- | --- |
| 1. Validation foundation | Implemented as standalone components | Validated input, structured output contract, response parser, evidence helper, and focused tests. |
| 2. Local model integration | Planned | Ollama request handling, extraction instructions, structured response handling, timeouts, and model-unavailability tests. |
| 3. Connected extraction service | Planned | Connect the components; define ambiguous commitment, relative-date, and unsupported-evidence policies; preserve review needs without inventing values. |
| 4. Usable MVP | Planned | Extraction endpoint, documented request/response examples, and actionable error responses through the local API interface. |
| 5. Evaluation and demonstration | Planned | Labeled synthetic transcripts, a documented matching rubric, measured errors and latency, reproducible demo, and disclosed limitations. |

The initial demo target is November 3, 2026. It is a delivery target, not a claim of completion.

## Terminology

| Term | Meaning in ActionGraph |
| --- | --- |
| Transcript | Text recording who said what during a meeting. |
| Action item | Proposed work supported by a commitment in the discussion. |
| Dependency | Something that must happen first; it does not necessarily establish a deadline. |
| JSON | A text format for objects, lists, strings, numbers, and values such as `null`. |
| Parsing | Converting JSON text into Python values; JSON `null` becomes Python `None`. |
| Schema | The contract defining required fields, allowed types, and constraints. |
| Validation | Checking input or output against explicit rules. |
| Evidence | An exact excerpt supporting a proposed item. |
| Inference | Running a model to generate a proposed result from input. |
| API / endpoint | A program interface / a particular route that accepts requests or returns responses. |
| FastAPI / Uvicorn | The Python API framework / the server that runs it locally. |
| Pydantic | The library enforcing the structured output contract. |
| pytest / Ruff | Tools for automated tests / Python code checks and formatting. |
| Ollama | The planned local model runtime; `llama3.2:3b` is the selected model. |
| Precision / recall | Planned evaluation measures: how many proposed items are correct / how many labeled items were found. Both require a defined matching rubric. |
| Latency | Measured time to produce a result; no extraction latency has been measured yet. |

## Scope and limitations

- Use synthetic or public transcripts only. The supplied example is in `data/synthetic/meeting-01.txt`.
- No model calls, end-to-end extraction, evidence flag integration, or review persistence exist yet.
- No extraction precision, recall, or latency results are available.
- Exact evidence matching proves quote presence, not interpretation, attribution, or completeness.
- Relative date conversion and ambiguous commitment policies remain to be defined.
- Audio transcription, calendar integrations, cross-meeting memory, and elaborate dashboards are deferred.
- Keep secrets, virtual environments, model weights, and private data out of version control.

## Repository guide

- `app/`: API and processing components.
- `tests/`: automated behavior checks.
- `data/synthetic/`: example input transcripts.
- `evals/`: reserved for evaluation artifacts; evaluation is not implemented.
- [Project status](docs/STATUS.md): implemented capabilities, checks, and current limitations.
- [Roadmap](docs/ROADMAP.md): delivery phases and acceptance criteria.
- [Validation design](docs/VALIDATION.md): component responsibilities and failure behavior.
