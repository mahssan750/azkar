"""Base class for reminders.

A reminder is anything with a ``name`` and a ``run()`` that performs its action
(show a toast, open a window, ...). The scheduler only needs ``run``.
"""
from __future__ import annotations


class Reminder:
    name: str = "reminder"

    def run(self) -> None:  # pragma: no cover - interface
        raise NotImplementedError
