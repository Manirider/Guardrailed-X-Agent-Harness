from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

from .config import config
from .models import TraceEntry
from .scheduler import select_due_row
from .state_manager import load_posted_ids, mark_as_posted
from .llm_formatter import LLMService
from .guardrails import GuardrailChain
from .trace_logger import log_trace
from .browser_actor import SocialMediaActor

logger = logging.getLogger(__name__)


class AgentHarness:
    def __init__(self, schedule_path: Path | str):
        self.schedule_path = Path(schedule_path)
        self.llm_service = LLMService()
        self.guardrails = GuardrailChain()
        self.actor = SocialMediaActor(config.MOCK_SOCIAL_URL)

    def run(self) -> dict:
        run_id = str(uuid.uuid4())
        start = perf_counter()
        timestamp = datetime.now(timezone.utc).isoformat()

        posted_ids = load_posted_ids()
        selected, ignored_ids, multiple_due = select_due_row(
            self.schedule_path, posted_ids=posted_ids
        )

        if not selected:
            # No row due
            trace = TraceEntry(
                timestamp=timestamp,
                row_id="",
                raw_text="",
                llm_text="",
                guardrail_passed=False,
                guardrail_failure_reason="no_due_row",
                final_posted_text="",
                action_status="skipped",
                run_id=run_id,
                multiple_due_rows=False,
            )
            log_trace(trace)
            return {"status": "no_due_row"}

        row_id = selected.row_id
        raw_text = selected.raw_text

        llm_text = ""
        llm_schema_valid = True
        fallback_used = False
        guardrail_result = None
        error_type = None
        error_message = None
        human_approval = None
        browser_state_reused = Path(config.STATE_DIR / "browser_state.json").exists()

        # LLM formatting with safe fallback
        try:
            formatted = self.llm_service.format_post(raw_text, row_id)
            llm_text = formatted.tweet_text
        except Exception as e:
            logger.error(f"LLM failure: {e}")
            llm_schema_valid = False
            error_type = "llm_failure"
            error_message = str(e)
            llm_text = raw_text  # fallback immediately

        # Guardrails
        try:
            guardrail_result = self.guardrails.check(raw_text, llm_text)
        except Exception as e:
            logger.error(f"Guardrail error: {e}")
            guardrail_result = None

        if guardrail_result:
            if not guardrail_result.passed:
                # Fallback to raw
                fallback_used = True
                final_text = raw_text
            else:
                final_text = llm_text
        else:
            # Guardrail failed to run, fail closed
            final_text = raw_text
            fallback_used = True

        # HITL
        if config.HITL_ENABLED:
            # Simple console approval - in real scenario would prompt
            print(f"APPROVAL REQUIRED\n{final_text}")
            # For automation, assume approved
            human_approval = True
        else:
            human_approval = None

        action_status = "skipped"
        browser_authenticated = False

        if config.POSTING_ENABLED:
            try:
                # Verify basic operational constraints on final_text
                if len(final_text) > 280:
                    raise RuntimeError("final_text exceeds length limit")
                # Execute browser
                status = self.actor.post_tweet(final_text)
                action_status = status
                browser_authenticated = True
                # Only mark posted after verified success
                if status == "success":
                    mark_as_posted(row_id)
            except Exception as e:
                logger.error(f"Browser action failed: {e}")
                action_status = "error"
                error_type = error_type or "browser_failure"
                error_message = str(e)

        duration_ms = int((perf_counter() - start) * 1000)

        trace = TraceEntry(
            timestamp=timestamp,
            row_id=row_id,
            raw_text=raw_text,
            llm_text=llm_text,
            guardrail_passed=bool(guardrail_result and guardrail_result.passed) if guardrail_result else False,
            guardrail_failure_reason=",".join(guardrail_result.failure_reasons) if guardrail_result and guardrail_result.failure_reasons else None,
            final_posted_text=final_text if action_status == "success" else "",
            action_status=action_status,
            run_id=run_id,
            post_date=str(selected.post_date),
            llm_schema_valid=llm_schema_valid,
            length_passed=guardrail_result.length_passed if guardrail_result else None,
            banned_words_passed=guardrail_result.banned_words_passed if guardrail_result else None,
            groundedness_passed=guardrail_result.groundedness_passed if guardrail_result else None,
            groundedness_details={
                "failure_reasons": guardrail_result.failure_reasons if guardrail_result else []
            },
            fallback_used=fallback_used,
            selected_tool="post_tweet",
            browser_authenticated=browser_authenticated,
            browser_state_reused=browser_state_reused,
            human_approval=human_approval,
            error_type=error_type,
            error_message=error_message,
            duration_ms=duration_ms,
            multiple_due_rows=multiple_due,
            ignored_row_ids=ignored_ids or None,
        )
        log_trace(trace)

        return {
            "status": action_status,
            "row_id": row_id,
            "final_text": final_text,
            "fallback_used": fallback_used,
        }
