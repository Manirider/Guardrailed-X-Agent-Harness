from __future__ import annotations

import json
import logging
from typing import Optional

import httpx

from .config import config
from .models import FormattedPost

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None, temperature: Optional[float] = None):
        self.base_url = base_url or config.LLM_BASE_URL
        self.model = model or config.LLM_MODEL
        self.temperature = temperature if temperature is not None else config.LLM_TEMPERATURE

    def format_post(self, raw_text: str, row_id: str) -> FormattedPost:
        prompt = f"""You are a text formatter. Transform the raw text into a tweet.

Rules:
- Preserve source facts. Do not invent information.
- Do not add links.
- Do not add handles.
- Do not add unsupported entities.
- Do not change source_row_id.
- Keep text concise.
- Do not make scheduling decisions.
- Do not perform actions.
- Return only a JSON object with fields tweet_text and source_row_id.

raw_text: {raw_text}
row_id: {row_id}
"""
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(
                    f"{self.base_url.rstrip('/')}/chat/completions",
                    json={
                        "model": self.model,
                        "temperature": self.temperature,
                        "messages": [{"role": "user", "content": prompt}],
                        "response_format": {"type": "json_object"},
                    },
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            raise

        # Extract content
        try:
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
        except Exception as e:
            logger.error(f"LLM response parsing failed: {e}")
            raise ValueError("Malformed LLM JSON")

        # Validate structure
        try:
            fp = FormattedPost(**parsed)
        except Exception as e:
            logger.error(f"Pydantic validation failed: {e}")
            raise

        if fp.source_row_id != row_id:
            raise ValueError(f"source_row_id mismatch: expected {row_id}, got {fp.source_row_id}")

        return fp
