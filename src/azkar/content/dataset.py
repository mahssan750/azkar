"""Load a structured content dataset (list of dict records) from content/data.

Used by the tabbed pages (morning/evening azkar, the 40 hadith). Unlike
``JsonContentProvider`` (which serves shuffled strings for the toast), this
returns the raw records so the UI can read fields like ``count`` or ``number``.
"""
from __future__ import annotations

import json

from ..paths import content_data_dir


def load_dataset(filename: str) -> list[dict]:
    try:
        raw = json.loads((content_data_dir() / filename).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [item for item in raw if isinstance(item, dict)]
