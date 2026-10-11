from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class Config:
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://mock-llm:8000/v1")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MOCK_SOCIAL_URL: str = os.getenv("MOCK_SOCIAL_URL", "http://mock_social:8080")
    MOCK_USERNAME: str = os.getenv("MOCK_USERNAME", "test_user")
    MOCK_PASSWORD: str = os.getenv("MOCK_PASSWORD", "test_password")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "mock-model")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0"))
    TIMEZONE: str = os.getenv("TIMEZONE", "UTC")
    HITL_ENABLED: bool = os.getenv("HITL_ENABLED", "false").lower() == "true"
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"
    POSTING_ENABLED: bool = os.getenv("POSTING_ENABLED", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    STATE_DIR: Path = Path(os.getenv("STATE_DIR", "./data"))

    @classmethod
    def ensure_state_dir(cls) -> None:
        cls.STATE_DIR.mkdir(parents=True, exist_ok=True)


config = Config()
