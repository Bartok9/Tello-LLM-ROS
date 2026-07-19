# -*- coding: utf-8 -*-

import math
import rospy
import requests
import time
from urllib.parse import urlparse
from .base import LLMBase


def sanitize_custom_server_url(url):
    """Normalize and accept only http(s) absolute URLs with a host.

    Rejects empty, file/ftp/data/javascript schemes, and scheme-less strings.
    Returns rstrip('/') base URL suitable for joining /v1/chat/completions.
    """
    if url is None or isinstance(url, bool):
        raise ValueError("server_url is missing or invalid.")
    if not isinstance(url, str):
        raise ValueError("server_url must be a string.")
    cleaned = url.strip()
    if not cleaned:
        raise ValueError("server_url is empty.")
    parsed = urlparse(cleaned)
    scheme = (parsed.scheme or "").lower()
    if scheme not in ("http", "https"):
        raise ValueError("server_url must use http or https scheme.")
    if not parsed.netloc:
        raise ValueError("server_url must include a host.")
    # Drop accidental whitespace fragments; keep path if provided
    normalized = cleaned.rstrip("/")
    return normalized


def sanitize_request_timeout(value, default=60.0, min_s=1.0, max_s=600.0):
    """Positive finite HTTP timeout in seconds; bool rejected."""
    if isinstance(value, bool) or value is None:
        return float(default)
    try:
        v = float(value)
    except (TypeError, ValueError):
        return float(default)
    if not math.isfinite(v) or v <= 0:
        return float(default)
    if v < min_s:
        return float(min_s)
    if v > max_s:
        return float(max_s)
    return float(v)


class CustomApiClient(LLMBase):
    """
    Client for a custom, self-hosted model API.
    """
    def _initialize(self, **kwargs):
        self.server_url = sanitize_custom_server_url(kwargs.get('server_url'))
        self.request_timeout = sanitize_request_timeout(kwargs.get('timeout', 60.0))

        self.api_endpoint = f"{self.server_url}/v1/chat/completions"
        self.headers = {'Content-Type': 'application/json'}
        rospy.loginfo(f"CustomApiClient initialized. Target server: {self.api_endpoint}")

    def query(self, system_prompt, user_prompt):
        payload = {
            "model": self.model_name,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        }
        
        try:
            response = requests.post(
                self.api_endpoint,
                headers=self.headers,
                json=payload,
                timeout=self.request_timeout,
            )
            response.raise_for_status()
            
            response_data = response.json()

            if response_data.get("success"):
                data = response_data.get("data", {})
                plan_text = data.get("plan_text", "")
                duration_s = data.get("duration_s", 0.0)
                usage = data.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                return True, plan_text, "", duration_s, prompt_tokens, completion_tokens
            else:
                error_msg = response_data.get("error_message", "Unknown error from custom API.")
                rospy.logerr(error_msg)
                return False, "", error_msg, 0.0, 0, 0

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to connect to custom model server at {self.api_endpoint}: {e}"
            rospy.logerr(error_msg)
            return False, "", error_msg, 0.0, 0, 0
