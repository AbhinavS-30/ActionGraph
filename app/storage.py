"""Opt-in local SQLite rules sessions with atomic revision-checked reviews."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.config import MAX_TRANSCRIPT_CHARS
from app.review import ReviewDecision, ReviewedProposal, ReviewRequest, review_actions
from app.rules import RULES_VERSION, extract_rule_actions
from app.schemas import ActionItem
from app.validation import validate_transcript


class StoreError(Exception):
    status = 500
    message = "Local storage failed. Check the configured database."


class MissingSession(StoreError):
    status = 404
    message = "Saved session not found."


class RevisionConflict(StoreError):
    status = 409
    message = "Session revision changed. Reload before reviewing or deleting."


class StoreBusy(StoreError):
    status = 503
    message = "Local storage is busy. Retry after the active operation finishes."


class InvalidSavedReview(StoreError):
    status = 422
    message = (
        "Invalid saved review. Supply complete decisions and preserve source evidence."
    )


class SessionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    transcript: str = Field(max_length=MAX_TRANSCRIPT_CHARS)

    @field_validator("transcript")
    @classmethod
    def validate_source(cls, value: str) -> str:
        validate_transcript(value)
        return value


class SavedReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=1, strict=True)
    decisions: list[ReviewDecision] = Field(max_length=100)


class SavedProposal(BaseModel):
    id: UUID
    proposal_index: int
    item: ActionItem


class SavedSession(BaseModel):
    id: UUID
    transcript: str
    engine: Literal["rules"] = "rules"
    rules_version: str
    schema_version: Literal[1] = 1
    created_at: str
    updated_at: str
    revision: int
    proposals: list[SavedProposal]
    latest_review: list[ReviewedProposal] | None = None
    persisted: Literal[True] = True


def now() -> str:
    return datetime.now(UTC).isoformat()


class SessionStore:
    def __init__(self, path: Path, *, timeout: float = 1):
        self.path = path
        self.timeout = timeout

    @contextmanager
    def connection(self):
        # rw prevents an accidentally removed database being recreated by a request.
        try:
            with sqlite3.connect(
                self.path.as_uri() + "?mode=rw", uri=True, timeout=self.timeout
            ) as db:
                db.execute("PRAGMA foreign_keys=ON")
                yield db
        except sqlite3.Error as exc:
            if getattr(exc, "sqlite_errorcode", 0) & 255 in (
                sqlite3.SQLITE_BUSY,
                sqlite3.SQLITE_LOCKED,
            ):
                raise StoreBusy() from exc
            raise StoreError() from exc
        finally:
            if "db" in locals():
                db.close()

    def initialize(self) -> None:
        """Create only a new schema; never reinterpret an unknown existing store."""
        try:
            with sqlite3.connect(self.path, timeout=self.timeout) as db:
                db.execute("BEGIN IMMEDIATE")
                version = db.execute("PRAGMA user_version").fetchone()[0]
                tables = {
                    r[0]
                    for r in db.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                }
                if version == 0 and not tables:
                    db.execute(
                        "CREATE TABLE sessions (id TEXT PRIMARY KEY, revision INTEGER NOT NULL CHECK(revision>=1), updated_at TEXT NOT NULL, payload TEXT NOT NULL)"
                    )
                    db.execute(
                        "CREATE TABLE reviews (session_id TEXT PRIMARY KEY REFERENCES sessions(id) ON DELETE CASCADE, payload TEXT NOT NULL)"
                    )
                    db.execute("PRAGMA user_version=1")
                elif version != 1 or tables != {"sessions", "reviews"}:
                    raise RuntimeError(
                        "Unsupported ActionGraph database schema. Use a compatible store or a new file."
                    )
                db.execute(
                    "SELECT id, revision, updated_at, payload FROM sessions LIMIT 0"
                )
                db.execute("SELECT session_id, payload FROM reviews LIMIT 0")
        except sqlite3.Error as exc:
            raise RuntimeError(
                "Cannot initialize ActionGraph storage. Check ACTIONGRAPH_DB_PATH and its existing writable parent directory."
            ) from exc
        finally:
            if "db" in locals():
                db.close()

    def _read(self, db, session_id: UUID) -> SavedSession:
        row = db.execute(
            "SELECT payload, revision, updated_at FROM sessions WHERE id=?",
            (str(session_id),),
        ).fetchone()
        if row is None:
            raise MissingSession()
        review = db.execute(
            "SELECT payload FROM reviews WHERE session_id=?", (str(session_id),)
        ).fetchone()
        try:
            return SavedSession.model_validate(
                {
                    **json.loads(row[0]),
                    "revision": row[1],
                    "updated_at": row[2],
                    "latest_review": json.loads(review[0]) if review else None,
                }
            )
        except (ValueError, TypeError) as exc:
            raise StoreError() from exc

    def create(self, request: SessionCreate) -> SavedSession:
        items = extract_rule_actions(request.transcript).items
        if len(items) > 100:
            raise InvalidSavedReview()
        timestamp = now()
        session = SavedSession(
            id=uuid4(),
            transcript=request.transcript,
            rules_version=RULES_VERSION,
            created_at=timestamp,
            updated_at=timestamp,
            revision=1,
            proposals=[
                SavedProposal(id=uuid4(), proposal_index=i, item=item)
                for i, item in enumerate(items)
            ],
        )
        with self.connection() as db:
            db.execute(
                "INSERT INTO sessions(id, revision, updated_at, payload) VALUES(?, ?, ?, ?)",
                (str(session.id), 1, timestamp, session.model_dump_json()),
            )
        return session

    def get(self, session_id: UUID) -> SavedSession:
        with self.connection() as db:
            db.execute("BEGIN")
            return self._read(db, session_id)

    def review(self, session_id: UUID, request: SavedReviewRequest) -> SavedSession:
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            session = self._read(db, session_id)
            if session.revision != request.expected_revision:
                raise RevisionConflict()
            try:
                validated = ReviewRequest(
                    transcript=session.transcript,
                    proposals=[p.item for p in session.proposals],
                    decisions=request.decisions,
                )
            except ValidationError as exc:
                raise InvalidSavedReview() from exc
            records = review_actions(validated).records
            db.execute(
                "INSERT INTO reviews(session_id, payload) VALUES(?, ?) ON CONFLICT(session_id) DO UPDATE SET payload=excluded.payload",
                (str(session_id), json.dumps([r.model_dump() for r in records])),
            )
            db.execute(
                "UPDATE sessions SET revision=revision+1, updated_at=? WHERE id=?",
                (now(), str(session_id)),
            )
            return self._read(db, session_id)

    def delete(self, session_id: UUID, expected_revision: int) -> None:
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            session = self._read(db, session_id)
            if session.revision != expected_revision:
                raise RevisionConflict()
            db.execute("DELETE FROM sessions WHERE id=?", (str(session_id),))
