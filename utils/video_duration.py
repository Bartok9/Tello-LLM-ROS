# -*- coding: utf-8 -*-
"""Sanitize RecordVideo duration (seconds)."""
import math


def sanitize_record_duration(value, min_s=1.0, max_s=120.0):
    """
    Return (ok, duration_or_None, message).
    Accepts finite numbers in [min_s, max_s]; rejects bool, NaN, Inf, non-numeric.
    """
    if isinstance(value, bool) or value is None:
        return False, None, "duration must be a finite number of seconds"
    try:
        duration = float(value)
    except (TypeError, ValueError):
        return False, None, "duration must be a finite number of seconds"
    if not math.isfinite(duration):
        return False, None, "duration must be finite (not NaN/Inf)"
    if duration < min_s or duration > max_s:
        return False, None, f"duration must be between {min_s:g} and {max_s:g} seconds"
    return True, duration, ""
