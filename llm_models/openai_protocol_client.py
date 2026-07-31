# -*- coding: utf-8 -*-

import rospy
import os
import time
from openai import OpenAI
from .base import LLMBase
from utils.openai_choices_guards import extract_chat_plan_text

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

        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
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

            ok, plan_text, extract_err = extract_chat_plan_text(response)
            usage = getattr(response, "usage", None)
            prompt_tokens = usage.prompt_tokens if usage else 0
            completion_tokens = usage.completion_tokens if usage else 0

            if not ok:
                rospy.logerr(
                    "OpenAI-compatible API returned unusable chat payload: {0}".format(
                        extract_err
                    )
                )
                return False, "", extract_err, duration_s, prompt_tokens, completion_tokens

            return True, plan_text, "", duration_s, prompt_tokens, completion_tokens

        except Exception as e:
            duration_s = time.time() - start_time
            error_msg = f"An unexpected error occurred with the API at {self.client.base_url}: {e}"
            rospy.logerr(error_msg)
            return False, "", error_msg, duration_s, 0, 0