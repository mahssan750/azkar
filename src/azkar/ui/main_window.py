"""The modern main window: a tabbed view of azkar and hadith.

Tabs: morning azkar, evening azkar, the 40 Nawawi hadith, and the user's own
azkar. A green header sits on top and a du'a footer at the bottom.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .. import APP_DISPLAY_NAME
from . import rtl
from .pages import AzkarCounterPage, HadithPage, MyAzkarPage

FOOTER_TEXT = "لا تنسونا من صالح دعائكم"

_STYLE = """
QWidget#central { background: #eef2f0; }

QFrame#header, QWidget#header {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #1f7a5a, stop:1 #155c43);
}
QLabel#headerTitle    { color: #ffffff; }
QLabel#headerSubtitle { color: #cfe9df; }

/* Tabs */
QTabWidget::pane { border: none; background: transparent; }
QTabBar { qproperty-drawBase: 0; }
QTabBar::tab {
    background: #dfe7e3; color: #3b4a44;
    padding: 9px 18px; margin: 8px 4px 0 4px;
    border-radius: 9px; font-weight: bold;
}
QTabBar::tab:selected { background: #1f7a5a; color: #ffffff; }
QTabBar::tab:hover:!selected { background: #cdd9d3; }

QScrollArea#scroll, QWidget#listContainer { background: transparent; border: none; }
QLabel#emptyState { color: #8a9994; }
QLabel#cardText { color: #1d2b25; }

/* Counter cards (morning / evening) */
QFrame#counterCard {
    background: #ffffff; border-radius: 14px; border-right: 4px solid #1f7a5a;
}
QFrame#counterCard[done="true"] {
    background: #e9f6ef; border-right: 4px solid #2faa78;
}
QPushButton#countBtn {
    background: #1f7a5a; color: #ffffff; border: none;
    border-radius: 18px; padding: 0 14px;
}
QPushButton#countBtn:hover   { background: #25946d; }
QPushButton#countBtn:pressed { background: #155c43; }
QFrame#counterCard[done="true"] QPushButton#countBtn { background: #2faa78; }
QLabel#infoBadge { color: #1f7a5a; }
QCheckBox#doneCheck { color: #3b4a44; spacing: 6px; }
QCheckBox#doneCheck::indicator { width: 20px; height: 20px; border-radius: 6px;
    border: 2px solid #b9c6c0; background: #ffffff; }
QCheckBox#doneCheck::indicator:checked { background: #2faa78; border-color: #2faa78; }

/* Hadith cards */
QFrame#hadithCard {
    background: #ffffff; border-radius: 14px; border-right: 4px solid #c8a85a;
}
QLabel#hadithNum {
    background: #1f7a5a; color: #ffffff; border-radius: 19px;
}
QLabel#hadithTitle { color: #155c43; }
QPushButton#explToggle {
    background: transparent; color: #1f7a5a; border: none;
    text-align: right; padding: 2px 0;
}
QPushButton#explToggle:hover { color: #25946d; }
QLabel#explText {
    color: #44524c; background: #f3f7f5; border-radius: 10px; padding: 12px;
    line-height: 150%;
}

/* My azkar (simple cards + add bar) */
QFrame#simpleCard {
    background: #ffffff; border-radius: 14px; border-right: 4px solid #1f7a5a;
}
QPushButton#cardDelete {
    background: transparent; color: #9aa6a0; border: none;
    border-radius: 17px; font-size: 15px;
}
QPushButton#cardDelete:hover { background: #fdecea; color: #d33b30; }
QFrame#addBar { background: #ffffff; border-top: 1px solid #dfe6e2; }
QLineEdit#addInput {
    background: #f4f6f5; border: 1px solid #dfe6e2; border-radius: 10px;
    padding: 10px 12px; color: #1d2b25;
}
QLineEdit#addInput:focus { border: 1px solid #1f7a5a; background: #ffffff; }
QPushButton#addButton {
    background: #1f7a5a; color: #ffffff; border: none;
    border-radius: 10px; padding: 10px 22px;
}
QPushButton#addButton:hover   { background: #25946d; }
QPushButton#addButton:pressed { background: #155c43; }

/* Footer */
QLabel#footer {
    color: #155c43; background: #e3ece8;
    border-top: 1px solid #d3ded8; padding: 10px;
}

/* Scrollbar */
QScrollBar:vertical { background: transparent; width: 10px; margin: 4px; }
QScrollBar::handle:vertical { background: #c3d2cb; border-radius: 5px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #1f7a5a; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""


class MainWindow(QMainWindow):
    def __init__(self, icon: QIcon | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(APP_DISPLAY_NAME)
        if icon is not None:
            self.setWindowIcon(icon)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.resize(560, 720)
        self.setMinimumSize(440, 520)
        self.setStyleSheet(_STYLE)

        central = QWidget()
        central.setObjectName("central")
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())

        tabs = QTabWidget()
        tabs.setObjectName("tabs")
        tabs.setDocumentMode(True)
        tabs.addTab(AzkarCounterPage("morning_azkar.json"), "أذكار الصباح")
        tabs.addTab(AzkarCounterPage("evening_azkar.json"), "أذكار المساء")
        tabs.addTab(HadithPage("arbaeen_nawawi.json"), "الأربعون النووية")
        tabs.addTab(MyAzkarPage(), "أذكاري")
        root.addWidget(tabs, 1)

        footer = QLabel(FOOTER_TEXT)
        footer.setObjectName("footer")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setFont(rtl.arabic_font(13, bold=True))
        root.addWidget(footer)

        self.setCentralWidget(central)

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("header")
        lay = QVBoxLayout(header)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(3)

        title = QLabel(APP_DISPLAY_NAME)
        title.setObjectName("headerTitle")
        title.setFont(rtl.arabic_font(22, bold=True))

        subtitle = QLabel("أذكار الصباح والمساء والأربعون النووية")
        subtitle.setObjectName("headerSubtitle")
        subtitle.setFont(rtl.arabic_font(11))

        lay.addWidget(title)
        lay.addWidget(subtitle)
        return header

    def reveal(self) -> None:
        """Show, un-minimise, and bring the window to the front."""
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event) -> None:
        # closing hides to the tray; the app keeps running
        event.ignore()
        self.hide()
