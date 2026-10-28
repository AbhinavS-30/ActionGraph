# Week 1: ActionGraph

October 28–November 03, 2026

## Purpose

Meeting transcript to evidence-backed action items.

## Study topics

Python functions, lists/dicts, exceptions, type hints; HTTP/JSON; Pydantic validation; precision/recall; explicit versus ambiguous commitments.

## Required MVP

Manual transcript input, structured action/owner/deadline/evidence output, exact evidence validation, local model calls, simple CLI or API, small labeled evaluation set.

## Deferred scope

Audio transcription, calendar integrations, polished dashboard, cross-meeting memory.

## Daily tasks

- **Wed Oct 28:** Set up environment, inspect schemas/tests, manually label the supplied transcript.
- **Thu Oct 29:** Implement transcript validation and JSON parsing; test empty and malformed inputs.
- **Fri Oct 30:** Call the local model with a structured schema; log failures without silently fixing results.
- **Sat Oct 31:** Implement exact evidence substring checks and null owner/deadline behavior.
- **Sun Nov 01:** Label at least ten short synthetic transcripts; compare a simple baseline with model extraction.
- **Mon Nov 02:** Add a minimal API or CLI demo; measure invalid output and extraction errors.
- **Tue Nov 03:** Publish a reproducible demo, record limitations and complete an independent change.

## Evaluation

Extraction precision/recall using a documented matching rubric; fabricated evidence count; schema validity; latency. Evaluate explicit and ambiguous items separately.

## Interview defense

Why null rather than guessing? Why does matching an evidence substring not prove the action interpretation is correct?

## Post

Show a 30–90 second demo, one design decision, one failure, measured evidence and a limitation. Optional second post: a debugging lesson. Do not claim the article's full platform scope was implemented.
