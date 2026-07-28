# -*- coding: utf-8 -*-
"""Fail-closed helpers for Tello client boot (connect / streamon)."""


def safe_tello_connect(tello):
    """
    Invoke tello.connect().

    Returns:
        (ok: bool, err: str)
    """
    if tello is None:
        return False, "tello client is None"
    try:
        connect = getattr(tello, "connect", None)
        if connect is None or not callable(connect):
            return False, "tello.connect is missing"
        connect()
        return True, ""
    except Exception as e:
        return False, str(e) or e.__class__.__name__


def safe_tello_streamon(tello):
    """
    Invoke tello.streamon().

    Returns:
        (ok: bool, err: str)
    """
    if tello is None:
        return False, "tello client is None"
    try:
        streamon = getattr(tello, "streamon", None)
        if streamon is None or not callable(streamon):
            return False, "tello.streamon is missing"
        streamon()
        return True, ""
    except Exception as e:
        return False, str(e) or e.__class__.__name__
