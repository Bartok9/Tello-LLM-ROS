# -*- coding: utf-8 -*-
"""RC control channel limits for DJI Tello send_rc_control."""

import math


def clamp_rc_channel(value, lo=-100, hi=100):
    """Convert a scaled RC channel to int clamped to [lo, hi].

    Non-finite values (NaN/inf) map to 0 (fail-closed / stick center).
    Matches historical int() truncation toward zero for finite inputs.
    """
    try:
        v = float(value)
    except (TypeError, ValueError):
        return 0
    if not math.isfinite(v):
        return 0
    iv = int(v)
    if iv < lo:
        return lo
    if iv > hi:
        return hi
    return iv
