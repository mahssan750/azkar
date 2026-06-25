"""The modern main window: a scrollable list of azkar cards with an add bar.

Inspired by modern azkar apps — a green header, white rounded cards, and a
bottom input to add new Arabic text that is saved and shown immediately.
"""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .. import APP_DISPLAY_NAME
from ..content.user_store import UserAzkarStore
from . import rtl

_STYLE = """
QWidget#central { background: #eef2f0; }
QFrame#header {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #1f7a5a, stop:1 #155c43);
}
QLabel#headerTitle    { color: #ffffff; }
QLabel#headerSubtitle { color: #cfe9df; }
QScrollArea#scroll, QWidget#listContainer { background: transparent; border: none; }
QLabel#emptyState { color: #8a9994; }
QFrame#azkarCard {
    background: #ffffff;
    border-radius: 14px;
    border-right: 4px solid #1f7a5a;
}
QLabel#cardText { color: #1d2b25; }
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
QScrollBar:vertical { background: transparent; width: 10px; margin: 4px; }
QScrollBar::handle:vertical { background: #c3d2cb; border-radius: 5px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #1f7a5a; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""


class AzkarCard(QFrame):
    def __init__(self, text: str, on_delete: Callable[[str], None], parent=None):
        super().__init__(parent)
        self.setObjectName("azkarCard")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        label = QLabel(text)
        label.setObjectName("cardText")
        label.setWordWrap(True)
        label.setFont(rtl.arabic_font(15))
        label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        delete = QPushButton("✕")  # ✕
        delete.setObjectName("cardDelete")
        delete.setToolTip("حذف")
        delete.setCursor(Qt.CursorShape.PointingHandCursor)
        delete.setFixedSize(34, 34)
        delete.clicked.connect(lambda: on_delete(text))

        layout.addWidget(label, 1)
        layout.addWidget(delete, 0, Qt.AlignmentFlag.AlignTop)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 38))
        self.setGraphicsEffect(shadow)


class MainWindow(QMainWindow):
    def __init__(self, icon: QIcon | None = None, parent=None):
        super().__init__(parent)
        self.store = UserAzkarStore()

        self.setWindowTitle(APP_DISPLAY_NAME)
        if icon is not None:
            self.setWindowIcon(icon)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.resize(520, 660)
        self.setMinimumSize(420, 480)
        self.setStyleSheet(_STYLE)

        central = QWidget()
        central.setObjectName("central")
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        root.addWidget(self._build_scroll(), 1)
        root.addWidget(self._build_add_bar())

        self.setCentralWidget(central)
        self._reload()

    # --- construction -----------------------------------------------------
    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("header")
        lay = QVBoxLayout(header)
        lay.setContentsMargins(24, 22, 24, 22)
        lay.setSpacing(4)

        title = QLabel(APP_DISPLAY_NAME)
        title.setObjectName("headerTitle")
        title.setFont(rtl.arabic_font(22, bold=True))

        self._subtitle = QLabel()
        self._subtitle.setObjectName("headerSubtitle")
        self._subtitle.setFont(rtl.arabic_font(11))

        lay.addWidget(title)
        lay.addWidget(self._subtitle)
        return header

    def _build_scroll(self) -> QScrollArea:
        self._scroll = QScrollArea()
        self._scroll.setObjectName("scroll")
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._list_container = QWidget()
        self._list_container.setObjectName("listContainer")
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(18, 18, 18, 18)
        self._list_layout.setSpacing(12)
        self._list_layout.addStretch(1)

        self._empty = QLabel("لا توجد أذكار بعد.\nأضف ذِكراً من الأسفل لتظهر هنا.")
        self._empty.setObjectName("emptyState")
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty.setFont(rtl.arabic_font(13))

        self._scroll.setWidget(self._list_container)
        return self._scroll

    def _build_add_bar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("addBar")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(10)

        self._input = QLineEdit()
        self._input.setObjectName("addInput")
        self._input.setFont(rtl.arabic_font(13))
        self._input.setPlaceholderText("أضف ذِكراً جديداً...")
        self._input.returnPressed.connect(self._on_add)

        add_button = QPushButton("إضافة")
        add_button.setObjectName("addButton")
        add_button.setFont(rtl.arabic_font(13, bold=True))
        add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        add_button.clicked.connect(self._on_add)

        lay.addWidget(self._input, 1)
        lay.addWidget(add_button, 0)
        return bar

    # --- behaviour --------------------------------------------------------
    def _clear_cards(self) -> None:
        # remove everything except the trailing stretch (last item)
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def _reload(self) -> None:
        self._clear_cards()
        items = self.store.all()
        if items:
            self._empty.setParent(None)
            for text in items:
                card = AzkarCard(text, self._on_delete)
                self._list_layout.insertWidget(self._list_layout.count() - 1, card)
        else:
            self._list_layout.insertWidget(0, self._empty)
        self._subtitle.setText(f"عدد الأذكار: {len(items)}")

    def _on_add(self) -> None:
        text = self._input.text().strip()
        if not text:
            return
        if self.store.add(text):
            self._input.clear()
            self._reload()
            bar = self._scroll.verticalScrollBar()
            bar.setValue(bar.maximum())

    def _on_delete(self, text: str) -> None:
        self.store.remove(text)
        self._reload()

    def reveal(self) -> None:
        """Show, un-minimise, and bring the window to the front."""
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event) -> None:
        # closing just hides to the tray; the app keeps running
        event.ignore()
        self.hide()
