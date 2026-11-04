# Saved-session Swagger verification — pending

Use only synthetic text and a disposable database. This procedure is not a record
of a completed browser check. The current automation connection is unavailable.

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
