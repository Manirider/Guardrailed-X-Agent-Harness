from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


class ScheduledPost(BaseModel):
    row_id: str
    post_date: date
    raw_text: str

    @field_validator("raw_text")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("raw_text must not be empty")
        return v.strip()


class FormattedPost(BaseModel):
    model_config = ConfigDict(extra='forbid')
    tweet_text: str
    source_row_id: str

    @field_validator("tweet_text")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("tweet_text must not be empty")
        return v.strip()


class GuardrailResult(BaseModel):
    passed: bool
    length_passed: bool
    banned_words_passed: bool
    groundedness_passed: bool
    failure_reasons: List[str] = Field(default_factory=list)


class TraceEntry(BaseModel):
    timestamp: str
    row_id: str
    raw_text: str
    llm_text: str
    guardrail_passed: bool
    guardrail_failure_reason: Optional[str]
    final_posted_text: str
    action_status: str

    # Optional extended fields
    run_id: Optional[str] = None
    post_date: Optional[str] = None
    llm_schema_valid: Optional[bool] = None
    length_passed: Optional[bool] = None
    banned_words_passed: Optional[bool] = None
    groundedness_passed: Optional[bool] = None
    groundedness_details: Optional[dict] = None
    fallback_used: Optional[bool] = None
    selected_tool: Optional[str] = None
    browser_authenticated: Optional[bool] = None
    browser_state_reused: Optional[bool] = None
    human_approval: Optional[bool] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    multiple_due_rows: Optional[bool] = None
    ignored_row_ids: Optional[List[str]] = None
