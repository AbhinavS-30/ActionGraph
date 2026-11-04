# Local resource limits

The local API caps raw HTTP request bodies at **2 MiB (2,097,152 bytes)** before
FastAPI parses JSON or invokes dependencies/routes. The cap applies to all HTTP
methods/routes. HTTP 413 returns a JSON string detail and no endpoint work runs.
A body exactly at the cap is admitted to ordinary validation; this does not mean
its JSON or fields are valid. Content-Length is only an early-rejection hint;
actual bytes are counted, including streamed requests without that header and
understated sizes. Under-limit bytes are replayed unchanged to FastAPI.

The middleware retains at most the permitted body bytes before parsing, plus
normal copying/transport overhead. It does not bound memory already allocated by
the ASGI server or an incoming chunk, total concurrent connections, upload time,
JSON complexity, decompression, application response size or SQLite file growth.
The application does not add request decompression. Keep the API on loopback.

The 2 MiB limit accommodates transcript-only requests (including escaped Unicode)
and ordinary review batches while bounding pre-parse request buffering. It is a
local product policy, not a measured optimal threshold. Maximum schema item count
does not guarantee every possible batch fits the byte cap: repeated evidence and
replacement strings contribute to the total. A review still needs all decisions;
do not split one session's decisions into incomplete review requests to bypass
this requirement. Shorten a stateless submitted batch when appropriate; saved
session review retains original source requirements. No cap override is exposed.

Other implemented limits:

| Boundary | Current limit |
| --- | --- |
| Transcript | 12,000 original Python characters; invalid input returns 422 |
| Review/saved proposals | Up to 100 per submitted review/saved session |
| Model generation | num_predict default 1024, allowed 1–4096; length-truncated output rejected |
| Model network operation | HTTPX timeout default 60 seconds, configured at most 120; not total duration |
| API model concurrency | One active Ollama extraction per process; busy returns 503 with Retry-After |
| SQLite write lock | One-second timeout in API store; busy returns 503 |

No total request deadline, upstream Ollama response-byte cap or distributed limit
is implemented. Saved sessions remain explicitly retained until deletion, with
no TTL/disk quota. This step does not make the service suitable for public hosting.
Next bound upstream response buffering and reconcile remaining local-release
limits; document further policies before implementation.

## Verification — November 4, 2026

339 tests and Ruff pass. Tests cover exact boundary, fixed and streamed bodies,
misleading/missing/invalid/large Content-Length values, early disconnects, rejection
across extract/review/session routes, and normal operation after rejection.
OpenAPI declares 413 using ErrorResponse on all routes. A disposable loopback
Uvicorn process returned 413 for actual fixed-length and chunked oversized
uploads, then 200 for normal extraction; OpenAPI 413 was present. Server stopped
after checking. These observations used the implementation working tree based
on ea62b5d; they are protocol checks, not browser or extraction-quality evidence.
