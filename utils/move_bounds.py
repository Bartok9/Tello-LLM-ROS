# -*- coding: utf-8 -*-
"""Finite-value and range checks for Tello move/record services."""

import math
from math import pi


def distance_meters_to_sdk_cm(value):
    """Convert distance meters to Tello SDK cm (20..500)."""
    try:
        v = float(value)
    except (TypeError, ValueError) as e:
        raise ValueError("Distance must be a finite number.") from e
    if not math.isfinite(v):
        raise ValueError("Distance must be a finite number.")
    value_in_sdk_units = int(v * 100)
    if not (20 <= value_in_sdk_units <= 500):
        raise ValueError("Distance must be between 0.2 and 5.0 meters.")
    return value_in_sdk_units


def angle_to_sdk_degrees(value):
    """Convert angle to Tello rotate degrees (1..360).

    Preserves existing driver heuristic: values > 10 treated as degrees;
    otherwise radians → degrees.
    """
    try:
        v = float(value)
    except (TypeError, ValueError) as e:
        raise ValueError("Angle must be a finite number.") from e
    if not math.isfinite(v):
        raise ValueError("Angle must be a finite number.")
    if v > 10:
        value_in_sdk_units = int(v)
    else:
        value_in_sdk_units = int(v * 180.0 / pi)
    if not (1 <= value_in_sdk_units <= 360):
        raise ValueError(
            f"Angle must be between ~0.017 and ~6.28 radians (1-360 degrees), command is {value}"
        )
    return value_in_sdk_units


def clamp_video_duration_s(duration, lo=1.0, hi=120.0):
    """Validate video record duration seconds in [lo, hi]."""
    try:
        v = float(duration)
    except (TypeError, ValueError) as e:
        raise ValueError(
            f"Video duration must be a finite number between {lo} and {hi} seconds."
        ) from e
    if not math.isfinite(v) or v < lo or v > hi:
        raise ValueError(
            f"Video duration must be between {lo} and {hi} seconds (got {duration!r})."
        )
    return v
