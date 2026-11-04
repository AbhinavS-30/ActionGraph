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

Ollama generation envelopes now have a separate 1 MiB response cap. No total
request deadline or distributed limit is implemented. Saved sessions remain explicitly retained until deletion, with
no TTL/disk quota. This step does not make the service suitable for public hosting.
Next reconcile remaining local-release limits and scope; document further
policies before implementation.

## Verification — November 4, 2026

339 tests and Ruff pass. Tests cover exact boundary, fixed and streamed bodies,
misleading/missing/invalid/large Content-Length values, early disconnects, rejection
across extract/review/session routes, and normal operation after rejection.
OpenAPI declares 413 using ErrorResponse on all routes. A disposable loopback
Uvicorn process returned 413 for actual fixed-length and chunked oversized
uploads, then 200 for normal extraction; OpenAPI 413 was present. Server stopped
after checking. These observations used the implementation working tree based
on ea62b5d; they are protocol checks, not browser or extraction-quality evidence.

## Ollama generation response cap

The shared generation client now opens HTTP responses in streaming mode and
buffers at most 1 MiB (1,048,576 bytes) of the JSON envelope, including generated
text and metadata. It requests Accept-Encoding: identity and rejects non-identity
Content-Encoding before decoding to avoid unbounded decompression. HTTP status
errors still propagate without reading their body. Content-Length can reject
early, but actual stream bytes are counted regardless of missing/understated
length. An envelope exactly at the cap can proceed to ordinary JSON validation.
Oversize raises OllamaResponseError and closes the response; API maps it to 502
without raw content/partial items and releases the model slot. No truncation,
repair, retry or fallback occurs. The caller-owned HTTPX client remains open.

The cap is generous relative to the configured generated-token limits and bounds
envelope buffering; it is not a measured optimal threshold. A transport chunk,
already-preloaded mock/custom response, JSON parsing and normal object/text copies
can consume additional memory. Arbitrary caller-installed HTTPX hooks must not
read unbounded bodies before the reader; the project's evaluation capture now
uses the same bounded reader. Inventory/version probes are separate from the
generation path; no broader model-management response-size guarantee is claimed.
Oversize capture attempts remain explicit failures without partial raw bodies;
historical raw artifacts are unchanged. No override setting is exposed.

346 tests and Ruff pass, including exact boundary, streamed excess/understated
length, huge announced length, early close, compressed rejection, compatible
eval capture and API 502 followed by successful slot reuse. These use simulated
responses; no real model inference or quality remeasurement occurred. API output
response size, total wall-clock duration, disk quota and distributed limits are
still outside the implemented caps. Keep the service local.
