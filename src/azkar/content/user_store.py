"""Stores the user's own azkar list (the ones shown in the main window).

Persisted to ``%APPDATA%\\Azkar\\user_azkar.json`` as a simple list of strings.
On first run it is seeded from the bundled ``azkar.json`` so the window isn't
empty; after that the user fully owns the list (add / delete).
"""
from __future__ import annotations

import json
from pathlib import Path

from ..paths import content_data_dir, data_dir

USER_FILE = "user_azkar.json"


class UserAzkarStore:
    def __init__(self, path: Path | None = None):
        self._path = path or (data_dir() / USER_FILE)
        if self._path.exists():
            self._items = self._read()
        else:
            self._items = self._seed()
            self._save()

    # --- io ---------------------------------------------------------------
    def _read(self) -> list[str]:
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        return [str(x) for x in raw if isinstance(x, str) and str(x).strip()]

    def _seed(self) -> list[str]:
        try:
            raw = json.loads((content_data_dir() / "azkar.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        out: list[str] = []
        for entry in raw:
            if isinstance(entry, str):
                out.append(entry)
            elif isinstance(entry, dict) and "text" in entry:
                out.append(str(entry["text"]))
        return out

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(self._items, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # --- api --------------------------------------------------------------
    def all(self) -> list[str]:
        return list(self._items)

    def add(self, text: str) -> bool:
        text = text.strip()
        if not text or text in self._items:
            return False
        self._items.append(text)
        self._save()
        return True

    def remove(self, text: str) -> bool:
        if text in self._items:
            self._items.remove(text)
            self._save()
            return True
        return False
