"""Request model text without interpreting it as extracted action items."""

import httpx


class OllamaResponseError(ValueError):
    """Ollama returned an invalid or incomplete generation envelope."""


def generate_text(
    prompt: str, *, client: httpx.Client, model: str = "llama3.2:3b"
) -> str:
    """Return generated text using a caller-owned client with a base URL/timeout.

    HTTPX connection, timeout, and HTTP status errors propagate to the caller.
    Invalid JSON or an incomplete envelope raises OllamaResponseError. The text
    inside the envelope is deliberately not parsed against ExtractionResult.
    """
    if not isinstance(prompt, str):
        raise TypeError("Prompt must be a string.")
    if not prompt.strip():
        raise ValueError("Prompt must not be blank.")

    response = client.post(
        "/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
    )
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
