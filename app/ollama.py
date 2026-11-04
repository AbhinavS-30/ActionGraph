"""Request model text without interpreting it as extracted action items."""

from typing import Any

import httpx


class OllamaResponseError(ValueError):
    """Ollama returned an invalid or incomplete generation envelope."""


MAX_OLLAMA_RESPONSE_BYTES = 1024 * 1024


class BoundedResponseStream(httpx.SyncByteStream):
    """Stop buffering at the envelope byte cap; close the underlying stream."""

    def __init__(self, stream: httpx.SyncByteStream):
        self.stream = stream

    def __iter__(self):
        total = 0
        for chunk in self.stream:
            total += len(chunk)
            if total > MAX_OLLAMA_RESPONSE_BYTES:
                raise OllamaResponseError("Ollama response exceeds the 1 MiB limit.")
            yield chunk

    def close(self):
        self.stream.close()


def read_bounded_response(response: httpx.Response) -> bytes:
    """Read an identity-encoded envelope with a cap, also usable by eval capture."""
    if response.headers.get("content-encoding", "identity").strip().lower() not in {
        "",
        "identity",
    }:
        raise OllamaResponseError("Compressed Ollama responses are unsupported.")
    length = response.headers.get("content-length", "")
    if length.isascii() and length.isdigit():
        size = length.lstrip("0") or "0"
        cap = str(MAX_OLLAMA_RESPONSE_BYTES)
        if len(size) > len(cap) or (len(size) == len(cap) and size > cap):
            raise OllamaResponseError("Ollama response exceeds the 1 MiB limit.")
    if response.is_stream_consumed:
        if len(response.content) > MAX_OLLAMA_RESPONSE_BYTES:
            raise OllamaResponseError("Ollama response exceeds the 1 MiB limit.")
        return response.content
    response.stream = BoundedResponseStream(response.stream)
    return response.read()


def generate_text(
    prompt: str,
    *,
    client: httpx.Client,
    model: str = "llama3.2:3b",
    response_schema: dict[str, Any] | None = None,
    num_predict: int = 1024,
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

    if (
        not isinstance(num_predict, int)
        or isinstance(num_predict, bool)
        or not 1 <= num_predict <= 4096
    ):
        raise ValueError("num_predict must be an integer between 1 and 4096.")
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": num_predict},
    }
    if response_schema is not None:
        payload["format"] = response_schema
    with client.stream(
        "POST", "/api/generate", json=payload, headers={"Accept-Encoding": "identity"}
    ) as response:
        response.raise_for_status()
        read_bounded_response(response)
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
        or data.get("done_reason") == "length"
    ):
        raise OllamaResponseError("Ollama returned an invalid generation envelope.")

    return data["response"]
