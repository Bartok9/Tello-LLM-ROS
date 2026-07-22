# -*- coding: utf-8 -*-
"""Path confinement helpers for media capture directories (stdlib only)."""

from __future__ import annotations

import os
from typing import Any, Optional


def resolve_confined_media_dir(
    raw: Any,
    default_subdir: str,
    allowed_root: Optional[str] = None,
) -> str:
    """
    Resolve a media save directory confined under ``allowed_root``.

    - Empty/None ``raw`` → ``<allowed_root>/<default_subdir>``
    - Absolute/relative paths expanded; if the resolved real path would escape
      ``allowed_root``, fall back to the default under the root (fail-closed).
    - Default ``allowed_root`` is ``~/.ros`` (Tello ROS media convention).

    Does not create directories; caller may mkdir.
    """
    if not default_subdir or not str(default_subdir).strip():
        default_subdir = "tello_media"

    if allowed_root is None or (isinstance(allowed_root, str) and not allowed_root.strip()):
        allowed_root = os.path.join(os.path.expanduser("~"), ".ros")
    else:
        allowed_root = os.path.abspath(os.path.expanduser(str(allowed_root)))

    default_path = os.path.abspath(os.path.join(allowed_root, str(default_subdir).strip()))

    if raw is None:
        return default_path
    if not isinstance(raw, str):
        return default_path
    stripped = raw.strip()
    if not stripped:
        return default_path

    expanded = os.path.expanduser(stripped)
    # Prefer absolute resolution relative to cwd for relative inputs
    candidate = os.path.abspath(expanded)

    # Confinement check (string prefix on absolute paths). Use os.path.commonpath
    # so "/foo/bar" does not accept "/foo/barbados".
    try:
        common = os.path.commonpath([allowed_root, candidate])
    except ValueError:
        # Different drives on Windows, or empty — reject
        return default_path

    if os.path.normcase(common) != os.path.normcase(allowed_root):
        return default_path

    return candidate
