"""The content-provider interface.

Any object that can hand out the "next" piece of text and list "all" of its
items can be plugged into a reminder. ``JsonContentProvider`` is the v1
implementation; future providers (a hadith book, a Qur'an index, an API) just
need to satisfy this protocol.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ContentProvider(Protocol):
    def next(self) -> str:
        """Return the next item to show (may be shuffled / rotated)."""
        ...

    def all(self) -> list[str]:
        """Return every item this provider knows about."""
        ...
