# ActionGraph: local project instructions

Work exclusively on ActionGraph. Read README.md, docs/WEEK-01.md and docs/DAY-01.md first. This is a meeting transcript to structured action-item application. Output fields: action, owner (nullable), deadline (nullable), exact evidence and review status.

Current starter: app/main.py health endpoint, app/schemas.py output contract, tests/test_contract.py, data/synthetic/meeting-01.txt. Extraction is not implemented. Never claim it is.

User is learning. Explain the problem and data flow, then examine the sample transcript together. Ask one question and wait. Teach one concept, give a miniature example and a different independent exercise; offer hints before solutions. Next exercise is validate_transcript(text): reject non-string/blank input and return trimmed text. Do not implement the extraction pipeline until requested.

Weekdays are project learning and building; interview preparation is weekends only. First demo target November 3, 2026. Budget $0 added services. Use Python 3.12, FastAPI/Pydantic/pytest and local Ollama llama3.2:3b. No paid API calls. Use synthetic/public data only. Never invent measurements.

This is a standalone ActionGraph repository. Use .venv/bin/python -m pytest and .venv/bin/python -m uvicorn app.main:app --reload from this folder. Stage only intended files. GitHub remote setup is being verified; inspect git remote -v for actual state.

End sessions with completed work, checks, independent understanding, remaining gaps and next task. Update docs/STATUS.md when work occurs.
