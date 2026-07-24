# -*- coding: utf-8 -*-
"""HTTP(S) base URL sanitizers for LLM clients (stdlib-only)."""

from urllib.parse import urlparse


def sanitize_http_base_url(value, default=None):
    """
    Return a cleaned http(s) base URL, or *default* when value is empty/None.

    Rejects non-http schemes, missing netloc, and non-string junk.
    Trailing slashes are stripped (ollama/OpenAI clients often re-add paths).
    """
    if value is None:
        return default
    if not isinstance(value, str):
        return default
    s = value.strip()
    if not s:
        return default
    try:
        parsed = urlparse(s)
    except Exception:
        return default
    if parsed.scheme not in ("http", "https"):
        return default
    if not parsed.netloc:
        return default
    # Rebuild without fragment; keep path if present (rare for ollama host)
    path = parsed.path.rstrip("/") if parsed.path else ""
    if path == "/":
        path = ""
    cleaned = f"{parsed.scheme}://{parsed.netloc}{path}"
    if parsed.query:
        cleaned = f"{cleaned}?{parsed.query}"
    return cleaned
