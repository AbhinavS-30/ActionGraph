"""Local transcript extraction API."""

import json
from collections.abc import Iterator
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, HTTPException
from pydantic import ValidationError

from app.extraction import UnsupportedEvidenceError, extract_actions
from app.ollama import OllamaResponseError
from app.schemas import ExtractionRequest, ExtractionResult

app = FastAPI(title="ActionGraph", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "extraction": "function_available",
        "extraction_api": "available",
    }


def get_ollama_client() -> Iterator[httpx.Client]:
    """Own and close one local client per request; no model readiness probe."""
    with httpx.Client(base_url="http://127.0.0.1:11434", timeout=60.0) as client:
        yield client


@app.post("/extract", response_model=ExtractionResult)
def extract(
    request: ExtractionRequest,
    client: Annotated[httpx.Client, Depends(get_ollama_client)],
) -> ExtractionResult:
    try:
        return extract_actions(request.transcript, client=client)
    except httpx.TimeoutException as exc:
        raise HTTPException(
            504, "Ollama timed out. Retry with a shorter transcript."
        ) from exc
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(
                503, "Check that llama3.2:3b is installed in Ollama."
            ) from exc
        raise HTTPException(
            502, "Ollama rejected the generation request. Check Ollama."
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            503, "Cannot reach Ollama. Start the local service and retry."
        ) from exc
    except UnsupportedEvidenceError as exc:
        raise HTTPException(
            502, "Model evidence did not match the transcript. Review input and retry."
        ) from exc
    except (OllamaResponseError, json.JSONDecodeError, ValidationError) as exc:
        raise HTTPException(
            502, "Ollama returned invalid output. Retry and review the result."
        ) from exc
