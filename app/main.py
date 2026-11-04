"""Local transcript extraction API."""

import json
from collections.abc import Iterator
from contextlib import asynccontextmanager
from threading import BoundedSemaphore
from typing import Annotated
from uuid import UUID

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.api_docs import (
    CONFLICT,
    EXTRACTION_ERRORS,
    NOT_FOUND,
    SAVED_VALIDATION,
    STORAGE_ERRORS,
    ErrorResponse,
)
from app.body_limit import RequestBodyLimit
from app.config import Settings, get_settings
from app.extraction import UnsupportedEvidenceError, extract_actions
from app.ollama import OllamaResponseError
from app.provenance import UnsupportedFieldError
from app.review import ReviewRequest, ReviewResponse, review_actions
from app.rules import RULES_SCOPE, extract_rule_actions
from app.schemas import ExtractionRequest, ExtractionResponse
from app.storage import (
    SavedReviewRequest,
    SavedSession,
    SessionCreate,
    SessionStore,
    StoreError,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.actiongraph_db_path is not None:
        SessionStore(settings.actiongraph_db_path).initialize()
    yield


app = FastAPI(
    title="ActionGraph",
    version="0.1.0",
    lifespan=lifespan,
    responses={
        413: {
            "model": ErrorResponse,
            "description": "Raw HTTP request body exceeds 2 MiB. Send a smaller batch; no endpoint processing occurred.",
        }
    },
)
app.add_middleware(RequestBodyLimit)
extraction_slot = BoundedSemaphore(1)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "extraction": "function_available",
        "extraction_api": "available",
        "default_engine": "rules",
    }


def get_ollama_client(
    request: ExtractionRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> Iterator[httpx.Client | None]:
    """Own and close one local client per request; no model readiness probe."""
    if request.engine == "rules":
        yield None
        return
    with httpx.Client(
        base_url=settings.ollama_base_url,
        timeout=settings.ollama_timeout_seconds,
        trust_env=False,
    ) as client:
        yield client


@app.post("/extract", response_model=ExtractionResponse, responses=EXTRACTION_ERRORS)
def extract(
    request: ExtractionRequest,
    client: Annotated[httpx.Client | None, Depends(get_ollama_client)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ExtractionResponse:
    if request.engine == "rules":
        result = extract_rule_actions(request.transcript)
        return ExtractionResponse(
            items=result.items, engine="rules", limitations=[RULES_SCOPE]
        )
    assert client is not None
    if not extraction_slot.acquire(blocking=False):
        raise HTTPException(
            503,
            "Another extraction is running. Retry after it finishes.",
            headers={"Retry-After": "1"},
        )
    try:
        result = extract_actions(request.transcript, client=client, settings=settings)
        return ExtractionResponse(
            items=result.items,
            engine="ollama",
            limitations=[
                "Experimental local model: evaluation found false commitments, missed tasks and invalid fields. Review every item."
            ],
        )
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
    except UnsupportedFieldError as exc:
        raise HTTPException(
            502,
            "Model owner or deadline is not supported by its evidence. Review input and retry.",
        ) from exc
    except (OllamaResponseError, json.JSONDecodeError, ValidationError) as exc:
        raise HTTPException(
            502, "Ollama returned invalid output. Retry and review the result."
        ) from exc
    finally:
        extraction_slot.release()


@app.post("/review", response_model=ReviewResponse)
def review(request: ReviewRequest) -> ReviewResponse:
    return review_actions(request)


def get_session_store(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SessionStore:
    if settings.actiongraph_db_path is None:
        raise HTTPException(
            503,
            "Saved sessions are disabled. Configure ACTIONGRAPH_DB_PATH and restart.",
        )
    return SessionStore(settings.actiongraph_db_path)


@app.exception_handler(StoreError)
async def storage_error_handler(request: Request, exc: StoreError):
    return JSONResponse(status_code=exc.status, content={"detail": exc.message})


@app.post(
    "/sessions",
    response_model=SavedSession,
    status_code=201,
    responses={**STORAGE_ERRORS, **SAVED_VALIDATION},
)
def create_session(
    request: SessionCreate, store: Annotated[SessionStore, Depends(get_session_store)]
):
    return store.create(request)


@app.get(
    "/sessions/{session_id}",
    response_model=SavedSession,
    responses={**STORAGE_ERRORS, **NOT_FOUND},
)
def get_session(
    session_id: UUID, store: Annotated[SessionStore, Depends(get_session_store)]
):
    return store.get(session_id)


@app.put(
    "/sessions/{session_id}/review",
    response_model=SavedSession,
    responses={**STORAGE_ERRORS, **NOT_FOUND, **CONFLICT, **SAVED_VALIDATION},
)
def review_session(
    session_id: UUID,
    request: SavedReviewRequest,
    store: Annotated[SessionStore, Depends(get_session_store)],
):
    return store.review(session_id, request)


@app.delete(
    "/sessions/{session_id}",
    status_code=204,
    responses={**STORAGE_ERRORS, **NOT_FOUND, **CONFLICT},
)
def delete_session(
    session_id: UUID,
    expected_revision: Annotated[int, Query(ge=1)],
    store: Annotated[SessionStore, Depends(get_session_store)],
):
    store.delete(session_id, expected_revision)
    return Response(status_code=204)
