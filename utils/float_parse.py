# -*- coding: utf-8 -*-
"""Safe float parsing for regex tool captures (stdlib)."""

from __future__ import annotations

from typing import Optional, Union


def safe_float_capture(raw: Union[str, None], default: Optional[float] = None) -> Optional[float]:
    """Parse a float from a regex capture.

    Returns ``default`` (None by default) when raw is None, empty, or non-numeric.
    """
    if raw is None:
        return default
    if not isinstance(raw, str):
        try:
            val = float(raw)
        except (TypeError, ValueError):
            return default
        if val != val:  # NaN
            return default
        return val
    s = raw.strip()
    if not s:
        return default
    try:
        val = float(s)
    except ValueError:
        return default
    if val != val:
        return default
    return val
