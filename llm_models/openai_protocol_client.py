# -*- coding: utf-8 -*-

import rospy
import os
import time
from openai import OpenAI
from .base import LLMBase

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

        if not api_key:
            rospy.logerr(f"API Key not found. Please set the {api_key_env_name} env var or 'api_key' ROS param.")
            raise ValueError("API Key is missing.")
        
        if not base_url:
            rospy.logerr("Base URL not found. Please set the 'base_url' ROS param for this client.")
            raise ValueError("Base URL is missing.")

        # Request timeout seconds (fail-closed sanitize)
        import math
        raw_timeout = kwargs.get('timeout', 60.0)
        try:
            if isinstance(raw_timeout, bool):
                raise TypeError('bool')
            t = float(raw_timeout)
            if not math.isfinite(t) or t <= 0:
                t = 60.0
            t = max(1.0, min(600.0, t))
        except (TypeError, ValueError):
            t = 60.0
        self.timeout = t

        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=self.timeout,
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