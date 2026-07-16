# -*- coding: utf-8 -*-
"""Pure helpers for packing LLM chat history (stdlib only — no rospy)."""


def pack_chat_messages(system_prompt, user_prompt, history=None):
    """
    Build OpenAI-style chat messages from system, optional flat history, and user.

    History is a flat alternating list: [user1, assistant1, user2, assistant2, ...].
    Index 0 is user. Odd indices are assistant replies.
    """
    messages = [{"role": "system", "content": system_prompt if system_prompt is not None else ""}]
    if history:
        for i, message_content in enumerate(history):
            role = "user" if i % 2 == 0 else "assistant"
            messages.append({"role": role, "content": message_content})
    messages.append({"role": "user", "content": user_prompt if user_prompt is not None else ""})
    return messages
