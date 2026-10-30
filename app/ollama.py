"""Request model text without interpreting it as extracted action items."""

from typing import Any

import httpx


class OllamaResponseError(ValueError):
    """Ollama returned an invalid or incomplete generation envelope."""


def generate_text(
    prompt: str,
    *,
    client: httpx.Client,
    model: str = "llama3.2:3b",
    response_schema: dict[str, Any] | None = None,
) -> str:
    """Return generated text using a caller-owned client with a base URL/timeout.

    HTTPX connection, timeout, and HTTP status errors propagate to the caller.
    Invalid JSON or an incomplete envelope raises OllamaResponseError. The text
    inside the envelope is deliberately not parsed against ExtractionResult.
    An optional JSON schema is sent as Ollama's format; callers must still
    validate the returned text locally.
    """
    if not isinstance(prompt, str):
        raise TypeError("Prompt must be a string.")
    if not prompt.strip():
        raise ValueError("Prompt must not be blank.")

    payload = {"model": model, "prompt": prompt, "stream": False}
    if response_schema is not None:
        payload["format"] = response_schema
    response = client.post("/api/generate", json=payload)
    response.raise_for_status()
    try:
        data = response.json()
    except ValueError as exc:
        raise OllamaResponseError("Ollama returned invalid JSON.") from exc

    if (
        not isinstance(data, dict)
        or data.get("done") is not True
        or not isinstance(data.get("response"), str)
        or not data["response"].strip()
        or "error" in data
    ):
        raise OllamaResponseError("Ollama returned an invalid generation envelope.")

    return data["response"]
