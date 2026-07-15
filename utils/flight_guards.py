# -*- coding: utf-8 -*-
"""Pure flight safety helpers (stdlib only)."""

from __future__ import annotations

import math
from typing import Any


def clamp_battery_percent_param(raw: Any, default: int = 10) -> int:
    """Sanitize min_takeoff_battery ROS param into [0, 100]."""
    try:
        value = int(float(raw))
    except (TypeError, ValueError):
        return default
    if value < 0:
        return 0
    if value > 100:
        return 100
    return value


def battery_allows_takeoff(percent: Any, minimum: int = 10) -> bool:
    """
    True only if ``percent`` is a finite number and >= ``minimum``.

    Non-finite, None, or unconvertible values fail closed (no takeoff).
    """
    try:
        value = float(percent)
    except (TypeError, ValueError):
        return False
    if not math.isfinite(value):
        return False
    try:
        min_v = int(minimum)
    except (TypeError, ValueError):
        min_v = 10
    return value >= min_v
