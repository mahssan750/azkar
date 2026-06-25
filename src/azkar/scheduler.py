"""A small QTimer-based scheduler that can drive many interval reminders.

v1 registers a single reminder (the tasbih toast), but the API is built for
more: prayer-time azkar, an hourly hadith, etc. Each gets its own timer and can
be retargeted or paused independently.
"""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QObject, QTimer

_MIN_INTERVAL_MS = 1000


class ReminderScheduler(QObject):
    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._timers: dict[str, QTimer] = {}
        self._callbacks: dict[str, Callable[[], None]] = {}
        self._paused = False

    def add_interval_reminder(self, name: str, interval_ms: int, fn: Callable[[], None]) -> None:
        timer = QTimer(self)
        timer.setInterval(max(_MIN_INTERVAL_MS, interval_ms))
        timer.timeout.connect(fn)
        self._timers[name] = timer
        self._callbacks[name] = fn
        if not self._paused:
            timer.start()

    def set_interval(self, name: str, interval_ms: int) -> None:
        timer = self._timers.get(name)
        if timer is not None:
            timer.setInterval(max(_MIN_INTERVAL_MS, interval_ms))

    def trigger_now(self, name: str) -> None:
        fn = self._callbacks.get(name)
        if fn is not None:
            fn()

    def pause(self) -> None:
        self._paused = True
        for timer in self._timers.values():
            timer.stop()

    def resume(self) -> None:
        self._paused = False
        for timer in self._timers.values():
            timer.start()

    @property
    def paused(self) -> bool:
        return self._paused
