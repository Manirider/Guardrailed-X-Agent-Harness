import json, tempfile
from pathlib import Path
from evaluate import compute_metrics


def test_metrics():
    traces = [
        {"row_id":"r1","action_status":"success","llm_schema_valid":True,"groundedness_passed":True,"guardrail_passed":True},
        {"row_id":"r2","action_status":"error","llm_schema_valid":True,"groundedness_passed":False,"guardrail_passed":False},
    ]
    m = compute_metrics(traces)
    assert m["task_completion_rate"] == 0.5
    assert m["groundedness_score"] == 0.5
    assert m["guardrail_trigger_rate"] == 0.5
