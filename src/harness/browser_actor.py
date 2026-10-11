from __future__ import annotations

import logging
from pathlib import Path

from .config import config

logger = logging.getLogger(__name__)


def _browser_state_path() -> Path:
    return config.STATE_DIR / "browser_state.json"


class SocialMediaActor:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.headless = config.HEADLESS
        self.username = config.MOCK_USERNAME
        self.password = config.MOCK_PASSWORD

    def post_tweet(self, text: str) -> str:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
        state_path = _browser_state_path()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(storage_state=str(state_path) if state_path.exists() else None)
            page = context.new_page()

            try:
                if state_path.exists():
                    # Try direct navigation, assume authenticated
                    page.goto(f"{self.base_url}/compose/tweet", wait_until="domcontentloaded", timeout=15000)
                    # Verify auth by checking for tweet textarea
                    try:
                        page.wait_for_selector("#tweet-text", timeout=5000)
                    except PlaywrightTimeoutError:
                        logger.warning("Auth state invalid, re-login")
                        self._login(page)
                else:
                    self._login(page)

                # Navigate to compose
                page.goto(f"{self.base_url}/compose/tweet", wait_until="domcontentloaded", timeout=15000)
                page.wait_for_selector("#tweet-text", timeout=10000)

                page.fill("#tweet-text", text)
                page.click("#post-btn")

                # Wait for success indicator
                # Mock server shows #post-success
                try:
                    page.wait_for_selector("#post-success", timeout=10000)
                except PlaywrightTimeoutError:
                    raise RuntimeError("Post success indicator not found")

                # Verify posted text
                posted_text_elem = page.query_selector("#posted-text")
                posted_text = posted_text_elem.inner_text().strip() if posted_text_elem else ""
                if posted_text != text:
                    raise RuntimeError(f"Posted text mismatch: expected {text!r}, got {posted_text!r}")

                # Save state
                context.storage_state(path=str(state_path))
                return "success"
            finally:
                context.close()
                browser.close()

    def _login(self, page) -> None:
        page.goto(f"{self.base_url}/login", wait_until="domcontentloaded", timeout=15000)
        page.wait_for_selector("#username", timeout=10000)
        page.fill("#username", self.username)
        page.fill("#password", self.password)
        page.click("#login-btn")
        # Wait for navigation to compose or success
        page.wait_for_url("**/compose/tweet", timeout=10000)
        # Save state after login
        # context storage will be saved later
