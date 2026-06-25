"""The modern main window: a tabbed view of azkar and hadith.

Tabs: morning azkar, evening azkar, the 40 Nawawi hadith, and the user's own
azkar. A green header (Hijri date + settings gear) sits on top; the footer holds
a "contact us" link on the left and a du'a in the centre.
"""
from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt, QUrl, QUrlQuery
from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import (
    QFrame,
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
CONTACT_EMAIL = "mahassan750@gmail.com"


class MainWindow(QMainWindow):
    def __init__(
        self,
        icon: QIcon | None = None,
        on_settings: Optional[Callable] = None,
        hijri_text: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self._icon = icon
        self._on_settings = on_settings
        self._hijri_text = hijri_text
        self._hijri_label: QLabel | None = None
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

        root.addWidget(self._build_footer())
        self.setCentralWidget(central)

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("header")
        lay = QHBoxLayout(header)
        lay.setContentsMargins(24, 16, 20, 16)
        lay.setSpacing(8)

        titles = QVBoxLayout()
        titles.setSpacing(2)
        title = QLabel(APP_DISPLAY_NAME)
        title.setObjectName("headerTitle")
        title.setFont(rtl.arabic_font(22, bold=True))
        subtitle = QLabel("أذكار الصباح والمساء والأربعون النووية")
        subtitle.setObjectName("headerSubtitle")
        subtitle.setFont(rtl.arabic_font(11))
        self._hijri_label = QLabel(self._hijri_text)
        self._hijri_label.setObjectName("hijriDate")
        self._hijri_label.setFont(rtl.arabic_font(12, bold=True))
        self._hijri_label.setVisible(bool(self._hijri_text))
        titles.addWidget(title)
        titles.addWidget(subtitle)
        titles.addWidget(self._hijri_label)
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

    def _build_footer(self) -> QFrame:
        footer = QFrame()
        footer.setObjectName("footer")
        footer.setLayoutDirection(Qt.LayoutDirection.LeftToRight)  # control physical sides
        lay = QHBoxLayout(footer)
        lay.setContentsMargins(16, 8, 16, 8)
        lay.setSpacing(10)

        contact = QPushButton("✉  تواصل معنا")
        contact.setObjectName("contactBtn")
        contact.setToolTip(CONTACT_EMAIL)
        contact.setCursor(Qt.CursorShape.PointingHandCursor)
        contact.setFont(rtl.arabic_font(12, bold=True))
        contact.setMinimumWidth(140)
        contact.clicked.connect(self._open_contact)

        dua = QLabel(FOOTER_TEXT)
        dua.setObjectName("footerDua")
        dua.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dua.setFont(rtl.arabic_font(13, bold=True))

        spacer = QWidget()  # balances the contact width so the du'a stays centred
        spacer.setFixedWidth(140)

        lay.addWidget(contact, 0, Qt.AlignmentFlag.AlignVCenter)
        lay.addWidget(dua, 1, Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(spacer, 0)
        return footer

    def _open_contact(self) -> None:
        url = QUrl(f"mailto:{CONTACT_EMAIL}")
        query = QUrlQuery()
        query.addQueryItem("subject", "تطبيق أذكار - تواصل")
        url.setQuery(query)
        QDesktopServices.openUrl(url)

    # --- appearance / state ----------------------------------------------
    def set_hijri(self, text: str) -> None:
        self._hijri_text = text
        if self._hijri_label is not None:
            self._hijri_label.setText(text)
            self._hijri_label.setVisible(bool(text))

    def apply_theme(self) -> None:
        self.setStyleSheet(theme.main_window_qss())

    def apply_appearance(self) -> None:
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
