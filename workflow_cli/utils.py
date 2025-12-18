from __future__ import annotations

import re
from typing import Iterable

STATUS_VALUES = ("todo", "in_progress", "done")

def normalize_status(value: str) -> str:
    v = (value or "").strip().lower()
    if v in STATUS_VALUES:
        return v
    raise ValueError(f"Invalid status: {value}. Choose one of: {', '.join(STATUS_VALUES)}")

def normalize_priority(value: int | str) -> int:
    try:
        n = int(value)
    except Exception:
        raise ValueError("Priority must be an integer (1-5).")
    if 1 <= n <= 5:
        return n
    raise ValueError("Priority must be between 1 and 5.")

def normalize_tags(tags: Iterable[str]) -> list[str]:
    cleaned: list[str] = []
    for t in tags:
        t = (t or "").strip().lower()
        if not t:
            continue
        t = re.sub(r"\s+", "-", t)
        cleaned.append(t)
    # de-dupe while preserving order
    seen = set()
    out = []
    for t in cleaned:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out

def clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))
