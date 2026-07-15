# -*- coding: utf-8 -*-
"""Pure helpers for tool parameter coercion (stdlib only)."""

from __future__ import annotations

import math
from typing import Any


def coerce_finite_float(raw: Any, name: str = "value") -> float:
    """Parse ``raw`` as a finite float or raise ValueError."""
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a number") from exc
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return value


def sanitize_history_length(raw: Any, default: int = 10) -> int:
    """
    Ensure a positive int for ``collections.deque(maxlen=...)``.

    Non-convertible or < 1 → ``default`` (if default invalid, use 10).
    """
    try:
        default_i = int(default)
    except (TypeError, ValueError):
        default_i = 10
    if default_i < 1:
        default_i = 10
    try:
        n = int(float(raw))
    except (TypeError, ValueError):
        return default_i
    if n < 1:
        return default_i
    return n
