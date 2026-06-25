"""Azkar — a Windows reminder app to help remember Allah during computer use.

v1 features:
  * A login dialog reminding you to say "بسم الله" and to set your intention.
  * A native Windows toast every N minutes ("قل سبحان الله والحمد لله").

The package is structured so new reminders (azkar windows, hadith shuffler,
Qur'an, ...) can be added without touching the core — see ``reminders`` and
``content``.
"""

__version__ = "0.1.0"

APP_NAME = "Azkar"               # internal name (registry value, files)
APP_DISPLAY_NAME = "أذكار"        # shown to the user (window titles, toasts)
APP_ID = "Azkar.Reminder.1"      # AppUserModelID — toast attribution / taskbar grouping
