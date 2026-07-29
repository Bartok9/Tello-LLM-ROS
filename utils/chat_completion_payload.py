# -*- coding: utf-8 -*-
"""Validate LAN custom model server chat-completion JSON body."""


def parse_chat_completion_payload(data):
    """
    Return (ok, error_message, fields_dict_or_None).
    fields: model, system_prompt, user_prompt (str).
    """
    if not isinstance(data, dict):
        return False, "request body must be a JSON object", None

    model = data.get("model", "default-model")
    system_prompt = data.get("system_prompt", "")
    user_prompt = data.get("user_prompt", "")

    if model is None:
        model = "default-model"
    if system_prompt is None:
        system_prompt = ""
    if user_prompt is None:
        user_prompt = ""

    if not isinstance(model, str):
        return False, "model must be a string", None
    if not isinstance(system_prompt, str):
        return False, "system_prompt must be a string", None
    if not isinstance(user_prompt, str):
        return False, "user_prompt must be a string", None

    user_prompt = user_prompt.strip()
    if not user_prompt:
        return False, "user_prompt is required.", None

    return True, "", {
        "model": model,
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
    }
