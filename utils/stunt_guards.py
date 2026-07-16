# -*- coding: utf-8 -*-
"""Pure battery helpers for Tello stunts (flips) — stdlib only."""

from __future__ import annotations

import math
from typing import Any


def battery_allows_stunt(percent: Any, minimum: int = 20) -> bool:
    """
    True only if ``percent`` is convertible to a finite number and >= minimum.

    None / NaN / non-convertible values → False (fail-closed).
    """
    try:
        min_i = int(minimum)
    except (TypeError, ValueError):
        min_i = 20
    if min_i < 0:
        min_i = 0
    if min_i > 100:
        min_i = 100
    if percent is None:
        return False
    try:
        value = float(percent)
    except (TypeError, ValueError):
        return False
    if not math.isfinite(value):
        return False
    return value >= min_i


def clamp_battery_threshold(raw: Any, default: int = 20) -> int:
    """Clamp a ROS param style threshold to [0, 100]."""
    try:
        default_i = int(default)
    except (TypeError, ValueError):
        default_i = 20
    try:
        n = int(float(raw))
    except (TypeError, ValueError):
        n = default_i
    if n < 0:
        return 0
    if n > 100:
        return 100
    return n
