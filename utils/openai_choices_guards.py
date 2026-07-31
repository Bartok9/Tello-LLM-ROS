# -*- coding: utf-8 -*-
"""Fail-closed extraction of plan text from OpenAI-compatible chat responses."""


def extract_chat_plan_text(response):
    """
    Extract assistant text from a chat.completions-like response.

    Returns (ok: bool, plan_text: str, error_message: str).
    Empty choices / missing message / non-str / blank content → fail-closed.
    """
    if response is None:
        return False, "", "OpenAI response is None"

    choices = getattr(response, "choices", None)
    if choices is None and isinstance(response, dict):
        choices = response.get("choices")

    if not isinstance(choices, (list, tuple)) or len(choices) == 0:
        return False, "", "OpenAI response has no choices"

    first = choices[0]
    message = getattr(first, "message", None)
    if message is None and isinstance(first, dict):
        message = first.get("message")
    if message is None:
        return False, "", "OpenAI choice has no message"

    content = getattr(message, "content", None)
    if content is None and isinstance(message, dict):
        content = message.get("content")

    if content is None:
        return False, "", "OpenAI message content is None"
    if not isinstance(content, str):
        return False, "", "OpenAI message content has unexpected type: {0}".format(
            type(content).__name__
        )

    text = content.strip()
    if not text:
        return False, "", "OpenAI message content is empty"

    return True, text, ""
