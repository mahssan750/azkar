"""A small QTimer-based scheduler that can drive many interval reminders.

Each reminder has its own timer and an ``enabled`` flag; a timer runs only when
it is enabled and the scheduler isn't globally paused. Built so future reminders
(prayer-time azkar, an hourly hadith, ...) just register here.
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
        self._enabled: dict[str, bool] = {}
        self._paused = False

    def add_interval_reminder(
        self, name: str, interval_ms: int, fn: Callable[[], None], *, enabled: bool = True
    ) -> None:
        timer = QTimer(self)
        timer.setInterval(max(_MIN_INTERVAL_MS, interval_ms))
        timer.timeout.connect(fn)
        self._timers[name] = timer
        self._callbacks[name] = fn
        self._enabled[name] = enabled
        self._apply(name)

    def set_interval(self, name: str, interval_ms: int) -> None:
        timer = self._timers.get(name)
        if timer is not None:
            timer.setInterval(max(_MIN_INTERVAL_MS, interval_ms))
            self._apply(name)  # restart so the new interval takes effect now

    def set_enabled(self, name: str, enabled: bool) -> None:
        if name in self._timers:
            self._enabled[name] = enabled
            self._apply(name)

    def trigger_now(self, name: str) -> None:
        fn = self._callbacks.get(name)
        if fn is not None:
            fn()

    def pause(self) -> None:
        self._paused = True
        self._apply_all()

    def resume(self) -> None:
        self._paused = False
        self._apply_all()

    @property
    def paused(self) -> bool:
        return self._paused

    # --- internals --------------------------------------------------------
    def _apply(self, name: str) -> None:
        timer = self._timers[name]
        if self._enabled.get(name, True) and not self._paused:
            timer.start()
        else:
            timer.stop()

    def _apply_all(self) -> None:
        for name in self._timers:
            self._apply(name)
