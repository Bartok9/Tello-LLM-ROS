# -*- coding: utf-8 -*-
"""Sanitize LLM model identifiers used in URL / path construction."""

from __future__ import annotations

import re
from typing import Any, Tuple

# Gemini / Generative Language API model ids (after optional models/ prefix)
_SAFE_MODEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def sanitize_gemini_model_id(raw: Any) -> Tuple[bool, str, str]:
    """
    Normalize a Gemini model id for use in REST path
    ``.../models/{id}:generateContent``.

    Returns ``(ok, cleaned_id, error)``.
    - Strips a single leading ``models/`` prefix (URL already includes it).
    - Accepts only ASCII alnum plus ``.`` ``_`` ``-``.
    - Rejects empty/None/non-str, path separators, whitespace, query/fragment.
    """
    if raw is None:
        return False, "", "model_name is None"
    if not isinstance(raw, str):
        return (
            False,
            "",
            "model_name has unexpected type {0}".format(type(raw).__name__),
        )

    name = raw.strip()
    if not name:
        return False, "", "model_name is empty"

    # Single optional models/ prefix (API path already includes models/)
    if name.startswith("models/") or name.startswith("models\\"):
        # Reject backslash form explicitly
        if "\\" in name:
            return False, "", "model_name must not contain path separators"
        name = name[len("models/") :]

    name = name.strip()
    if not name:
        return False, "", "model_name is empty after models/ strip"

    if ".." in name:
        return False, "", "model_name must not contain path traversal"

    if "/" in name or "\\" in name:
        return False, "", "model_name must not contain path separators"

    if any(ch in name for ch in ("?", "#", " ", "\t", "\n", "\r", "%", "&", "=", ":", "<", ">", '"', "'", "`")):
        return False, "", "model_name contains forbidden character(s)"

    if not _SAFE_MODEL_RE.match(name):
        return False, "", "model_name has invalid characters"

    return True, name, ""
