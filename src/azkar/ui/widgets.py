"""Reusable styled widgets.

``ArabicMessageDialog`` is a centered, RTL, always-on-top message box with a
single button. It backs the startup reminder today and is the base for future
azkar / hadith / Qur'an pop-ups.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from . import rtl

_STYLESHEET = """
QDialog#azkarDialog { background: #0f1c17; }
QLabel#azkarText { color: #f3efe2; padding: 6px; }
QPushButton#azkarButton {
    background: #1f7a5a;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 10px 28px;
}
QPushButton#azkarButton:hover  { background: #25946d; }
QPushButton#azkarButton:pressed { background: #155c43; }
"""


class ArabicMessageDialog(QDialog):
    def __init__(
        self,
        text: str,
        *,
        title: str = "أذكار",
        button_text: str = "تم",
        icon: QIcon | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("azkarDialog")
        self.setWindowTitle(title)
        if icon is not None:
            self.setWindowIcon(icon)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setMinimumWidth(460)
        self.setStyleSheet(_STYLESHEET)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 24)
        layout.setSpacing(24)

        label = QLabel(text)
        label.setObjectName("azkarText")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(rtl.arabic_font(20, bold=True))
        layout.addWidget(label)

        row = QHBoxLayout()
        row.addStretch(1)
        button = QPushButton(button_text)
        button.setObjectName("azkarButton")
        button.setFont(rtl.arabic_font(13, bold=True))
        button.setMinimumWidth(130)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setDefault(True)
        button.clicked.connect(self.accept)
        row.addWidget(button)
        row.addStretch(1)
        layout.addLayout(row)

    def center_on_screen(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        self.adjustSize()
        geo = screen.availableGeometry()
        self.move(
            geo.center().x() - self.width() // 2,
            geo.center().y() - self.height() // 2,
        )
