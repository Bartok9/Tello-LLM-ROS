# -*- coding: utf-8 -*-

import rospy
import os
import time
import requests
import json
from .base import LLMBase
from .gemini_payload import pack_gemini_payload


class GeminiClient(LLMBase):
    """
    Google Gemini API implementation of the LLMBase, using direct REST API calls.
    This version avoids potential SDK version conflicts.
    """
    def _initialize(self, **kwargs):
        """
        Initializes the Gemini client by storing the API key and base URL.
        """
        # 优先从环境变量 GOOGLE_API_KEY 获取
        self.api_key = os.getenv('GOOGLE_API_KEY') or kwargs.get('api_key')
        self.base_url = kwargs.get('base_url')

        if not self.api_key:
            rospy.logerr("Gemini API key not found. Please set the GOOGLE_API_KEY env var or 'api_key' ROS param.")
            raise ValueError("Gemini API key is missing.")
        
        if not self.base_url:
            rospy.logerr("Gemini base_url not found. Please set the 'base_url' ROS param.")
            raise ValueError("Gemini base_url is missing.")
        
        self.headers = {
            'Content-Type': 'application/json',
        }
        self.full_url = f"{self.base_url}?key={self.api_key}"
        rospy.loginfo(f"GeminiClient (REST API) initialized for model: {self.model_name}")

    def query(self, system_prompt, user_prompt, history=None):
        """
        Queries the Gemini REST API using the 'requests' library.
        Honors multi-turn history as alternating user/model parts.
        """
        start_time = time.time()
        response_data = None
        payload = pack_gemini_payload(system_prompt, user_prompt, history)
        self.full_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model_name}:generateContent?key={self.api_key}"
        )

        try:
            response = requests.post(self.full_url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()

            duration_s = time.time() - start_time
            response_data = response.json()

            candidates = response_data.get("candidates") or []
            if not candidates:
                error_msg = "Gemini API returned no candidates"
                rospy.logerr(error_msg)
                return False, "", error_msg, duration_s, 0, 0

            try:
                plan_text = candidates[0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError, TypeError) as e:
                error_msg = (
                    f"Failed to parse Gemini API response. "
                    f"Structure might be unexpected. Error: {e}"
                )
                rospy.logerr(error_msg)
                rospy.logerr(f"Full Response: {response_data}")
                return False, "", error_msg, duration_s, 0, 0

            if not (plan_text or "").strip():
                error_msg = "Gemini API returned empty plan text"
                rospy.logerr(error_msg)
                return False, "", error_msg, duration_s, 0, 0

            # REST API response often omits token counts; keep interface stable.
            prompt_tokens = 0
            completion_tokens = 0
            return True, plan_text.strip(), "", duration_s, prompt_tokens, completion_tokens

        except requests.exceptions.RequestException as e:
            duration_s = time.time() - start_time
            error_msg = f"An error occurred with Gemini REST API: {e}"
            rospy.logerr(error_msg)
            if getattr(e, "response", None) is not None:
                rospy.logerr(f"API Response body: {e.response.text}")
            return False, "", error_msg, duration_s, 0, 0
        except (KeyError, IndexError, TypeError) as e:
            duration_s = time.time() - start_time
            error_msg = (
                f"Failed to parse Gemini API response. "
                f"Structure might be unexpected. Error: {e}"
            )
            rospy.logerr(error_msg)
            if response_data is not None:
                rospy.logerr(f"Full Response: {response_data}")
            return False, "", error_msg, duration_s, 0, 0
