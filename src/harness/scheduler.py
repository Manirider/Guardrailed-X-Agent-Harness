from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd

from .config import config
from .models import ScheduledPost


def _parse_schedule(csv_path: Path) -> List[ScheduledPost]:
    df = pd.read_csv(csv_path)
    # Support both schemas
    # Normalize columns
    columns = {c.lower(): c for c in df.columns}
    # Map possible names
    def get_col(*names):
        for n in names:
            if n in columns:
                return columns[n]
        raise ValueError(f"Missing required column, tried {names}")

    # Try row_id / row_id
    try:
        row_id_col = get_col("row_id", "rowid")
        date_col = get_col("post_date", "date", "postdate")
        text_col = get_col("raw_text", "tweet_text", "text")
    except ValueError as e:
        raise ValueError(f"Schedule CSV validation error: {e}")

    posts: List[ScheduledPost] = []
    seen_ids = set()
    for _, row in df.iterrows():
        row_id = str(row[row_id_col]).strip()
        if not row_id:
            raise ValueError("row_id missing")
        if row_id in seen_ids:
            raise ValueError(f"Duplicate row_id detected: {row_id}")
        seen_ids.add(row_id)

        raw_text = str(row[text_col]).strip()
        if not raw_text:
            raise ValueError(f"Empty raw_text for row_id {row_id}")

        date_val = row[date_col]
        # Parse date
        try:
            if isinstance(date_val, pd.Timestamp):
                post_date = date_val.date()
            else:
                post_date = pd.to_datetime(str(date_val)).date()
        except Exception:
            raise ValueError(f"Malformed date for row_id {row_id}: {date_val}")

        posts.append(ScheduledPost(row_id=row_id, post_date=post_date, raw_text=raw_text))
    return posts


def _today() -> date:
    tz = ZoneInfo(config.TIMEZONE)
    return datetime.now(tz).date()


def select_due_row(
    csv_path: Path,
    today: Optional[date] = None,
    posted_ids: Optional[set[str]] = None,
) -> Tuple[Optional[ScheduledPost], List[str], bool]:
    """
    Returns selected post, ignored_row_ids, multiple_due_rows_flag
    """
    if today is None:
        today = _today()
    posts = _parse_schedule(csv_path)
    eligible = [
        p for p in posts
        if p.post_date == today and (posted_ids is None or p.row_id not in posted_ids)
    ]
    if not eligible:
        return None, [], False
    # Deterministic: sort by row_id
    eligible.sort(key=lambda p: p.row_id)
    selected = eligible[0]
    ignored = [p.row_id for p in eligible[1:]]
    multiple = len(eligible) > 1
    return selected, ignored, multiple
