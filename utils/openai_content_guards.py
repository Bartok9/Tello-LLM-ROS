# -*- coding: utf-8 -*-
"""Fail-closed guards for OpenAI-compatible chat message content."""

from __future__ import annotations

from typing import Any, Tuple


def normalize_message_content(content: Any) -> Tuple[bool, str, str]:
    """
    Normalize a chat completion ``message.content`` value.

    Returns ``(ok, text, error)``:
    - ok True → ``text`` is a stripped string (may be empty)
    - ok False → ``text`` is "" and ``error`` explains why (None / non-str)
    """
    if content is None:
        return False, "", "message content is None"
    if not isinstance(content, str):
        return (
            False,
            "",
            "message content has unexpected type {0}".format(type(content).__name__),
        )
    return True, content.strip(), ""
