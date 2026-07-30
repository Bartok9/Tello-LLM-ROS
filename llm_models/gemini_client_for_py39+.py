# -*- coding: utf-8 -*-

import rospy
import os
import time
from google import genai
from .base import LLMBase


def pack_gemini_contents(user_prompt, history=None):
    """
    Build a genai contents list that preserves prior turns.

    history is expected as an alternating user/assistant string list
    (same convention as llm_service_node / task_control).
    """
    contents = []
    if history:
        for item in history:
            if item is None:
                continue
            text = item if isinstance(item, str) else str(item)
            text = text.strip()
            if text:
                contents.append(text)
    if user_prompt is None:
        user_prompt = ""
    if not isinstance(user_prompt, str):
        user_prompt = str(user_prompt)
    contents.append(user_prompt)
    return contents


def extract_plan_text(response):
    """Fail-closed plan_text from a generate_content response."""
    text = getattr(response, "text", None)
    if not isinstance(text, str):
        return None
    text = text.strip()
    if not text:
        return None
    return text


class GeminiClient(LLMBase):
    """
    Google Gemini API implementation of the LLMBase, using the genai.Client() method.
    """
    def _initialize(self, **kwargs):
        """
        Initializes the Gemini client.
        Authentication is handled by Google Cloud's Application Default Credentials.
        Make sure you have run 'gcloud auth application-default login' in your terminal.
        """
        api_key = kwargs.get('api_key') or os.getenv('GOOGLE_API_KEY')
        
        try:
            # 初始化通用客户端。如果已运行gcloud auth，则无需api_key。
            # 如果未认证，它会尝试使用参数或环境变量中的api_key。
            self.client = genai.Client(api_key=api_key)
            rospy.loginfo(f"GeminiClient initialized for model: {self.model_name}")
        except Exception as e:
            rospy.logerr(f"Failed to initialize Gemini Client. Have you run 'gcloud auth application-default login'? Error: {e}")
            raise

    def query(self, system_prompt, user_prompt, history=None):
        start_time = time.time()
        duration_s = 0
        prompt_tokens = 0
        completion_tokens = 0

        try:
            contents = pack_gemini_contents(user_prompt, history=history)
            # 1. 生成内容 (使用 client.models.generate_content)
            # system_prompt 可以通过 system_instruction 参数直接传入
            response = self.client.models.generate_content(
                model=f"models/{self.model_name}",  # 新版API通常需要 'models/' 前缀
                contents=contents,
                system_instruction=system_prompt
            )
            plan_text = extract_plan_text(response)
            duration_s = time.time() - start_time
            if plan_text is None:
                error_msg = "Gemini response missing or empty text (blocked/empty candidates)."
                rospy.logerr(error_msg)
                return False, "", error_msg, duration_s, prompt_tokens, completion_tokens
            
            # 2. 计算Token数 (使用 client.models.count_tokens)
            # 将 system_prompt 和 contents 一起传入以获得准确的prompt token数
            prompt_contents = list(contents)
            if system_prompt:
                prompt_contents.insert(0, system_prompt)

            count_response = self.client.models.count_tokens(
                model=f"models/{self.model_name}",
                contents=prompt_contents
            )
            prompt_tokens = count_response.total_tokens

            # 计算生成文本的token数
            completion_tokens = self.client.models.count_tokens(
                model=f"models/{self.model_name}",
                contents=[plan_text]
            ).total_tokens

            return True, plan_text, "", duration_s, prompt_tokens, completion_tokens

        except TypeError as e:
            # Surface history-related TypeErrors clearly if SDK rejects kwargs
            duration_s = time.time() - start_time
            error_msg = f"An error occurred with Gemini API: {e}"
            rospy.logerr(error_msg)
            return False, "", error_msg, duration_s, prompt_tokens, completion_tokens
        except Exception as e:
            duration_s = time.time() - start_time
            error_msg = f"An error occurred with Gemini API: {e}"
            rospy.logerr(error_msg)
            return False, "", error_msg, duration_s, prompt_tokens, completion_tokens
