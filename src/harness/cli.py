from __future__ import annotations

import logging
from pathlib import Path

from .config import config
from .agent import AgentHarness

logging.basicConfig(level=config.LOG_LEVEL)


def main():
    schedule_path = Path("data/schedule.csv")
    if not schedule_path.exists():
        schedule_path = Path("schedule.csv")
    harness = AgentHarness(schedule_path)
    result = harness.run()
    print(result)


if __name__ == "__main__":
    main()
