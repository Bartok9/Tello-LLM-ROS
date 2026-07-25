# -*- coding: utf-8 -*-

import rospy
import ollama
from .base import LLMBase

class OllamaClient(LLMBase):
    """
    Ollama implementation of the LLMBase.
    Connects to a local Ollama server to get model responses.
    """
    def _initialize(self, **kwargs):
        """
        Initializes the Ollama client.
        kwargs can include 'timeout'.
        """
        self.timeout = kwargs.get('timeout', 150.0)
        try:
            self.client = ollama.Client(timeout=self.timeout)
            self.client.list()
            rospy.loginfo(f"Successfully connected to Ollama client. Model: {self.model_name}")
        except Exception as e:
            rospy.logfatal(f"Failed to connect to Ollama. Is the server running? Error: {e}")
            raise

    def query(self, system_prompt, user_prompt, history=None):
        """
        Queries the Ollama model.
        """
        # messages = [
        #     {'role': 'system', 'content': system_prompt},
        #     {'role': 'user', 'content': user_prompt}
        # ]
        
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            # 假设历史是 [user_msg1, assistant_msg1, user_msg2, ...] 的扁平列表
            # 我们需要将其转换为带 'role' 的字典列表
            for i, message_content in enumerate(history):
                role = "user" if i % 2 == 0 else "assistant"
                messages.append({"role": role, "content": message_content})
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=messages,
            )
            if not isinstance(response, dict):
                error_msg = f"Ollama model '{self.model_name}' returned non-dict response"
                rospy.logerr(error_msg)
                return False, "", error_msg, 0.0, 0, 0
            message = response.get('message')
            if not isinstance(message, dict):
                error_msg = f"Ollama model '{self.model_name}' response missing message object"
                rospy.logerr(error_msg)
                return False, "", error_msg, 0.0, 0, 0
            plan_text = message.get('content')
            if not isinstance(plan_text, str):
                error_msg = f"Ollama model '{self.model_name}' returned empty or non-str message.content"
                rospy.logerr(error_msg)
                return False, "", error_msg, 0.0, 0, 0
            duration_ns = response.get('total_duration', 0) or 0
            try:
                duration_s = float(duration_ns) / 1_000_000_000.0
            except (TypeError, ValueError):
                duration_s = 0.0
            prompt_tokens = response.get('prompt_eval_count', 0) or 0
            completion_tokens = response.get('eval_count', 0) or 0
            try:
                prompt_tokens = int(prompt_tokens)
                completion_tokens = int(completion_tokens)
            except (TypeError, ValueError):
                prompt_tokens, completion_tokens = 0, 0
            return True, plan_text, "", duration_s, prompt_tokens, completion_tokens

        except Exception as e:
            error_msg = f"Failed to query Ollama model '{self.model_name}': {e}"
            rospy.logerr(error_msg)
            return False, "", str(e), 0.0, 0, 0