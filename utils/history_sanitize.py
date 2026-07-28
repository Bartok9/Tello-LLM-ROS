# -*- coding: utf-8 -*-
"""Sanitize multi-turn chat history before LLM client message build."""


def sanitize_chat_history(history, max_items=100, max_chars=8000):
    """
    Normalize history into a list of plain strings safe for chat APIs.

    - None / non-list → []
    - keep str (strip); drop empty after strip
    - int/float → str(...); bool skipped (ambiguous)
    - other types dropped
    - cap list length and per-item character length
    """
    if history is None:
        return []
    if not isinstance(history, (list, tuple)):
        return []

    try:
        max_items = int(max_items)
    except (TypeError, ValueError):
        max_items = 100
    if max_items < 0:
        max_items = 0

    try:
        max_chars = int(max_chars)
    except (TypeError, ValueError):
        max_chars = 8000
    if max_chars < 1:
        max_chars = 1

    out = []
    for item in history:
        if isinstance(item, bool):
            continue
        if isinstance(item, str):
            s = item.strip()
        elif isinstance(item, (int, float)):
            # reject non-finite floats
            if isinstance(item, float):
                import math
                if not math.isfinite(item):
                    continue
            s = str(item).strip()
        else:
            continue
        if not s:
            continue
        if len(s) > max_chars:
            s = s[:max_chars]
        out.append(s)
        if len(out) >= max_items:
            break
    return out
