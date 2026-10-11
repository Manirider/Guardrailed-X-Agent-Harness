import tempfile
from pathlib import Path

from src.harness.config import config
from src.harness.state_manager import load_posted_ids, mark_as_posted


def test_load_empty():
    with tempfile.TemporaryDirectory() as td:
        config.STATE_DIR = Path(td)
        ids = load_posted_ids()
        assert ids == set()


def test_mark_and_load():
    with tempfile.TemporaryDirectory() as td:
        config.STATE_DIR = Path(td)
        mark_as_posted("r1")
        mark_as_posted("r1")
        ids = load_posted_ids()
        assert ids == {"r1"}
