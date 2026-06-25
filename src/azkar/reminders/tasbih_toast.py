"""The every-N-minutes reminder: a native toast ("قل سبحان الله والحمد لله").

By default it always shows ``settings.tasbih_text``. If ``tasbih_shuffle`` is
enabled, it rotates through ``content/data/tasbih.json`` instead.
"""
from __future__ import annotations

from ..config import Settings
from ..content.json_provider import JsonContentProvider
from ..notifier import Notifier
from ..sound import play_knock
from .base import Reminder

TOAST_TITLE = "تذكير"


class TasbihToastReminder(Reminder):
    name = "tasbih"

    def __init__(self, notifier: Notifier, settings: Settings):
        self._notifier = notifier
        self._settings = settings
        self._provider = JsonContentProvider("tasbih.json")

    def run(self) -> None:
        if self._settings.tasbih_shuffle:
            text = self._provider.next() or self._settings.tasbih_text
        else:
            text = self._settings.tasbih_text
        sound = self._settings.reminder_sound_enabled
        if sound:
            play_knock()
        self._notifier.notify(TOAST_TITLE, text, silent=sound)
