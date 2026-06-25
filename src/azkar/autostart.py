"""Run-at-login management via the per-user ``Run`` registry key.

Uses ``HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run`` so no admin
rights are needed. The value points at the packaged ``Azkar.exe`` when frozen,
or at the venv's ``azkar`` launcher / ``pythonw -m azkar`` during development.
"""
from __future__ import annotations

import sys
from pathlib import Path

from . import APP_NAME, paths

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = APP_NAME  # "Azkar"


# Passed when launched at login, so the app knows to show the startup reminder
# (a manual launch omits it and shows the main window instead).
STARTUP_FLAG = "--startup"


def _command() -> str:
    """The command line Windows should execute at login (quoted)."""
    if paths.is_frozen():
        return f'"{Path(sys.executable)}" {STARTUP_FLAG}'
    # dev: prefer the windowed launcher created by `pip install -e .`
    scripts_dir = Path(sys.executable).parent  # e.g. .venv\Scripts
    launcher = scripts_dir / "azkar.exe"
    if launcher.exists():
        return f'"{launcher}" {STARTUP_FLAG}'
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    runner = pythonw if pythonw.exists() else Path(sys.executable)
    return f'"{runner}" -m azkar {STARTUP_FLAG}'


def enable() -> None:
    import winreg

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
        winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_SZ, _command())


def disable() -> None:
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, VALUE_NAME)
    except FileNotFoundError:
        pass


def is_enabled() -> bool:
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_QUERY_VALUE) as key:
            winreg.QueryValueEx(key, VALUE_NAME)
        return True
    except FileNotFoundError:
        return False


def sync(enabled: bool) -> None:
    """Make the registry match ``enabled``."""
    if enabled:
        enable()
    else:
        disable()
