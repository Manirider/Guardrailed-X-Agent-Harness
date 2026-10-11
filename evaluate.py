from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict

TRACES_PATH = Path("traces.jsonl")
METRICS_PATH = Path("metrics.json")


def load_traces() -> List[Dict]:
    if not TRACES_PATH.exists():
        return []
    traces = []
    with TRACES_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            traces.append(json.loads(line))
    return traces


def compute_metrics(traces: List[Dict]) -> Dict:
    # Filter traces where row_id present (attempted processing)
    attempted = [t for t in traces if t.get("row_id")]
    # Successful posts: distinct row_ids with at least one success
    successful_row_ids = {t["row_id"] for t in attempted if t.get("action_status") == "success"}
    # Rows due: distinct row_ids attempted
    rows_due = len(set(t["row_id"] for t in attempted))

    # Task completion rate = successful posts / rows due
    tcr = len(successful_row_ids) / rows_due if rows_due else 0.0

    # Groundedness score = LLM outputs passing groundedness / LLM outputs evaluated
    llm_evaluated = [t for t in attempted if t.get("llm_schema_valid") is not None]
    grounded_pass = [t for t in llm_evaluated if t.get("groundedness_passed") is True]
    groundedness_score = len(grounded_pass) / len(llm_evaluated) if llm_evaluated else 0.0

    # Guardrail trigger rate = runs where any guardrail failed / runs evaluated
    guardrail_runs = [t for t in attempted if t.get("guardrail_passed") is not None]
    guardrail_failed = [t for t in guardrail_runs if t.get("guardrail_passed") is False]
    guardrail_trigger_rate = len(guardrail_failed) / len(guardrail_runs) if guardrail_runs else 0.0

    metrics = {
        "task_completion_rate": round(tcr, 6),
        "groundedness_score": round(groundedness_score, 6),
        "guardrail_trigger_rate": round(guardrail_trigger_rate, 6),
    }
    return metrics


def main():
    traces = load_traces()
    metrics = compute_metrics(traces)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
