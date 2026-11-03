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

from app.config import get_settings
from app.extraction import extract_actions
from app.prompts import EXTRACTION_INSTRUCTIONS
from app.rules import extract_rule_actions
from evals.baseline import extract_baseline
from evals.concise import CONCISE_INSTRUCTIONS, extract_concise_actions
from evals.decisions import (
    DECISION_INSTRUCTIONS,
    FIELD_INSTRUCTIONS,
    extract_decided_actions,
)
from evals.list_contract import LIST_INSTRUCTIONS, extract_list_actions


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
    parser.add_argument(
        "--dataset",
        choices=["development", "validation", "rules-validation"],
        default="development",
    )
    parser.add_argument(
        "--contract",
        choices=["public", "lists", "decisions", "concise", "rules"],
        default="public",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    dataset_name = {
        "development": "cases.json",
        "validation": "validation-cases.json",
        "rules-validation": "rules-validation-v1.json",
    }[args.dataset]
    dataset = (root / "evals" / dataset_name).read_bytes()
    cases = json.loads(dataset)
    settings = get_settings()
    variants = {
        "public": (EXTRACTION_INSTRUCTIONS, extract_actions, "ollama"),
        "rules": (
            "Deterministic rules grammar v1; source commit records implementation.",
            lambda transcript, **_: extract_rule_actions(transcript),
            "rules",
        ),
        "concise": (CONCISE_INSTRUCTIONS, extract_concise_actions, "ollama_concise"),
        "lists": (LIST_INSTRUCTIONS, extract_list_actions, "ollama_lists"),
        "decisions": (
            DECISION_INSTRUCTIONS + FIELD_INSTRUCTIONS,
            extract_decided_actions,
            "ollama_decisions",
        ),
    }
    instructions, extractor, system = variants[args.contract]
    model_used = args.contract != "rules" and not args.baseline_only

    def git(*arguments):
        return subprocess.check_output(["git", *arguments], cwd=root, text=True).strip()

    metadata = {
        "started_utc": datetime.now(UTC).isoformat(),
        "commit": git("rev-parse", "HEAD"),
        "working_tree_dirty": bool(git("status", "--porcelain")),
        "dataset_sha256": hashlib.sha256(dataset).hexdigest(),
        "dataset_name": dataset_name,
        "instructions_sha256": hashlib.sha256(instructions.encode()).hexdigest(),
        "generation_contract": args.contract,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python": platform.python_version(),
        "model": settings.ollama_model if model_used else None,
        "model_used": model_used,
        "generation_settings": {
            "num_predict": settings.ollama_num_predict,
            "other_options": "Ollama defaults; schema format; stream=false",
        }
        if model_used
        else None,
        "runtime_settings": settings.model_dump(),
        "model_initial_state": "unknown; no warmup request performed"
        if model_used
        else "not applicable",
        "timeout_seconds_per_operation": settings.ollama_timeout_seconds,
    }

    # Exclusive creation prevents accidentally replacing an earlier run.
    with args.output.open("x", encoding="utf-8") as output:

        def write(record):
            output.write(json.dumps(record, ensure_ascii=False) + "\n")
            output.flush()

        with httpx.Client(
            base_url=settings.ollama_base_url,
            timeout=settings.ollama_timeout_seconds,
            trust_env=False,
        ) as client:
            if model_used:
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
                    system,
                    lambda transcript: extractor(
                        transcript, client=client, settings=settings
                    ),
                )
                record["raw_responses"] = list(raw_responses)
                write(record)
                print(f"{case['id']}: {record['status']}", flush=True)


if __name__ == "__main__":
    main()
