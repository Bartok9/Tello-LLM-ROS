# -*- coding: utf-8 -*-
"""Log-safe secret helpers (stdlib-only; safe to import without rospy)."""


def redact_secret(value, visible_tail=4):
    """Return a log-safe redaction of an API key or token. Never returns the full secret."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return ""
    if len(s) <= visible_tail:
        return "***"
    return f"***{s[-visible_tail:]}"
