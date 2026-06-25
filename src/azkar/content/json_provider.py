"""A content provider backed by a JSON file.

The JSON is a list of either plain strings or objects with a ``"text"`` key
(extra keys like ``source``/``book`` are ignored for now but kept in the file
for future features). Items are served as a shuffled "bag": every item appears
once before any repeats, and the same item never shows twice in a row.
"""
from __future__ import annotations

import json
import random
from os import PathLike
from pathlib import Path

from ..paths import content_data_dir


class JsonContentProvider:
    def __init__(
        self,
        filename: str | None = None,
        *,
        path: str | PathLike[str] | None = None,
        rng: random.Random | None = None,
    ):
        if path is not None:
            self._path = Path(path)
        elif filename is not None:
            self._path = content_data_dir() / filename
        else:
            raise ValueError("Provide either filename or path")
        self._rng = rng or random.Random()
        self._items: list[str] = self._load()
        self._bag: list[int] = []
        self._last: str | None = None

    def _load(self) -> list[str]:
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        items: list[str] = []
        for entry in raw:
            if isinstance(entry, str):
                items.append(entry)
            elif isinstance(entry, dict) and "text" in entry:
                items.append(str(entry["text"]))
        return items

    def all(self) -> list[str]:
        return list(self._items)

    def next(self) -> str:
        if not self._items:
            return ""
        if len(self._items) == 1:
            self._last = self._items[0]
            return self._items[0]
        if not self._bag:
            self._bag = list(range(len(self._items)))
            self._rng.shuffle(self._bag)
            # avoid an immediate repeat across the shuffle boundary
            if self._items[self._bag[0]] == self._last:
                self._bag.append(self._bag.pop(0))
        choice = self._items[self._bag.pop(0)]
        self._last = choice
        return choice
