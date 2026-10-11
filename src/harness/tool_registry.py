from __future__ import annotations

from typing import Set


class ToolRegistry:
    ALLOWED_TOOLS: Set[str] = {"login", "read_csv", "post_tweet"}

    @classmethod
    def is_allowed(cls, tool_name: str) -> bool:
        return tool_name in cls.ALLOWED_TOOLS

    @classmethod
    def list_tools(cls) -> Set[str]:
        return set(cls.ALLOWED_TOOLS)
