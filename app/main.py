"""Health endpoint for ActionGraph; extraction is not yet implemented."""

from fastapi import FastAPI

app = FastAPI(title="ActionGraph", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "extraction": "not_implemented"}
