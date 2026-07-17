# -*- coding: utf-8 -*-
"""Gemini REST generateContent payload helpers (stdlib-only)."""


def pack_gemini_payload(system_prompt, user_prompt, history=None):
    """Build Gemini generateContent body; history is flat [user, assistant, ...].

    Returns payload dict with systemInstruction + contents.
    """
    system_text = system_prompt if system_prompt is not None else ""
    user_text = user_prompt if user_prompt is not None else ""
    contents = []
    if history:
        for i, message_content in enumerate(history):
            role = "user" if i % 2 == 0 else "model"
            contents.append({"role": role, "parts": [{"text": str(message_content)}]})
    contents.append({"role": "user", "parts": [{"text": str(user_text)}]})
    return {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": str(system_text)}]},
    }
