from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import config
from .models import TraceEntry


def log_trace(entry: TraceEntry | dict[str, Any]) -> None:
    config.ensure_state_dir()
    traces_file_root = Path("traces.jsonl")
    traces_file_data = config.STATE_DIR / "traces.jsonl"
    if isinstance(entry, TraceEntry):
        data = entry.model_dump(exclude_none=True)
    else:
        data = entry

    # Ensure timestamp
    if "timestamp" not in data:
        data["timestamp"] = datetime.now(timezone.utc).isoformat()

    line = json.dumps(data, ensure_ascii=False)
    # Atomic append to both root and data directory for compatibility
    for tf in [traces_file_root, traces_file_data]:
        # Ensure parent directory exists
        tf.parent.mkdir(parents=True, exist_ok=True)
        with tf.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
