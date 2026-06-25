"""Hijri (Islamic) date — local conversion with a monthly online adjustment.

The date is computed locally with ``hijridate`` (Umm al-Qura) so it works
offline. About once a month, if there is an internet connection, we fetch the
official Hijri date from the Aladhan API and store a small day ``adjustment`` to
reconcile any moon-sighting difference. The network call runs on a background
thread and never blocks the UI.
"""
from __future__ import annotations

import datetime
import json
import urllib.request
from typing import Callable

from PySide6.QtCore import QObject, Signal

_ARABIC_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
_SYNC_EVERY_DAYS = 28
_API = "https://api.aladhan.com/v1/gToH/{d:02d}-{m:02d}-{y}"


def _ar(n: int) -> str:
    return str(n).translate(_ARABIC_DIGITS)


def format_hijri(adjustment: int = 0, date: datetime.date | None = None) -> str:
    """Return e.g. "١١ محرم ١٤٤٨ هـ", or "" if conversion is unavailable."""
    date = date or datetime.date.today()
    try:
        from hijridate import Gregorian

        shifted = date + datetime.timedelta(days=adjustment)
        h = Gregorian(shifted.year, shifted.month, shifted.day).to_hijri()
        return f"{_ar(h.day)} {h.month_name('ar')} {_ar(h.year)} هـ"
    except Exception:
        return ""


def _compute_adjustment(timeout: float = 4.0) -> int | None:
    """Day offset between the official (online) Hijri date and the local one."""
    today = datetime.date.today()
    url = _API.format(d=today.day, m=today.month, y=today.year)
    with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310 (https only)
        data = json.load(resp)
    h = data["data"]["hijri"]
    from hijridate import Hijri

    g = Hijri(int(h["year"]), int(h["month"]["number"]), int(h["day"])).to_gregorian()
    offset = (datetime.date(g.year, g.month, g.day) - today).days
    return offset if abs(offset) <= 3 else 0


def needs_sync(last_sync_iso: str) -> bool:
    if not last_sync_iso:
        return True
    try:
        last = datetime.date.fromisoformat(last_sync_iso)
    except ValueError:
        return True
    return (datetime.date.today() - last).days >= _SYNC_EVERY_DAYS


class HijriSync(QObject):
    """Runs the (rare) online adjustment on a daemon thread; emits ``updated``."""

    updated = Signal()

    def __init__(self, settings, save_fn: Callable, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._save = save_fn

    def maybe_sync(self, *, force: bool = False) -> None:
        if not force and not needs_sync(self._settings.hijri_last_sync):
            return
        import threading

        threading.Thread(target=self._work, daemon=True).start()

    def _work(self) -> None:
        try:
            offset = _compute_adjustment()
        except Exception:
            return  # offline / API error — keep the last known adjustment
        if offset is None:
            return
        self._settings.hijri_adjustment = offset
        self._settings.hijri_last_sync = datetime.date.today().isoformat()
        try:
            self._save(self._settings)
        except Exception:
            pass
        self.updated.emit()
