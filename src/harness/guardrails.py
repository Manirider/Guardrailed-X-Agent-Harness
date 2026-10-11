from __future__ import annotations

import re
from typing import List, Set

from .models import GuardrailResult


BANNED_WORDS_DEFAULT = {"guarantee", "investment"}
URL_RE = re.compile(r"https?://[^\s]+", re.IGNORECASE)
MENTION_RE = re.compile(r"@[A-Za-z0-9_]+")

def _extract_entities(text: str) -> tuple[Set[str], Set[str]]:
    urls = set(URL_RE.findall(text))
    mentions = set(MENTION_RE.findall(text))
    return urls, mentions


class GuardrailChain:
    def __init__(self, banned_words: Set[str] | None = None):
        self.banned_words = banned_words or BANNED_WORDS_DEFAULT

    def check(self, source_text: str, candidate_text: str) -> GuardrailResult:
        failures: List[str] = []

        # Length
        length_ok = len(candidate_text) <= 280
        if not length_ok:
            failures.append(f"length:{len(candidate_text)}")

        # Banned words
        lowered = candidate_text.lower()
        found_banned = []
        for w in self.banned_words:
            # token-aware simple check
            if re.search(rf"\b{re.escape(w)}\b", lowered):
                found_banned.append(w)
        banned_ok = len(found_banned) == 0
        if not banned_ok:
            failures.extend([f"banned_word:{w}" for w in found_banned])

        # Groundedness
        src_urls, src_mentions = _extract_entities(source_text)
        cand_urls, cand_mentions = _extract_entities(candidate_text)

        # Introduced URLs / mentions not in source
        introduced_urls = cand_urls - src_urls
        introduced_mentions = cand_mentions - src_mentions

        grounded_ok = len(introduced_urls) == 0 and len(introduced_mentions) == 0
        if not grounded_ok:
            if introduced_urls:
                failures.append("introduced_url")
            if introduced_mentions:
                failures.append("introduced_mention")

        passed = length_ok and banned_ok and grounded_ok
        return GuardrailResult(
            passed=passed,
            length_passed=length_ok,
            banned_words_passed=banned_ok,
            groundedness_passed=grounded_ok,
            failure_reasons=failures,
        )
