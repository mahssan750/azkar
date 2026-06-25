"""Card widgets used inside the main-window tabs.

- ``AzkarCounterCard`` — an azkar with a tap-to-count button and a "done"
  checkbox (used in the morning / evening tabs).
- ``HadithCard`` — a numbered hadith with an expandable explanation.
- ``SimpleAzkarCard`` — text + delete (used in the "My azkar" tab).
"""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from . import rtl

_ARABIC_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


def arabic_number(n: int) -> str:
    return str(n).translate(_ARABIC_DIGITS)


class AzkarCounterCard(QFrame):
    def __init__(self, text: str, target: int, virtue: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("counterCard")
        self._target = max(1, int(target))
        self._current = 0
        self._done = False

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        self._text = QLabel(text)
        self._text.setObjectName("cardText")
        self._text.setWordWrap(True)
        self._text.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self._text.setFont(rtl.arabic_font(14))
        self._text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        root.addWidget(self._text)

        row = QHBoxLayout()
        row.setSpacing(10)

        self._count_btn = QPushButton()
        self._count_btn.setObjectName("countBtn")
        self._count_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._count_btn.setFixedHeight(36)
        self._count_btn.setMinimumWidth(104)
        self._count_btn.setFont(rtl.arabic_font(12, bold=True))
        self._count_btn.clicked.connect(self._increment)
        row.addWidget(self._count_btn, 0)

        if virtue:
            info = QLabel("ⓘ")
            info.setObjectName("infoBadge")
            info.setToolTip(virtue)
            info.setFont(rtl.arabic_font(13))
            row.addWidget(info, 0)

        row.addStretch(1)

        self._check = QCheckBox("تم")
        self._check.setObjectName("doneCheck")
        self._check.setCursor(Qt.CursorShape.PointingHandCursor)
        self._check.setFont(rtl.arabic_font(12))
        self._check.toggled.connect(self._on_check)
        row.addWidget(self._check, 0)

        root.addLayout(row)

        # opacity-pulse animation on each tap
        self._fx = QGraphicsOpacityEffect(self._count_btn)
        self._count_btn.setGraphicsEffect(self._fx)
        self._fx.setOpacity(1.0)
        self._pulse = QPropertyAnimation(self._fx, b"opacity", self)
        self._pulse.setDuration(180)
        self._pulse.setStartValue(0.35)
        self._pulse.setEndValue(1.0)
        self._pulse.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._refresh()

    def _increment(self) -> None:
        if self._done:
            return
        self._current += 1
        self._pulse.stop()
        self._pulse.start()
        if self._current >= self._target:
            self._set_done(True)
        self._refresh()

    def _on_check(self, checked: bool) -> None:
        if checked and not self._done:
            self._current = self._target
            self._set_done(True)
            self._refresh()
        elif not checked and self._done:
            self._current = 0
            self._set_done(False)
            self._refresh()

    def _set_done(self, done: bool) -> None:
        self._done = done
        self.setProperty("done", done)
        self.style().unpolish(self)
        self.style().polish(self)
        self._check.blockSignals(True)
        self._check.setChecked(done)
        self._check.blockSignals(False)

    def _refresh(self) -> None:
        if self._done:
            self._count_btn.setText("✓ تم")
        else:
            self._count_btn.setText(f"{arabic_number(self._current)} / {arabic_number(self._target)}")


class HadithCard(QFrame):
    def __init__(self, number: int, text: str, explanation: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("hadithCard")

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        top = QHBoxLayout()
        top.setSpacing(10)
        badge = QLabel(arabic_number(number))
        badge.setObjectName("hadithNum")
        badge.setFixedSize(38, 38)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFont(rtl.arabic_font(14, bold=True))
        title = QLabel(f"الحديث {arabic_number(number)}")
        title.setObjectName("hadithTitle")
        title.setFont(rtl.arabic_font(13, bold=True))
        top.addWidget(badge, 0)
        top.addWidget(title, 0)
        top.addStretch(1)
        root.addLayout(top)

        body = QLabel(text)
        body.setObjectName("cardText")
        body.setWordWrap(True)
        body.setAlignment(Qt.AlignmentFlag.AlignRight)
        body.setFont(rtl.arabic_font(14))
        body.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        root.addWidget(body)

        if explanation:
            self._toggle = QPushButton("◂ الشرح والفوائد")
            self._toggle.setObjectName("explToggle")
            self._toggle.setCursor(Qt.CursorShape.PointingHandCursor)
            self._toggle.setFont(rtl.arabic_font(11, bold=True))
            self._toggle.clicked.connect(self._toggle_explanation)

            self._expl = QLabel(explanation)
            self._expl.setObjectName("explText")
            self._expl.setWordWrap(True)
            self._expl.setAlignment(Qt.AlignmentFlag.AlignRight)
            self._expl.setFont(rtl.arabic_font(12))
            self._expl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            self._expl.setVisible(False)

            root.addWidget(self._toggle)
            root.addWidget(self._expl)

    def _toggle_explanation(self) -> None:
        visible = not self._expl.isVisible()
        self._expl.setVisible(visible)
        self._toggle.setText(("▾ " if visible else "◂ ") + "الشرح والفوائد")


class SimpleAzkarCard(QFrame):
    def __init__(self, text: str, on_delete: Callable[[str], None], parent=None):
        super().__init__(parent)
        self.setObjectName("simpleCard")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        label = QLabel(text)
        label.setObjectName("cardText")
        label.setWordWrap(True)
        label.setFont(rtl.arabic_font(15))
        label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        delete = QPushButton("✕")
        delete.setObjectName("cardDelete")
        delete.setToolTip("حذف")
        delete.setCursor(Qt.CursorShape.PointingHandCursor)
        delete.setFixedSize(34, 34)
        delete.clicked.connect(lambda: on_delete(text))

        layout.addWidget(label, 1)
        layout.addWidget(delete, 0, Qt.AlignmentFlag.AlignTop)
