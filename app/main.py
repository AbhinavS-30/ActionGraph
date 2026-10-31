"""Local transcript extraction API."""

import json
from collections.abc import Iterator
from contextlib import asynccontextmanager
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, HTTPException
from pydantic import ValidationError

from app.config import Settings, get_settings
from app.extraction import UnsupportedEvidenceError, extract_actions
from app.ollama import OllamaResponseError
from app.schemas import ExtractionRequest, ExtractionResult


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_settings()  # Fail startup on invalid settings, without contacting Ollama.
    yield


app = FastAPI(title="ActionGraph", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "extraction": "function_available",
        "extraction_api": "available",
    }


def get_ollama_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Iterator[httpx.Client]:
    """Own and close one local client per request; no model readiness probe."""
    with httpx.Client(
        base_url=settings.ollama_base_url,
        timeout=settings.ollama_timeout_seconds,
        trust_env=False,
    ) as client:
        yield client


@app.post("/extract", response_model=ExtractionResult)
def extract(
    request: ExtractionRequest,
    client: Annotated[httpx.Client, Depends(get_ollama_client)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ExtractionResult:
    try:
        return extract_actions(request.transcript, client=client, settings=settings)
    except httpx.TimeoutException as exc:
        raise HTTPException(
            504, "Ollama timed out. Retry with a shorter transcript."
        ) from exc
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(
                503, "Check that the configured model is installed in Ollama."
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
