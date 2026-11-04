# Saved-session Swagger verification — completed November 4, 2026

Use only synthetic text and a disposable database. The user executed this
procedure through Swagger and supplied screenshots reviewed in the conversation.
Browser automation remained unavailable; this was user-assisted verification.

## Start an isolated demo server

Run from the repository root in a separate terminal. Port 8001 avoids changing
an existing server on 8000. mktemp creates a new test directory; no existing
session database is used.

```bash
actiongraph_demo_dir=$(mktemp -d /tmp/actiongraph-swagger.XXXXXX)
export ACTIONGRAPH_DB_PATH="$actiongraph_demo_dir/sessions.sqlite3"
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Open http://127.0.0.1:8001/docs. Confirm Swagger renders all saved-session routes.
Use Try it out and Execute for each operation below. Read Server response,
not just the static Responses documentation.

1. POST /sessions with:

   ```json
   {"transcript":"Maya: I will review the report tomorrow."}
   ```

   Expect actual 201, revision=1, persisted=true, one proposal with stable UUID,
   owner Maya, deadline tomorrow, exact evidence and needs_review. Copy session id.
2. GET /sessions/{session_id} using that ID. Expect 200 and the same proposal.
3. PUT /sessions/{session_id}/review with:

   ```json
   {"expected_revision":1,"decisions":[{"proposal_index":0,"decision":"confirm"}]}
   ```

   Expect 200, revision=2, original proposal still needs_review, and separate
   latest_review entry with reviewed.review_status=confirmed.
4. Execute the same review body again. Expect 409 and no revision change.
   GET should still return revision=2 and the same review.
5. In the terminal stop this demo server with Ctrl-C, then start the same command
   again in that terminal (same exported path). GET the same ID through Swagger.
   Expect the saved revision=2 and identical original/review values.
6. DELETE this disposable session with expected_revision=1: expect 409. Repeat
   with expected_revision=2: expect 204. GET afterward: expect 404.
7. POST /sessions with a blank transcript: expect 422. Save no real meeting text.

Record source commit, actual statuses and what was visibly verified. A screenshot
of executed Server response can document the result; do not reuse older screenshots.
Stop the temporary demo server with Ctrl-C when done. Unset ACTIONGRAPH_DB_PATH
in that terminal when finished. This does not delete the temporary database file;
logical deletion above is not secure filesystem erasure.

## Observed results

Application implementation: 252c776; verification started at documentation source
9a1db54. Isolated server on port 8001, synthetic Maya report task. User screenshots
showed actual Server response results, not only static endpoint documentation:

| Operation | Observed |
| --- | --- |
| POST /sessions | 201, revision=1, rules v4 and needs_review proposal |
| PUT review expected_revision=1 | 200, revision=2 |
| Repeat same PUT | 409 with revision-change message |
| GET saved session | 200; original needs_review, reviewed confirmed, persisted=true |
| GET after agent-controlled restart on same database | 200; original/review/persisted fields preserved; agent TCP comparison also verified full response and revision=2 unchanged |
| DELETE expected_revision=1 | 409 |
| DELETE expected_revision=2 | 204, no body |
| GET deleted ID | 404, Saved session not found |
| POST blank transcript | 422, Transcript must not be blank |

The test session was deleted through the API; the isolated server was then
stopped. Database file cleanup/secure erasure was not performed. The normal
port-8000 server was untouched. Screenshots remain in the conversation; they
were not copied into the public repository. These are workflow smoke checks, not
semantic extraction evaluation. Screenshot scope does not establish every field
on every response; conclusions combine the explicitly stated browser observations
with the separately identified TCP restart comparison.

Swagger displayed 409/404 as Undocumented Error because custom error responses
are not declared in OpenAPI yet. Runtime statuses are correct; documenting those
responses is a remaining API usability task. This check does not establish full
production readiness, independent quality adjudication or completed presentation.
