# -*- coding: utf-8 -*-
"""Tools config loader helpers (stdlib; no rospy required)."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional, Tuple


def load_tools_config(path: Optional[str]) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """Load tools JSON.

    Returns (ok, config, err). On success config always has a list under ``tools``.
    """
    if path is None or not isinstance(path, str) or not path.strip():
        return False, None, "tools_config path is missing or empty"
    path = path.strip()
    if not os.path.isfile(path):
        return False, None, f"tools_config file not found: {path}"
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        return False, None, f"tools_config invalid JSON: {exc}"
    except OSError as exc:
        return False, None, f"tools_config read error: {exc}"
    if not isinstance(data, dict):
        return False, None, "tools_config root must be a JSON object"
    tools = data.get("tools")
    if tools is None:
        data = dict(data)
        data["tools"] = []
    elif not isinstance(tools, list):
        return False, None, "tools_config 'tools' must be a list"
    return True, data, ""
