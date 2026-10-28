# ActionGraph

A learning project that converts meeting transcripts into structured, evidence-backed action items.

## Current state

Day 1 scaffold: health endpoint, output schema, synthetic transcript, and three contract tests. LLM extraction is not implemented.

## Setup

Python 3.12 is used.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock.txt
python -m pytest
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs. Local model: Ollama llama3.2:3b. No paid API is needed.

## Learning documents

- [Week 1](docs/WEEK-01.md)
- [Day 1](docs/DAY-01.md)
- [Status](docs/STATUS.md)

Code is in app/, tests in tests/, synthetic inputs in data/synthetic/, and evaluations in evals/.

Weekdays focus on building and learning; interview practice is reserved for weekends.
