"""Run labelled provider-stub scenarios; not a live-model quality benchmark."""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import get_settings
from app.demo import CORPUS_ID, FIXTURES, documents
from app.main import app
from app.rag.engine import _SYSTEM_PROMPT


def evaluate() -> dict:
    if not get_settings().demo_mode:
        raise RuntimeError("Evaluation requires DEMO_MODE=true; no live provider calls are allowed.")
    cases = json.loads((FIXTURES / "evaluation-cases.json").read_text())
    results = []
    with TestClient(app) as client:
        for case in cases:
            response = client.post("/query", json={"question": case["question"], "top_k": 3})
            body = response.json()
            ids = [source["chunk_id"] for source in body.get("sources", [])]
            checks = {
                "http_ok": response.status_code == 200,
                "fixture_label": body.get("response_mode") == "fixture",
                "status_match": body.get("status") == case["status"],
                "citation_match": ids == case["citations"],
                "answer_content": all(text in body.get("answer", "") for text in case["contains"]),
            }
            results.append({"id": case["id"], "question": case["question"],
                            "expected_status": case["status"], "actual_status": body.get("status"),
                            "expected_citations": case["citations"], "actual_citations": ids,
                            "checks": checks, "passed": all(checks.values())})
    return {
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "corpus_id": CORPUS_ID,
        "corpus_sha256": hashlib.sha256(json.dumps(documents(), sort_keys=True).encode()).hexdigest(),
        "fixture_sha256": hashlib.sha256((FIXTURES / "answers.json").read_bytes()).hexdigest(),
        "prompt_sha256": hashlib.sha256(_SYSTEM_PROMPT.encode()).hexdigest(),
        "provider": "author-written exact-match stub", "model": None,
        "configuration": {"demo_mode": True, "embedding": "sha256-word-count-256-v1",
                          "vector_store": "Chroma ephemeral cosine", "top_k": 3},
        "versions": {name: version(name) for name in ["fastapi", "pydantic", "chromadb"]},
        "limitations": [
            "Expected scenarios and provider answers are authored fixtures, not independent model predictions.",
            "This checks retrieval, API shape, citation filtering and abstention plumbing; it does not measure AI accuracy.",
            "The stub abstains on paraphrases. Its injection case is not evidence of live-model injection resistance.",
            "Valid citation IDs do not prove that an answer is entailed by its sources.",
        ],
        "passed": sum(result["passed"] for result in results), "total": len(results),
        "results": results,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("../outputs/evaluation.json"))
    args = parser.parse_args()
    report = evaluate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(0 if report["passed"] == report["total"] else 1)
