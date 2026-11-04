"""OpenAPI declarations for existing application errors; no runtime changes."""

from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


class ReviewValidationResponse(BaseModel):
    # Saved review errors can come from request validation or stored-source checks.
    detail: str | list[dict[str, Any]]


STORAGE_ERRORS = {
    500: {
        "model": ErrorResponse,
        "description": "Local storage failed; no partial change is committed.",
    },
    503: {
        "model": ErrorResponse,
        "description": "Saved sessions disabled or SQLite busy. Configure storage/restart, or retry after the active operation.",
    },
}
NOT_FOUND = {
    404: {
        "model": ErrorResponse,
        "description": "Saved session does not exist or has been deleted.",
    }
}
CONFLICT = {
    409: {
        "model": ErrorResponse,
        "description": "Expected revision is stale. GET the latest session before reviewing or deleting; nothing changed.",
    }
}
SAVED_VALIDATION = {
    422: {
        "model": ReviewValidationResponse,
        "description": "Invalid request or saved review, or more than 100 extracted proposals; correct input. No partial result is saved.",
    }
}
EXTRACTION_ERRORS = {
    502: {
        "model": ErrorResponse,
        "description": "Experimental Ollama upstream/output failure, including unsupported evidence or fields; no partial items returned.",
    },
    503: {
        "model": ErrorResponse,
        "description": "Experimental Ollama unreachable, configured model unavailable, or another model extraction active.",
        "headers": {
            "Retry-After": {
                "description": "Present only for a busy model slot; wait this many seconds before retrying.",
                "schema": {"type": "string", "example": "1"},
            }
        },
    },
    504: {
        "model": ErrorResponse,
        "description": "Experimental Ollama network operation timed out; consider shorter input.",
    },
}
