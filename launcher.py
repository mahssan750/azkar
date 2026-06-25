"""Frozen-build entry point.

PyInstaller analyses the entry file as a top-level script, where the package's
relative imports (``from .app import ...``) don't resolve. Using an absolute
import here — together with ``--paths src`` — lets PyInstaller discover the
``azkar`` package and all of its dependencies (PySide6, windows-toasts).

For normal use prefer ``python -m azkar`` or the installed ``azkar`` launcher.
"""
from azkar.app import main

if __name__ == "__main__":
    raise SystemExit(main())
