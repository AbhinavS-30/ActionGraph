# Validation design

## Input boundary

`validate_transcript(text)` requires a string. Non-string input raises TypeError. Leading and trailing whitespace is removed; blank results raise ValueError. Internal whitespace is preserved. This check does not decide whether the transcript contains a commitment.

## Structured response boundary

`parse_extraction_result(text)` requires response text, parses JSON, and validates the resulting data with ExtractionResult. Malformed JSON raises JSONDecodeError. Data that violates the contract raises Pydantic ValidationError. The parser does not call a model, repair output, or check evidence.

## Evidence boundary

`evidence_matches(transcript, evidence)` validates transcript input and requires string evidence. Blank evidence returns False. Nonblank evidence is compared exactly against the original transcript without changing either string. This preserves quote boundaries, case, spacing, and punctuation.

An exact match establishes quote presence only. It does not establish that an action, owner, deadline, or commitment was interpreted correctly. Human review and extraction evaluation remain separate responsibilities.

## Review boundary

The current schema defaults review_status to needs_review and also permits confirmed. No confirmation workflow, persistence, or automatic unsupported-evidence flagging is implemented.

## Model transport boundary

`generate_text(prompt, client=...)` sends a nonblank prompt to Ollama `/api/generate` with `stream=false`. The caller owns the HTTPX client and configures its base URL and timeout. Connection, timeout, and HTTP status errors propagate unchanged. Invalid JSON, missing or blank response text, error envelopes, and incomplete generations raise `OllamaResponseError`. No retries or silent fallback to an empty action list occur. Generated text is returned unchanged; validating its action-item JSON remains the separate parser’s responsibility.

## Extraction policy and prompt boundary

The initial policy includes explicit commitments and explicitly accepted requests. Suggestions, tentative proposals, ambiguous commitments, and unanswered requests are excluded. Unknown owners and unspecified deadlines remain null. Relative deadlines retain their original wording; calendar conversion is deferred. Dependencies belong in the action description rather than being treated as deadlines. Generated items must use `needs_review`.

Evidence must be one contiguous exact excerpt. Accepted requests need evidence containing both the request and acceptance, including intervening text. The planned connected flow will fail extraction if any evidence is unsupported rather than present unsupported items as successful results; enforcement is not implemented yet.

`build_extraction_prompt` validates the transcript and appends the original text as a JSON string to fixed instructions. JSON encoding preserves quotes, newlines, and boundary whitespace. Instructions treat the transcript as data; this does not guarantee model compliance or prevent every prompt injection. Prompt construction tests verify input handling and text preservation, not extraction quality.

The optional `response_schema` argument forwards a JSON schema as Ollama’s `format`. Callers can obtain it using `ExtractionResult.model_json_schema()`. The client still returns text; the caller must pass it to `parse_extraction_result`. A schema request does not replace local validation or semantic evaluation. The existing schema permits `confirmed`; enforcing the stricter generation policy remains a connected-flow task.
