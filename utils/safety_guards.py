# -*- coding: utf-8 -*-
"""Pure fail-closed guards shared by Tello ROS driver (no rospy import)."""


def sanitize_cmd_vel_timeout_sec(value, default=0.5, min_s=0.05, max_s=30.0):
    """Return a positive finite watchdog timeout in seconds for cmd_vel.

    Rejects bool (avoids True->1), non-numeric, non-finite, and non-positive
    values. Clamps into [min_s, max_s].
    """
    if isinstance(value, bool) or value is None:
        return float(default)
    try:
        v = float(value)
    except (TypeError, ValueError):
        return float(default)
    if v != v or v in (float("inf"), float("-inf")):
        return float(default)
    if v <= 0:
        return float(default)
    if v < min_s:
        return float(min_s)
    if v > max_s:
        return float(max_s)
    return float(v)
