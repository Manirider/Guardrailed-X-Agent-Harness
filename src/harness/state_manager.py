from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Set

from .config import config


def _posted_ids_path() -> Path:
    return config.STATE_DIR / "posted_ids.json"


def _ensure_initialized() -> None:
    config.ensure_state_dir()
    if not _posted_ids_path().exists():
        _atomic_write([])


def _atomic_write(data: list[str]) -> None:
    tmp = tempfile.NamedTemporaryFile("w", delete=False, dir=config.STATE_DIR, encoding="utf-8")
    try:
        json.dump(data, tmp, indent=2)
        tmp.flush()
        tmp.close()
        Path(tmp.name).replace(_posted_ids_path())
    finally:
        try:
            Path(tmp.name).unlink(missing_ok=True)
        except Exception:
            pass


def load_posted_ids() -> Set[str]:
    _ensure_initialized()
    try:
        content = _posted_ids_path().read_text(encoding="utf-8")
        data = json.loads(content)
        if not isinstance(data, list):
            raise ValueError("posted_ids.json must contain a list")
        return set(str(x) for x in data)
    except (json.JSONDecodeError, ValueError, FileNotFoundError):
        # Corruption detection: reset to empty
        _atomic_write([])
        return set()


def mark_as_posted(row_id: str) -> None:
    posted = load_posted_ids()
    if row_id in posted:
        return
    posted.add(row_id)
    _atomic_write(sorted(posted))


def is_posted(row_id: str) -> bool:
    return row_id in load_posted_ids()
