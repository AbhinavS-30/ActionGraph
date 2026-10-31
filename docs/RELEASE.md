# Release readiness

The current application is a local text extraction prototype with tested API
failure handling and an initial synthetic evaluation. It is not a production
service. The November 3, 2026 target is an initial demonstration, not a guaranteed
production deployment date.

## Local demonstration release

- Review provisional semantic scores and record any adjudication changes.
- Investigate refusals, unanswered requests, suggestions, missing dependencies,
  missing items, string-null fields, and incomplete evidence support observed in
  the first run. Preserve unsuccessful experiments as well as improvements.
- Evaluate agreed changes with repeated development runs and new untouched cases;
  report counts, failures, and timing limitations without generalizing tiny samples.
- Finish bounded input/output validation, explicit runtime configuration, and
  tests for resource limits appropriate to the local demo.
- Run automated checks in CI, verify installation from pinned dependencies, and
  verify the actual Uvicorn and interactive API workflow.
- Prepare a versioned release with setup instructions, a synthetic demonstration,
  reproducible evaluation artifacts, architecture, and disclosed limitations.

## Public deployment decision

A project page or recorded demonstration can describe a local application without
making local Ollama reachable by visitors. A live extraction service needs an
approved host for both FastAPI and model compute; a hosted API cannot reach a
developer's `127.0.0.1`. Hosting, hardware, operating cost, and availability have
not been selected or validated.

Before exposing live inference, define the intended users and synthetic/public
data boundary, access control, TLS, request size limits, concurrency limits,
overload behavior, generation limits, readiness checks, privacy-conscious
operational logging, deployment configuration, monitoring, and rollback. Test
those controls and the deployed end-to-end path. No claim of production readiness
or public service availability should precede those checks.

## Public communication

An engineering portfolio release should state what was built, how it was tested,
what was measured, where it fails, and how to reproduce it. Distinguish a project
page, recorded local demo, and live inference deployment. Do not claim users,
production operation, broad accuracy, or speedups without evidence. A LinkedIn
draft may be prepared after the release artifacts are verified; publishing
requires the user's explicit instruction.
