"""Play the notification sound (a short "knock-knock") on Windows.

Uses the stdlib ``winsound`` so there are no extra dependencies. Playback is
asynchronous (non-blocking) and any failure is swallowed — a missing sound must
never stop a reminder.
"""
from __future__ import annotations

from .paths import assets_dir


def knock_path() -> str:
    return str(assets_dir() / "sounds" / "knock.wav")


def play_knock() -> None:
    try:
        import os
        import winsound

        path = knock_path()
        if os.path.exists(path):
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception:
        pass
