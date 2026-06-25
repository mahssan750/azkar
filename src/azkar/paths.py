"""Filesystem locations, resolved for both dev runs and PyInstaller builds.

Read-only resources (assets, seed content) ship with the app; per-user state
(config, generated icon) lives under ``%APPDATA%\\Azkar``.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from . import APP_NAME


def is_frozen() -> bool:
    """True when running from a PyInstaller-built executable."""
    return getattr(sys, "frozen", False)


def resource_root() -> Path:
    """Root for bundled, read-only resources (the ``assets`` folder, etc.)."""
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS"))
    # dev: project root is two levels above this file (src/azkar/paths.py)
    return Path(__file__).resolve().parents[2]


def package_root() -> Path:
    """Directory of the installed ``azkar`` package."""
    return Path(__file__).resolve().parent


def assets_dir() -> Path:
    return resource_root() / "assets"


def content_data_dir() -> Path:
    """Where the seed JSON content lives (bundled with the package)."""
    candidate = package_root() / "content" / "data"
    if candidate.exists():
        return candidate
    # PyInstaller fallback (added via --add-data to <root>/azkar/content/data)
    return resource_root() / "azkar" / "content" / "data"


def data_dir() -> Path:
    """Per-user writable directory, created on demand: ``%APPDATA%\\Azkar``."""
    base = os.environ.get("APPDATA") or str(Path.home())
    d = Path(base) / APP_NAME
    d.mkdir(parents=True, exist_ok=True)
    return d


def icon_png_path() -> Path:
    """Cached PNG of the app icon, used as the toast logo image."""
    return data_dir() / "icon.png"
