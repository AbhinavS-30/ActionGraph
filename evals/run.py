"""Collect synthetic evaluation attempts without automatically judging meaning."""

import argparse
import hashlib
import json
import platform
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

import httpx

from app.extraction import extract_actions
from app.prompts import EXTRACTION_INSTRUCTIONS
from evals.baseline import extract_baseline


def collect_attempt(case, system, operation):
    """Keep failures explicit and separate from successful empty results."""
    started = perf_counter()
    record = {"case_id": case["id"], "system": system}
    try:
        record["result"] = operation(case["transcript"]).model_dump()
        record["status"] = "success"
    except (httpx.HTTPError, ValueError, TypeError) as exc:
        # Retain expected transport/validation failures; programming errors stop.
        record.update(status="failure", error_type=type(exc).__name__, error=str(exc))
    record["duration_seconds"] = perf_counter() - started
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--baseline-only", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    dataset = (root / "evals/cases.json").read_bytes()
    cases = json.loads(dataset)

    def git(*arguments):
        return subprocess.check_output(["git", *arguments], cwd=root, text=True).strip()

    metadata = {
        "started_utc": datetime.now(UTC).isoformat(),
        "commit": git("rev-parse", "HEAD"),
        "working_tree_dirty": bool(git("status", "--porcelain")),
        "dataset_sha256": hashlib.sha256(dataset).hexdigest(),
        "instructions_sha256": hashlib.sha256(
            EXTRACTION_INSTRUCTIONS.encode()
        ).hexdigest(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python": platform.python_version(),
        "model": "llama3.2:3b",
        "generation_settings": "Ollama defaults; JSON schema format; stream=false",
        "model_initial_state": "unknown; no warmup request performed",
        "timeout_seconds_per_operation": 60,
    }

    # Exclusive creation prevents accidentally replacing an earlier run.
    with args.output.open("x", encoding="utf-8") as output:

        def write(record):
            output.write(json.dumps(record, ensure_ascii=False) + "\n")
            output.flush()

        with httpx.Client(base_url="http://127.0.0.1:11434", timeout=60.0) as client:
            if not args.baseline_only:
                for endpoint, key in [
                    ("/api/version", "ollama_version"),
                    ("/api/tags", "model_inventory"),
                ]:
                    try:
                        response = client.get(endpoint)
                        response.raise_for_status()
                        metadata[key] = response.json()
                    except (httpx.HTTPError, ValueError) as exc:
                        metadata[key] = {
                            "error_type": type(exc).__name__,
                            "error": str(exc),
                        }
            write({"type": "metadata", **metadata})

            raw_responses = []

            def capture(response):
                response.read()
                raw_responses.append(
                    {"http_status": response.status_code, "body": response.text}
                )

            client.event_hooks["response"] = [capture]
            for case in cases:
                write(collect_attempt(case, "baseline", extract_baseline))
                if args.baseline_only:
                    continue
                raw_responses.clear()
                record = collect_attempt(
                    case,
                    "ollama",
                    lambda transcript: extract_actions(transcript, client=client),
                )
                record["raw_responses"] = list(raw_responses)
                write(record)
                print(f"{case['id']}: {record['status']}", flush=True)


if __name__ == "__main__":
    main()
