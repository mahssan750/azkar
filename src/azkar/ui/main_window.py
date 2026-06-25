"""The modern main window: a tabbed view of azkar and hadith.

Tabs: morning azkar, evening azkar, the 40 Nawawi hadith, and the user's own
azkar. A green header (with a settings gear) sits on top and a du'a footer at
the bottom. Appearance (theme + font size) is rebuilt on demand.
"""
from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .. import APP_DISPLAY_NAME
from . import rtl, theme
from .pages import AzkarCounterPage, HadithPage, MyAzkarPage

FOOTER_TEXT = "لا تنسونا من صالح دعائكم"


class MainWindow(QMainWindow):
    def __init__(self, icon: QIcon | None = None, on_settings: Optional[Callable] = None, parent=None):
        super().__init__(parent)
        self._icon = icon
        self._on_settings = on_settings
        self._tabs: QTabWidget | None = None

        self.setWindowTitle(APP_DISPLAY_NAME)
        if icon is not None:
            self.setWindowIcon(icon)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.resize(560, 720)
        self.setMinimumSize(440, 520)

        self._build_ui()
        self.apply_theme()

    # --- construction -----------------------------------------------------
    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("central")
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())

        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)
        self._tabs.addTab(AzkarCounterPage("morning_azkar.json"), "أذكار الصباح")
        self._tabs.addTab(AzkarCounterPage("evening_azkar.json"), "أذكار المساء")
        self._tabs.addTab(HadithPage("arbaeen_nawawi.json"), "الأربعون النووية")
        self._tabs.addTab(MyAzkarPage(), "أذكاري")
        root.addWidget(self._tabs, 1)

        footer = QLabel(FOOTER_TEXT)
        footer.setObjectName("footer")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setFont(rtl.arabic_font(13, bold=True))
        root.addWidget(footer)

        self.setCentralWidget(central)  # replaces & deletes any previous central widget

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("header")
        lay = QHBoxLayout(header)
        lay.setContentsMargins(24, 18, 20, 18)
        lay.setSpacing(8)

        titles = QVBoxLayout()
        titles.setSpacing(3)
        title = QLabel(APP_DISPLAY_NAME)
        title.setObjectName("headerTitle")
        title.setFont(rtl.arabic_font(22, bold=True))
        subtitle = QLabel("أذكار الصباح والمساء والأربعون النووية")
        subtitle.setObjectName("headerSubtitle")
        subtitle.setFont(rtl.arabic_font(11))
        titles.addWidget(title)
        titles.addWidget(subtitle)
        lay.addLayout(titles, 1)

        gear = QPushButton("⚙")
        gear.setObjectName("gearBtn")
        gear.setToolTip("الإعدادات")
        gear.setCursor(Qt.CursorShape.PointingHandCursor)
        gear.setFixedSize(38, 38)
        if self._on_settings is not None:
            gear.clicked.connect(self._on_settings)
        lay.addWidget(gear, 0, Qt.AlignmentFlag.AlignTop)
        return header

    # --- appearance -------------------------------------------------------
    def apply_theme(self) -> None:
        self.setStyleSheet(theme.main_window_qss())

    def apply_appearance(self) -> None:
        """Rebuild the UI (new fonts) and re-apply the current theme."""
        index = self._tabs.currentIndex() if self._tabs else 0
        self._build_ui()
        self.apply_theme()
        if self._tabs and 0 <= index < self._tabs.count():
            self._tabs.setCurrentIndex(index)

    def reveal(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event) -> None:
        event.ignore()
        self.hide()
