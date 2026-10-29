# ActionGraph project instructions

Work exclusively in this standalone ActionGraph repository. Read README.md, docs/STATUS.md, docs/ROADMAP.md, and docs/VALIDATION.md before making changes. Supporting documentation covers project status, delivery roadmap, and validation design.

## Product and constraints

Meeting transcripts become structured action items with action, nullable owner, nullable deadline, exact evidence, and review status. Standalone validation, parsing, and evidence helpers exist; extraction is not implemented. Never claim otherwise or invent measurements.

Use Python 3.12, FastAPI, Pydantic, pytest, and local Ollama llama3.2:3b. No paid API calls, new services, large downloads, or unnecessary dependencies. Explain dependencies before adding them. Use synthetic/public data only. Keep secrets, model weights, virtual environments, and private information out of Git.

Initial demo target: November 3, 2026. Defer audio, calendar integration, elaborate dashboards, and other projects. Schema validity and exact evidence matching do not prove extraction correctness. Define ambiguity and relative-date rules before implementing them.

## Collaboration

Work in small reviewable steps. Explain purpose, data flow, important syntax, and failure behavior. Implement agreed changes, explain the result, and ask one focused understanding question at a time. Offer hints for independent exercises. Do not implement future phases without user authorization. Keep personal learning history in the conversation, not repository documentation.

## Checks and delivery

Run `.venv/bin/python -m pytest` and `.venv/bin/python -m ruff check app tests` from this folder. Run the API with `.venv/bin/python -m uvicorn app.main:app --reload`.

Update docs/STATUS.md with factual capabilities, checks, limitations, and next task when work occurs. Inspect git remote -v for the actual destination. Review changes and stage only intended files. Commit and push completed tested work when requested or at the end of a daily session; never create artificial activity. Do not publish posts automatically.
