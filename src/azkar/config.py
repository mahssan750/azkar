"""User settings, persisted as JSON under ``%APPDATA%\\Azkar\\config.json``.

Adding a new option = add a field here. Unknown keys in an older/newer config
file are ignored, and missing keys fall back to the defaults below.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path

from .paths import data_dir

CONFIG_FILENAME = "config.json"

# The exact phrase you asked the 10-minute reminder to show.
DEFAULT_TASBIH_TEXT = "قل سبحان الله والحمد لله"


@dataclass
class Settings:
    reminder_interval_minutes: int = 10
    startup_dialog_enabled: bool = True
    tasbih_reminder_enabled: bool = True
    reminder_sound_enabled: bool = True
    run_at_login: bool = True

    # The 10-minute reminder text. By default it is the fixed phrase above.
    tasbih_text: str = DEFAULT_TASBIH_TEXT
    # When True, the reminder rotates through content/data/tasbih.json instead
    # of always showing ``tasbih_text`` (ready for "shuffle" later).
    tasbih_shuffle: bool = False

    # Testing aid: when > 0, overrides the interval with this many seconds.
    debug_interval_seconds: int = 0

    # Free-form toggles for future features (azkar window, hadith, quran...).
    features: dict[str, bool] = field(default_factory=dict)

    @property
    def interval_ms(self) -> int:
        if self.debug_interval_seconds and self.debug_interval_seconds > 0:
            return self.debug_interval_seconds * 1000
        return max(1, self.reminder_interval_minutes) * 60 * 1000


def config_path() -> Path:
    return data_dir() / CONFIG_FILENAME


def load_settings() -> Settings:
    """Load settings, creating a default file on first run."""
    p = config_path()
    if not p.exists():
        s = Settings()
        save_settings(s)
        return s
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return Settings()
    known = {f.name for f in fields(Settings)}
    data = {k: v for k, v in raw.items() if k in known}
    return Settings(**data)


def save_settings(s: Settings) -> None:
    p = config_path()
    p.write_text(json.dumps(asdict(s), ensure_ascii=False, indent=2), encoding="utf-8")
