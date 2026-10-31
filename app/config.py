"""Validated environment configuration for local-only inference."""

import os
from functools import lru_cache
from urllib.parse import urlsplit

from pydantic import BaseModel, Field, field_validator

MAX_TRANSCRIPT_CHARS = 12_000


class Settings(BaseModel):
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_timeout_seconds: float = Field(default=60, gt=0, le=120)
    ollama_num_predict: int = Field(default=1024, ge=1, le=4096)

    @field_validator("ollama_base_url")
    @classmethod
    def require_local_url(cls, value: str) -> str:
        url = urlsplit(value)
        if (
            url.scheme != "http"
            or url.hostname not in {"127.0.0.1", "localhost", "::1"}
            or url.username is not None
            or url.password is not None
            or url.path not in {"", "/"}
            or url.query
            or url.fragment
        ):
            raise ValueError(
                "Ollama URL must be an HTTP loopback origin without credentials."
            )
        _ = url.port  # Validate port syntax/range before constructing HTTPX clients.
        return value.rstrip("/")

    @field_validator("ollama_model")
    @classmethod
    def require_nonblank_model(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Ollama model must not be blank.")
        return value


@lru_cache
def get_settings() -> Settings:
    """Read exported variables once; restart the API to apply changes."""
    fields = {
        name: os.environ[name.upper()]
        for name in Settings.model_fields
        if name.upper() in os.environ
    }
    return Settings.model_validate(fields)
