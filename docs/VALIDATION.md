# Validation design

## Input boundary

`validate_transcript(text)` requires a string. Non-string input raises TypeError. Leading and trailing whitespace is removed; blank results raise ValueError. Internal whitespace is preserved. This check does not decide whether the transcript contains a commitment.

## Structured response boundary

`parse_extraction_result(text)` requires response text, parses JSON, and validates the resulting data with ExtractionResult. Malformed JSON raises JSONDecodeError. Data that violates the contract raises Pydantic ValidationError. The parser does not call a model, repair output, or check evidence.

## Evidence boundary

`evidence_matches(transcript, evidence)` validates transcript input and requires string evidence. Blank evidence returns False. Nonblank evidence is compared exactly against the original transcript without changing either string. This preserves quote boundaries, case, spacing, and punctuation.

An exact match establishes quote presence only. It does not establish that an action, owner, deadline, or commitment was interpreted correctly. Human review and extraction evaluation remain separate responsibilities.

## Review boundary

The current schema defaults review_status to needs_review and also permits confirmed. No confirmation workflow or persistence is implemented. The extraction function forces generated items to `needs_review` and fails on unsupported evidence.

## Model transport boundary

`generate_text(prompt, client=...)` sends a nonblank prompt to Ollama `/api/generate` with `stream=false`. The caller owns the HTTPX client and configures its base URL and timeout. Connection, timeout, and HTTP status errors propagate unchanged. Invalid JSON, missing or blank response text, error envelopes, and incomplete generations raise `OllamaResponseError`. No retries or silent fallback to an empty action list occur. Generated text is returned unchanged; validating its action-item JSON remains the separate parser’s responsibility.

## Extraction policy and prompt boundary

The initial policy includes explicit commitments and explicitly accepted requests. Suggestions, tentative proposals, ambiguous commitments, and unanswered requests are excluded. Unknown owners and unspecified deadlines remain null. Relative deadlines retain their original wording; calendar conversion is deferred. Dependencies belong in the action description rather than being treated as deadlines. Generated items must use `needs_review`.

Evidence must be one contiguous exact excerpt. Accepted requests need evidence containing both the request and acceptance, including intervening text. The connected extraction function raises `UnsupportedEvidenceError` if any evidence is unsupported and returns no partial result.

`build_extraction_prompt` validates the transcript and appends the original text as a JSON string to fixed instructions. JSON encoding preserves quotes, newlines, and boundary whitespace. Instructions treat the transcript as data; this does not guarantee model compliance or prevent every prompt injection. Prompt construction tests verify input handling and text preservation, not extraction quality.

The optional `response_schema` argument forwards a JSON schema as Ollama’s `format`. Callers can obtain it using `ExtractionResult.model_json_schema()`. The client still returns text; the caller must pass it to `parse_extraction_result`. A schema request does not replace local validation or semantic evaluation. The existing schema permits `confirmed`; the extraction function resets every generated item to `needs_review` before returning.

## Connected extraction boundary

`extract_actions(transcript, client=...)` builds the prompt, calls the model with the output schema, parses its response, and checks every evidence excerpt against the original transcript. Input, transport, and parser exceptions propagate. One unsupported excerpt fails the entire result. Review status is controlled by the application rather than the model. These checks do not verify commitment meaning, owner attribution, deadline interpretation, or completeness. Unit tests use simulated model responses; the reusable function has not yet been evaluated against a labeled dataset.

## HTTP boundary

`ExtractionRequest` requires a string transcript, rejects blank text and unexpected fields, and preserves the original transcript for evidence checking. FastAPI returns 422 on invalid requests before model invocation. `POST /extract` uses a synchronous route and a request-scoped HTTPX client, closed through a yielding dependency. Its fixed local URL is `http://127.0.0.1:11434`; the timeout is 60 seconds per HTTPX network operation, not a total request deadline.

Timeout errors map to 504; connection/request failures and upstream 404 map to 503; other upstream status errors, invalid envelopes, malformed model JSON, output schema failures, and unsupported evidence map to 502. Error responses omit raw model text and internal exception details. Invalid model output is never returned as a successful empty list. `/health` reports implemented capabilities, not Ollama readiness. Tests replace the client dependency with simulated responses, exercising the API through evidence checking.
