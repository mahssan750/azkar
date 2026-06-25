"""The pages that fill the main-window tabs.

Each page is a scrollable list. ``FadePage`` adds a one-time fade-in the first
time a tab is shown (the effect is removed afterwards so scrolling stays fast).
"""
from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..content.dataset import load_dataset
from ..content.user_store import UserAzkarStore
from . import rtl
from .cards import AzkarCounterCard, HadithCard, SimpleAzkarCard


def _make_scroll() -> tuple[QScrollArea, QVBoxLayout]:
    scroll = QScrollArea()
    scroll.setObjectName("scroll")
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    container = QWidget()
    container.setObjectName("listContainer")
    layout = QVBoxLayout(container)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(12)
    layout.addStretch(1)
    scroll.setWidget(container)
    return scroll, layout


class FadePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._faded = False

    def showEvent(self, event):
        super().showEvent(event)
        if self._faded:
            return
        self._faded = True
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(280)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.finished.connect(lambda: self.setGraphicsEffect(None))
        self._fade_anim = anim  # keep a reference
        anim.start()


class AzkarCounterPage(FadePage):
    """Morning / evening azkar with counters and checkboxes."""

    def __init__(self, filename: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        scroll, lst = _make_scroll()
        layout.addWidget(scroll)

        for item in load_dataset(filename):
            text = (item.get("text") or "").strip()
            if not text:
                continue
            card = AzkarCounterCard(text, item.get("count", 1), item.get("virtue", ""))
            lst.insertWidget(lst.count() - 1, card)


class HadithPage(FadePage):
    """The 40 hadith of an-Nawawi."""

    def __init__(self, filename: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        scroll, lst = _make_scroll()
        layout.addWidget(scroll)

        for item in load_dataset(filename):
            text = (item.get("text") or "").strip()
            if not text:
                continue
            card = HadithCard(item.get("number", 0), text, item.get("explanation", ""))
            lst.insertWidget(lst.count() - 1, card)


class MyAzkarPage(FadePage):
    """User-added azkar: add via the bottom bar, delete per card."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.store = UserAzkarStore()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._scroll, self._list = _make_scroll()
        layout.addWidget(self._scroll, 1)

        self._empty = QLabel("لا توجد أذكار بعد.\nأضف ذِكراً من الأسفل لتظهر هنا.")
        self._empty.setObjectName("emptyState")
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty.setFont(rtl.arabic_font(13))

        bar = QFrame()
        bar.setObjectName("addBar")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(16, 14, 16, 14)
        bar_layout.setSpacing(10)
        self._input = QLineEdit()
        self._input.setObjectName("addInput")
        self._input.setFont(rtl.arabic_font(13))
        self._input.setPlaceholderText("أضف ذِكراً جديداً...")
        self._input.returnPressed.connect(self._on_add)
        add_btn = QPushButton("إضافة")
        add_btn.setObjectName("addButton")
        add_btn.setFont(rtl.arabic_font(13, bold=True))
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._on_add)
        bar_layout.addWidget(self._input, 1)
        bar_layout.addWidget(add_btn, 0)
        layout.addWidget(bar)

        self._reload()

    def _clear(self) -> None:
        while self._list.count() > 1:
            item = self._list.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

    def _reload(self) -> None:
        self._clear()
        items = self.store.all()
        if items:
            self._empty.setParent(None)
            for text in items:
                self._list.insertWidget(self._list.count() - 1, SimpleAzkarCard(text, self._on_delete))
        else:
            self._list.insertWidget(0, self._empty)

    def _on_add(self) -> None:
        text = self._input.text().strip()
        if text and self.store.add(text):
            self._input.clear()
            self._reload()
            bar = self._scroll.verticalScrollBar()
            bar.setValue(bar.maximum())

    def _on_delete(self, text: str) -> None:
        self.store.remove(text)
        self._reload()
