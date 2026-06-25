"""Right-to-left layout and Arabic-font helpers.

A bundled font in ``assets/fonts/*.ttf`` (if present) is preferred so Arabic
renders consistently on any machine; otherwise we fall back to a known-good
system family.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

from ..paths import assets_dir

# Preference order when no bundled font is found.
SYSTEM_FONT_CANDIDATES = [
    "Amiri",
    "Scheherazade New",
    "Traditional Arabic",
    "Segoe UI",
    "Tahoma",
]

_family: str | None = None


def load_arabic_font() -> str:
    """Resolve (once) the best available Arabic-capable font family."""
    global _family
    if _family:
        return _family

    fonts_dir = assets_dir() / "fonts"
    if fonts_dir.exists():
        for ttf in sorted(fonts_dir.glob("*.ttf")):
            fid = QFontDatabase.addApplicationFont(str(ttf))
            families = QFontDatabase.applicationFontFamilies(fid)
            if families:
                _family = families[0]
                return _family

    available = set(QFontDatabase.families())
    for fam in SYSTEM_FONT_CANDIDATES:
        if fam in available:
            _family = fam
            return _family

    _family = QApplication.font().family()
    return _family


def apply_rtl(app: QApplication) -> None:
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    base = QFont(load_arabic_font())
    base.setPointSize(11)
    app.setFont(base)


def arabic_font(point_size: int, *, bold: bool = False) -> QFont:
    f = QFont(load_arabic_font(), point_size)
    f.setBold(bold)
    return f
