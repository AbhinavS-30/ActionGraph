import asyncio
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import httpx
import pytest
from pydantic import ValidationError

from app.config import Settings, get_settings
from app.main import app
from app.storage import (
    InvalidSavedReview,
    MissingSession,
    RevisionConflict,
    SavedReviewRequest,
    SessionCreate,
    SessionStore,
    StoreBusy,
    StoreError,
)

SOURCE = (
    "  Maya: I will send Leo the report tomorrow.  \nMaya: I will review the checklist."
)


@pytest.fixture
def store(tmp_path):
    value = SessionStore(tmp_path / "test.sqlite3", timeout=0.05)
    value.initialize()
    return value


def decision(revision=1, index=0):
    return SavedReviewRequest(
        expected_revision=revision,
        decisions=[
            {"proposal_index": index, "decision": "confirm"},
            {"proposal_index": 1, "decision": "reject"},
        ],
    )


def test_reopen_preserves_originals_nulls_ids_and_latest_review(store):
    created = store.create(SessionCreate(transcript=SOURCE))
    assert created.revision == 1 and created.latest_review is None
    assert created.proposals[0].item.evidence == SOURCE.splitlines()[0]
    assert created.proposals[1].item.deadline is None
    updated = store.review(created.id, decision())
    assert updated.revision == 2
    assert updated.latest_review[0].reviewed.review_status == "confirmed"
    assert updated.latest_review[1].reviewed is None
    reopened = SessionStore(store.path).get(created.id)
    assert reopened == updated
    assert reopened.proposals == created.proposals
    replacement = created.proposals[0].item.model_copy(
        update={"action": "Send the report to Leo"}
    )
    changed = store.review(
        created.id,
        SavedReviewRequest(
            expected_revision=2,
            decisions=[
                {
                    "proposal_index": 0,
                    "decision": "confirm",
                    "replacement": replacement,
                },
                {"proposal_index": 1, "decision": "confirm"},
            ],
        ),
    )
    assert changed.revision == 3
    assert changed.latest_review[0].reviewed.action == replacement.action
    assert changed.proposals == created.proposals


def test_invalid_batch_and_stale_write_leave_data_unchanged(store):
    created = store.create(SessionCreate(transcript=SOURCE))
    with pytest.raises(InvalidSavedReview):
        store.review(created.id, SavedReviewRequest(expected_revision=1, decisions=[]))
    assert store.get(created.id) == created
    current = store.review(created.id, decision())
    with pytest.raises(RevisionConflict):
        store.review(created.id, decision())
    with pytest.raises(RevisionConflict):
        store.delete(created.id, 1)
    assert store.get(created.id) == current


def test_concurrent_same_revision_only_one_commits(store):
    created = store.create(SessionCreate(transcript=SOURCE))
    barrier = Barrier(2)

    def update():
        barrier.wait()
        try:
            return store.review(created.id, decision()).revision
        except RevisionConflict:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: update(), range(2)))
    assert sorted(map(str, results)) == ["2", "conflict"]
    assert store.get(created.id).revision == 2


def test_delete_cascades_and_missing_is_404(store):
    created = store.create(SessionCreate(transcript=SOURCE))
    store.review(created.id, decision())
    store.delete(created.id, 2)
    with pytest.raises(MissingSession):
        store.get(created.id)
    with pytest.raises(MissingSession):
        store.delete(created.id, 2)
    with sqlite3.connect(store.path) as db:
        assert db.execute("SELECT count(*) FROM reviews").fetchone()[0] == 0
        assert db.execute("SELECT count(*) FROM sessions").fetchone()[0] == 0


def test_lock_timeout_and_sql_failure_do_not_partially_save(store):
    created = store.create(SessionCreate(transcript=SOURCE))
    with sqlite3.connect(store.path) as db:
        db.execute("BEGIN IMMEDIATE")
        with pytest.raises(StoreBusy):
            store.review(created.id, decision())
    assert store.get(created.id) == created
    with sqlite3.connect(store.path) as db:
        db.execute(
            "CREATE TRIGGER fail_update BEFORE UPDATE ON sessions BEGIN SELECT RAISE(ABORT, 'private error'); END"
        )
    with pytest.raises(StoreError):
        store.review(created.id, decision())
    assert store.get(created.id) == created


def test_oversized_proposal_batch_saves_nothing(store):
    source = "\n".join("Maya: I will review logs." for _ in range(101))
    with pytest.raises(InvalidSavedReview):
        store.create(SessionCreate(transcript=source))
    with sqlite3.connect(store.path) as db:
        assert db.execute("SELECT count(*) FROM sessions").fetchone()[0] == 0


def test_existing_unknown_schema_and_missing_parent_fail(tmp_path):
    path = tmp_path / "unknown.db"
    with sqlite3.connect(path) as db:
        db.execute("PRAGMA user_version=9")
    with pytest.raises(RuntimeError, match="Unsupported"):
        SessionStore(path).initialize()
    with pytest.raises(RuntimeError, match="initialize"):
        SessionStore(tmp_path / "absent" / "x.db").initialize()


def test_removed_store_is_not_recreated(store):
    store.path.unlink()
    with pytest.raises(StoreError):
        store.get(uuid4())
    assert not store.path.exists()


@pytest.mark.parametrize("value", ["", " ", ":memory:", "relative.db"])
def test_config_requires_explicit_absolute_file(value):
    with pytest.raises(ValidationError):
        Settings(actiongraph_db_path=value)


def test_storage_opt_in_and_lifespan(tmp_path, monkeypatch):
    monkeypatch.delenv("ACTIONGRAPH_DB_PATH", raising=False)
    get_settings.cache_clear()

    async def run():
        async with app.router.lifespan_context(app):
            pass

    try:
        asyncio.run(run())
        assert list(tmp_path.iterdir()) == []
        path = tmp_path / "saved.db"
        monkeypatch.setenv("ACTIONGRAPH_DB_PATH", str(path))
        get_settings.cache_clear()
        asyncio.run(run())
        assert path.exists()
    finally:
        get_settings.cache_clear()


def test_saved_session_api_and_disabled_mode(store, monkeypatch):
    def fail(*args, **kwargs):
        pytest.fail("Saved rules sessions must not construct model clients")

    monkeypatch.setattr("app.main.httpx.Client", fail)
    app.dependency_overrides[get_settings] = lambda: Settings(
        actiongraph_db_path=store.path
    )

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post("/sessions", json={"transcript": SOURCE})
            assert response.status_code == 201
            created = response.json()
            url = "/sessions/" + created["id"]
            assert (await client.get(url)).json() == created
            response = await client.put(url + "/review", json=decision().model_dump())
            assert response.status_code == 200 and response.json()["revision"] == 2
            assert (
                await client.put(url + "/review", json=decision().model_dump())
            ).status_code == 409
            assert (
                await client.delete(url + "?expected_revision=1")
            ).status_code == 409
            assert (
                await client.delete(url + "?expected_revision=2")
            ).status_code == 204
            assert (await client.get(url)).status_code == 404
            assert (await client.get("/sessions/not-a-uuid")).status_code == 422
            assert (
                await client.post(
                    "/sessions", json={"transcript": SOURCE, "engine": "ollama"}
                )
            ).status_code == 422
            app.dependency_overrides[get_settings] = lambda: Settings()
            assert (
                await client.post("/sessions", json={"transcript": SOURCE})
            ).status_code == 503

    try:
        asyncio.run(run())
    finally:
        app.dependency_overrides.pop(get_settings, None)


@pytest.mark.parametrize(
    "replacement",
    [{"evidence": "Other quote"}, {"owner": "Absent"}, {"deadline": "Monday"}],
)
def test_correction_must_match_stored_source_and_rolls_back(store, replacement):
    created = store.create(SessionCreate(transcript=SOURCE))
    corrected = {**created.proposals[0].item.model_dump(), **replacement}
    request = SavedReviewRequest(
        expected_revision=1,
        decisions=[
            {"proposal_index": 0, "decision": "confirm", "replacement": corrected},
            {"proposal_index": 1, "decision": "reject"},
        ],
    )
    with pytest.raises(InvalidSavedReview):
        store.review(created.id, request)
    assert store.get(created.id) == created


def test_empty_session_and_duplicate_creation_have_independent_ids(store):
    one = store.create(SessionCreate(transcript="Maya: Good morning."))
    two = store.create(SessionCreate(transcript="Maya: Good morning."))
    assert one.id != two.id
    assert one.proposals == []
    assert (
        store.review(
            one.id, SavedReviewRequest(expected_revision=1, decisions=[])
        ).latest_review
        == []
    )
    assert store.get(two.id).revision == 1


def test_session_creation_rejects_caller_proposals_or_engine():
    for extra in [{"engine": "rules"}, {"proposals": []}, {"transcript": " "}]:
        with pytest.raises(ValidationError):
            SessionCreate.model_validate({"transcript": SOURCE, **extra})
