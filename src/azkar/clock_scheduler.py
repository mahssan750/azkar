"""Fire reminders at a time of day (daily or on a given weekday).

A single QTimer ticks every 30s and fires any matching reminder once per day,
within a short window after its target time (so it won't fire retroactively
hours later if the laptop was off at that minute).
"""
from __future__ import annotations

import datetime
from typing import Callable, Optional

from PySide6.QtCore import QObject, QTimer

_WINDOW_SECONDS = 150
_CHECK_MS = 30_000


def parse_hhmm(value: str, default=(0, 0)) -> tuple[int, int]:
    try:
        hh, mm = value.strip().split(":")
        h, m = int(hh), int(mm)
        if 0 <= h < 24 and 0 <= m < 60:
            return h, m
    except (ValueError, AttributeError):
        pass
    return default


class ClockScheduler(QObject):
    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._items: list[dict] = []
        self._timer = QTimer(self)
        self._timer.setInterval(_CHECK_MS)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def add_daily(
        self,
        name: str,
        hour: int,
        minute: int,
        fn: Callable[[], None],
        *,
        weekday: Optional[int] = None,  # Mon=0 .. Sun=6; None = every day
        enabled: bool = True,
    ) -> None:
        self._items.append(
            {"name": name, "h": hour, "m": minute, "fn": fn,
             "weekday": weekday, "enabled": enabled, "last": None}
        )

    def update(self, name: str, *, hour=None, minute=None, enabled=None) -> None:
        for it in self._items:
            if it["name"] == name:
                if hour is not None:
                    it["h"] = hour
                if minute is not None:
                    it["m"] = minute
                if enabled is not None:
                    it["enabled"] = enabled

    def _tick(self) -> None:
        now = datetime.datetime.now()
        today = now.date()
        for it in self._items:
            if not it["enabled"] or it["last"] == today:
                continue
            if it["weekday"] is not None and now.weekday() != it["weekday"]:
                continue
            target = now.replace(hour=it["h"], minute=it["m"], second=0, microsecond=0)
            delta = (now - target).total_seconds()
            if 0 <= delta < _WINDOW_SECONDS:
                it["last"] = today
                try:
                    it["fn"]()
                except Exception:
                    pass
