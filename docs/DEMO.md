# Local demonstration

This demonstration shows the local text API, evidence-backed proposed items,
input rejection, and the review boundary. It is not a claim of production
readiness or extraction accuracy on real meetings. Use synthetic/public text only.
The public project page and video recording are not yet created.

## Start

From the repository root, ensure local Ollama is running with `llama3.2:3b`
already installed. The application never downloads a model automatically.

```bash
.venv/bin/python -m uvicorn app.main:app --reload
```

Use one worker. Open <http://127.0.0.1:8000/docs>. The default Swagger interface
loads assets from its configured CDN, so browser asset access may be required.
Keep the service on loopback; the intended public release is a project page and
recorded local demo, not a publicly exposed inference endpoint.

## Demonstration sequence

1. Expand `GET /health`, choose **Try it out**, then **Execute**. Explain that
   the response reports application capabilities, not model readiness.
2. Expand `POST /extract`, choose **Try it out**, and submit:

   ```json
   {"transcript": "Maya: I will send the report tomorrow."}
   ```

3. Inspect the returned item: task, owner, original relative deadline, exact
   evidence, and `needs_review`. Explain why the application preserves
   "tomorrow" and does not infer a calendar date.
4. Submit a blank transcript:

   ```json
   {"transcript": "   "}
   ```

   Expect HTTP 422, without inference. Correct it rather than retrying unchanged.
5. Explain that valid structure and quote presence cannot prove commitment
   interpretation or completeness. Show an evaluation failure from the recorded
   reports, including the baseline comparison. Do not present a successful
   example as representative accuracy or omit failures from claimed metrics.

Model output varies. If inference returns 502, explain the validation failure
and retain the result; do not silently substitute a saved response or retry until
the result looks good. A saved example must be labeled as recorded, not live.
503 means the model/service is unavailable or another extraction is active;
504 means an Ollama operation timed out. Consult README for limits and settings.

## Command-line equivalent

```bash
curl -X POST http://127.0.0.1:8000/extract \
  -H 'Content-Type: application/json' \
  -d '{"transcript":"Maya: I will send the report tomorrow."}'
```

## Observed verification — November 2, 2026

Source `837533d`, actual Uvicorn reload server on `127.0.0.1:8000`, real local
Ollama; requests sent over TCP with HTTPX, not the in-process test transport:

| Request | Observed result |
| --- | --- |
| `GET /health` | HTTP 200; extraction function and API available |
| `GET /docs` | HTTP 200; Swagger UI markup served |
| `GET /openapi.json` | HTTP 200; POST extraction success references ExtractionResult |
| Blank transcript | HTTP 422 with transcript-blank validation message |
| Synthetic commitment above | HTTP 200 with Send the report / Maya / tomorrow / exact sentence / needs_review |

Automated browser access was unavailable and native browser control timed out.
The user subsequently executed both requests through Swagger **Try it out** and
provided screenshots reviewed in the conversation on November 2. They confirm
visual rendering, HTTP 200 for the synthetic commitment with the expected fields,
and HTTP 422 with "Transcript must not be blank" for whitespace input. This is
user-executed browser verification, separate from the earlier automated TCP check.
No video has been recorded. These observations are smoke tests, not quality or
latency evaluation.
