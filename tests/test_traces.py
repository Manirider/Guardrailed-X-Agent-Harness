import tempfile, json
from pathlib import Path
from src.harness.config import config
from src.harness.trace_logger import log_trace
from src.harness.models import TraceEntry


def test_trace_written():
    with tempfile.TemporaryDirectory() as td:
        config.STATE_DIR = Path(td)
        entry = TraceEntry(timestamp="2026-01-01T00:00:00Z", row_id="r1", raw_text="a", llm_text="b", guardrail_passed=True, guardrail_failure_reason=None, final_posted_text="b", action_status="success")
        log_trace(entry)
        traces_file = Path(td)/"traces.jsonl"
        lines = traces_file.read_text().strip().splitlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["row_id"] == "r1"
