# Validation design

## Input boundary

`validate_transcript(text)` requires a string. Non-string input raises TypeError. More than 12,000 original characters raises ValueError before trimming. Leading and trailing whitespace is removed; blank results raise ValueError. Internal whitespace is preserved. This check does not decide whether the transcript contains a commitment.

## Structured response boundary

`parse_extraction_result(text)` requires response text, parses JSON, and validates the resulting data with ExtractionResult. Malformed JSON raises JSONDecodeError. Data that violates the contract raises Pydantic ValidationError. The parser does not call a model, repair output, or check evidence.

## Evidence boundary

`evidence_matches(transcript, evidence)` validates transcript input and requires string evidence. Blank evidence returns False. Nonblank evidence is compared exactly against the original transcript without changing either string. This preserves quote boundaries, case, spacing, and punctuation.

An exact match establishes quote presence only. It does not establish that an action, owner, deadline, or commitment was interpreted correctly. Human review and extraction evaluation remain separate responsibilities.

## Review boundary

The current schema defaults review_status to needs_review and also permits confirmed. Stateless confirmation is available through POST /review; persistence is not implemented. The extraction function forces generated items to `needs_review` and fails on unsupported evidence.

## Model transport boundary

`generate_text(prompt, client=...)` sends a nonblank prompt to Ollama `/api/generate` with `stream=false`. The caller owns the HTTPX client and configures its base URL and timeout. Connection, timeout, and HTTP status errors propagate unchanged. Invalid JSON, missing or blank response text, error envelopes, and incomplete generations raise `OllamaResponseError`. No retries or silent fallback to an empty action list occur. Generated text is returned unchanged; validating its action-item JSON remains the separate parser’s responsibility.

## Extraction policy and prompt boundary

The initial policy includes explicit commitments and explicitly accepted requests. Suggestions, tentative proposals, ambiguous commitments, and unanswered requests are excluded. Unknown owners and unspecified deadlines remain null. Relative deadlines retain their original wording; calendar conversion is deferred. Dependencies belong in the action description rather than being treated as deadlines. Generated items must use `needs_review`.

Evidence must be one contiguous exact excerpt. Accepted requests need evidence containing both the request and acceptance, including intervening text. The connected extraction function raises `UnsupportedEvidenceError` if any evidence is unsupported and returns no partial result.

`build_extraction_prompt` validates the transcript and appends the original text as a JSON string to fixed instructions. JSON encoding preserves quotes, newlines, and boundary whitespace. Instructions treat the transcript as data; this does not guarantee model compliance or prevent every prompt injection. Prompt construction tests verify input handling and text preservation, not extraction quality.

The optional `response_schema` argument forwards a JSON schema as Ollama’s `format`. Callers can obtain it using `ExtractionResult.model_json_schema()`. The client still returns text; the caller must pass it to `parse_extraction_result`. A schema request does not replace local validation or semantic evaluation. The existing schema permits `confirmed`; the extraction function resets every generated item to `needs_review` before returning.

## Connected extraction boundary

`extract_actions(transcript, client=...)` builds the prompt, calls the model with the output schema, parses its response, and checks every evidence excerpt against the original transcript. Input, transport, and parser exceptions propagate. One unsupported excerpt fails the entire result. Review status is controlled by the application rather than the model. These checks do not verify commitment meaning, owner attribution, deadline interpretation, or completeness. Unit tests use simulated model responses; the first ten-case development comparison is retained in `evals/results/`, with provisional Codex review and human adjudication pending.

## HTTP boundary

`ExtractionRequest` requires a string transcript, rejects blank text and unexpected fields, and preserves the original transcript for evidence checking. FastAPI returns 422 on invalid requests before model invocation. `POST /extract` uses a synchronous route and a request-scoped HTTPX client, closed through a yielding dependency. Its default local URL is `http://127.0.0.1:11434`; validated exported settings can override loopback origin, model, timeout, and generated-token cap. The default timeout is 60 seconds per HTTPX network operation, not a total request deadline.

Timeout errors map to 504; connection/request failures and upstream 404 map to 503; other upstream status errors, invalid envelopes, malformed model JSON, output schema failures, and unsupported evidence map to 502. Error responses omit raw model text and internal exception details. Invalid model output is never returned as a successful empty list. `/health` reports implemented capabilities, not Ollama readiness. Tests replace the client dependency with simulated responses, exercising the API through evidence checking.

## Unknown-value contract

`ActionItem` rejects owner or deadline strings whose stripped, case-folded value
is `null`. JSON null remains Python None and is allowed. Other strings are
returned unchanged; no inference or silent repair occurs. Violations raise
Pydantic ValidationError and map to HTTP 502 for model output. This custom Python
validator is not expressed by the generated JSON schema, so local validation
remains necessary even for schema-constrained requests. The change prevents
invalid placeholder delivery; it does not establish better model extraction.
Historical evaluation reports describe the source revisions recorded in them
and must not be reinterpreted as results from the current stricter contract.

## Runtime limits

Settings are validated once at startup and cached until restart, using existing Pydantic without a new settings dependency. Only HTTP loopback Ollama origins are allowed; HTTPX ignores proxy environment variables for local requests. The extraction function and evaluation collector receive the effective model and generated-token cap. Requests include `options.num_predict` (default 1024, permitted 1–4096); `done_reason=length` raises `OllamaResponseError` instead of returning a potentially partial result. The 12,000-character transcript cap is shared by the schema and standalone transcript validator and preserves original evidence boundaries. Raw HTTP body bytes, upstream response bytes, total duration, and concurrency are not bounded by this change.

## API concurrency boundary

A process-local `BoundedSemaphore(1)` admits one extraction. Nonblocking acquisition
returns HTTP 503 and `Retry-After: 1` when busy, before model invocation. The route
always releases an acquired slot in `finally`, including transport and validation
failures. Invalid input still fails request validation before entering the route.
Health does not acquire the slot. Tests overlap two requests using events rather
than timing sleeps and verify slot reuse after success and failure. This protects
one API process only: multiple workers, standalone extraction, and other clients
of Ollama are not coordinated.

## Field-text provenance boundary

After transcript quote matching, the production extraction function checks that
each non-null owner and deadline occurs verbatim in that item's evidence, with
Unicode word boundaries to prevent matching a name inside another name. Case,
spacing, and punctuation are not normalized; blank non-null fields fail. Nulls
remain allowed. `UnsupportedFieldError` fails the entire extraction and maps to
HTTP 502 without echoing raw model values. The prompt explicitly requests this
verbatim representation. Experimental adapters remain unchanged for traceable
comparisons; they are not the production path.

This establishes textual presence only, not semantic support. A recipient name
can be mistaken for an owner and a meeting-end time for a deadline even when
both appear in the quote. Paraphrased values and case variations can be rejected,
which is an intentional restrictive policy for this local version. No value is
silently rewritten or replaced with null. Old evaluation artifacts retain the
behavior of their recorded revisions; replaying a new validator is not a fresh
model-quality evaluation.

## Engine selection

`ExtractionRequest.engine` defaults to rules, with ollama as explicit experimental mode. `ExtractionResponse` adds engine and limitations to items. Rules uses the shared input, schema and field-provenance helpers, original-line evidence and needs_review status. It never constructs the model client or acquires the inference slot. Model failures remain failures with no fallback. Rules scope and missed forms are documented in `docs/RULES.md`; successful grammar matching is not general commitment understanding.

## Rules cancellation boundary

Rules v2 processes explicit same-speaker negations against earlier active items.
Task matching shares the bounded promise parser and compares case-folded,
whitespace-collapsed actions with dependencies retained. Undated negations remove
all earlier matches; dated ones remove only the same deadline. Speaker labels
remain exact after edge trimming. Unrelated, vague, conditional, and unresolved
pronoun targets do not remove items. Later recommitments remain possible.
Returned evidence remains the original surviving commitment line. This does not
implement general dialogue resolution. Exact supported forms are in `RULES.md`.
Historical baseline and v1 reports are unchanged; updated runs need their own
source revision and `rules_version` metadata.

## Rules accepted-request boundary

Rules v3 recognizes only adjacent named requests and explicit matching-verb
acceptances as defined in RULES.md. The request supplies action and deadline;
the exact addressed speaker must accept. Evidence spans both original lines,
preserving CRLF or LF and boundary spaces. Other replies or intervening lines
are skipped. Existing cancellation matching applies to the resulting task.
This bounded reference rule does not establish general dialogue understanding.

## Rules two-task boundary

Rules v4 uses a promise-only parser for exactly two complete clauses joined by
and. Each passes the single-task parser before either item is returned. A final
date with no first-clause date is treated as ambiguous and the pair is skipped.
Dependencies in pairs are skipped. Requests and negations retain the single-task
parser. Items share exact original-line evidence; later single-task cancellations
match each item independently. See RULES.md for exact bounds and known omissions.

## Nonblank output-field boundary

ActionItem rejects empty or whitespace-only action/evidence strings and non-null
owner/deadline strings, using Python str.strip() only for the check. Valid values
are returned byte-for-byte unchanged as Python strings; genuine null stays allowed
for owner/deadline. Unicode whitespace recognized by strip is included; this is
not a general invisible-character filter. Zero-width format characters are not
classified as whitespace by this rule. String-null rejection remains separate.

Pydantic field validation runs before evidence/provenance checks: blank output
now raises ValidationError at parsing rather than UnsupportedEvidenceError or
UnsupportedFieldError later. Experimental Ollama API output maps this to 502
without raw content or partial items. These custom Python checks are not encoded
in generated JSON Schema; local validation remains authoritative. Historical
evaluation artifacts retain their recorded behavior. No semantic accuracy claim
or rules grammar change follows from this validation fix.

## Stateless review boundary

ReviewRequest validates source length, up to 100 proposals/decisions, exact
source quotes, needs_review inputs and complete unique index coverage before
review_actions runs. Confirmed corrected owner/deadline retain text-presence
requirements; original evidence cannot change. Rejections preserve submitted
originals without requiring their potentially wrong field attribution to pass.
The function creates deep copies, never mutates its request, and returns records
in proposal order. Validation errors map to 422 with no partial records. No
model dependency or inference slot is used. Caller-supplied originals are not
server-authenticated extraction snapshots, and confirmation is caller assertion.
See REVIEW.md for contract, exact bounds and deferred persistence semantics.
