# -*- coding: utf-8 -*-

import rospy
import os
import time
from openai import OpenAI
from .base import LLMBase


def sanitize_openai_timeout(value, default=60.0, min_s=1.0, max_s=600.0):
    """Positive finite HTTP timeout in [min_s, max_s]; invalid -> default. bool rejected."""
    if isinstance(value, bool) or value is None:
        return float(default)
    try:
        t = float(value)
    except (TypeError, ValueError):
        return float(default)
    if t != t or t in (float("inf"), float("-inf")):
        return float(default)
    if t < float(min_s) or t > float(max_s):
        return float(default)
    return float(t)


def validate_openai_base_url(url):
    """Require non-empty http(s) base URL; return stripped URL or raise ValueError."""
    if url is None:
        raise ValueError("Base URL is missing.")
    if not isinstance(url, str):
        raise ValueError("Base URL must be a string.")
    cleaned = url.strip()
    if not cleaned:
        raise ValueError("Base URL is missing.")
    lower = cleaned.lower()
    if not (lower.startswith("http://") or lower.startswith("https://")):
        raise ValueError("Base URL must start with http:// or https://")
    return cleaned


class GenericOpenAIClient(LLMBase):
    """
    A generic client for any API that is compatible with the OpenAI protocol.
    It is configured via api_key and base_url.
    """
    def _initialize(self, **kwargs):
        """
        Initializes the OpenAI client to connect to a specified endpoint.
        """
        api_key_env_name = kwargs.get('api_key_env_name', 'GENERIC_OPENAI_API_KEY')
        api_key = os.getenv(api_key_env_name) or kwargs.get('api_key')
        
        base_url = kwargs.get('base_url')
        timeout = sanitize_openai_timeout(kwargs.get('timeout', 60.0))

        if not api_key:
            rospy.logerr(f"API Key not found. Please set the {api_key_env_name} env var or 'api_key' ROS param.")
            raise ValueError("API Key is missing.")
        
        try:
            base_url = validate_openai_base_url(base_url)
        except ValueError as ve:
            rospy.logerr(f"Base URL invalid: {ve}. Please set the 'base_url' ROS param for this client.")
            raise

        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=timeout,
            )
            rospy.loginfo(f"GenericOpenAIClient initialized for model '{self.model_name}' at endpoint '{base_url}'")
        except Exception as e:
            rospy.logerr(f"Failed to initialize GenericOpenAIClient: {e}")
            raise

    def query(self, system_prompt, user_prompt, history=None):
        start_time = time.time()
        
        # messages = [
        #     {"role": "system", "content": system_prompt},
        #     {"role": "user", "content": user_prompt}
        # ]
        
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            for i, message_content in enumerate(history):
                role = "user" if i % 2 == 0 else "assistant"
                messages.append({"role": role, "content": message_content})
        messages.append({"role": "user", "content": user_prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            duration_s = time.time() - start_time

            plan_text = response.choices[0].message.content
            usage = response.usage
            prompt_tokens = usage.prompt_tokens if usage else 0
            completion_tokens = usage.completion_tokens if usage else 0

            return True, plan_text.strip(), "", duration_s, prompt_tokens, completion_tokens

        except Exception as e:
            duration_s = time.time() - start_time
            error_msg = f"An unexpected error occurred with the API at {self.client.base_url}: {e}"
            rospy.logerr(error_msg)
            return False, "", error_msg, duration_s, 0, 0