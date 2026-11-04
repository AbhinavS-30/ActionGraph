# Local persistence policy — design, not implemented

The current extract/review routes remain stateless. The next implementation will
add optional saved rules sessions using Python 3.12's standard-library sqlite3.
No new dependency, service, model call or download is needed. This document defines
the behavior before storage code is added; none of these saved-session routes or
settings exist yet.

## Scope and opt-in

Storage is disabled unless ACTIONGRAPH_DB_PATH explicitly names a local database.
No database or parent directory is created when it is unset. Enabling storage may
create the database in an existing writable directory. Invalid configured paths or
unsupported database schema versions fail startup with an actionable error; do not
silently fall back to another file. Default documentation keeps Uvicorn on loopback,
one worker, synthetic/public data only. No authentication is implied by loopback.
Anyone able to access the local API could read or change these sessions.

Existing POST /extract and POST /review keep their contracts and do not save or
modify sessions. Disabled saved-session operations return 503. No automatic saving
of input, model output or review payloads occurs.

## Stored record and provenance

A saved session contains a server-generated UUID, original transcript, immutable
rules-generated proposals, engine=rules, rules version, schema version, UTC creation
and update times, an integer revision, and the latest complete review if any.
Initial revision is 1. Each proposal gets a stable server-generated UUID plus its
original zero-based index. Store exact evidence and genuine nulls unchanged.

The server executes the current rules engine when creating a session. It does not
accept caller-supplied proposals as authentic extraction records. This establishes
provenance within that database, not protection against direct file tampering or
proof of semantic correctness. Stateless review retains its caller-supplied
snapshot semantics. Experimental Ollama session creation is deferred; no implicit
model selection or fallback. At most 100 proposals per saved session, consistent
with review limits; reject an oversized batch with 422 and save nothing.

## Planned routes

| Route | Contract |
| --- | --- |
| POST /sessions | Transcript only, existing length/nonblank validation; run rules and atomically save session and proposal snapshots; return 201, ID, revision and snapshot. |
| GET /sessions/{id} | Return saved transcript, original proposals, metadata, current revision and latest review; unknown ID returns 404. |
| PUT /sessions/{id}/review | expected_revision plus one complete decision per original proposal index; use stored transcript/proposals with the existing review validator. Return saved review and incremented revision. |
| DELETE /sessions/{id}?expected_revision=N | Atomically delete session, proposals and latest review only if revision matches; return 204. Missing session returns 404. |

Malformed IDs or input return 422. Version mismatches return 409 with no change.
No listing/search/export route is included in the first storage step. Saving the
same transcript twice creates separate sessions; retries are not idempotent.
Do not automatically retry POST after an uncertain network response.

## Review and concurrency

Original proposals and evidence never change. Complete-batch review can replace
the latest decisions, including changing confirmed to rejected or correcting a
previous review. Each new review still references the original proposals. Reject
incomplete/duplicate/out-of-range decisions, changed evidence, blank corrections
or unsupported confirmed fields with 422 and no database changes.

Validate expected revision and commit the whole review in one transaction. The
revision check must occur under the same write transaction as replacement; two
writers using the same revision cannot both succeed. Read/validation/write
failures roll back. A stale DELETE also returns 409, preventing removal of an
unseen newer review. A short SQLite lock timeout returns 503 on contention;
other storage failures return a sanitized server error, never success with lost
changes. Use parameterized SQL, per-operation connections and foreign-key
constraints; do not keep a shared connection across API threads. Timestamps are
server observations, not trusted reviewer identity. No claim of multi-user or
production concurrency support.

## Retention, deletion and filesystem handling

Saving is explicit. Retain sessions across restarts until an explicit DELETE;
no TTL, background purge, hidden cache, automatic backup or cloud sync is built.
The user can choose an unsynced local path; the application does not control OS
backups. This policy supports synthetic/public records, not private transcripts.

Deletion removes the session and dependent records from logical database access
in one transaction. It is not guaranteed secure erasure from SQLite free pages,
filesystem snapshots, backups or exported copies. Historical review revisions
are not retained in v1: only immutable extraction originals and the latest review
survive, until deletion. Thus v1 is not a complete audit-history system.

Ignore database and SQLite sidecar files (including journal, WAL and shared-memory
files) in Git before implementation writes any local store. Tests use disposable
temporary databases, never a developer's configured database. Do not log transcript
or review bodies as part of storage operations. File permissions and explicit
configuration protect accidental handling, not an authenticated access boundary.

## Required implementation checks

- Disabled mode creates no database; invalid configuration cannot silently redirect.
- Create/read after closing and reopening connections preserves nulls, exact text,
  stable IDs and original needs_review snapshots.
- Confirm/correct/reject validates against stored source, preserves originals and
  increments revision exactly once; invalid batches do not change data.
- Two writes sharing an expected revision yield one success and one conflict;
  stale delete cannot remove newer work.
- Deletion removes dependent records; GET returns 404 afterward.
- Oversized input/batches and storage errors never leave partial records.
- Existing stateless contracts remain unchanged; no Ollama calls are introduced.
