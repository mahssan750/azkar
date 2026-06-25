"""The settings dialog: theme, font size, and reminder options."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
)

from .. import APP_DISPLAY_NAME
from ..config import Settings
from . import rtl, theme

_MIN_SCALE, _MAX_SCALE, _STEP = 0.7, 1.6, 0.1


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, icon: QIcon | None = None, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsDialog")
        self.setWindowTitle(f"{APP_DISPLAY_NAME} — الإعدادات")
        if icon is not None:
            self.setWindowIcon(icon)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setMinimumWidth(440)
        self.setStyleSheet(theme.settings_qss())

        self._scale = float(settings.font_scale)

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 18)
        root.setSpacing(16)

        root.addWidget(self._appearance_group(settings))
        root.addWidget(self._font_group())
        root.addWidget(self._reminder_group(settings))
        root.addLayout(self._buttons())

    # --- groups -----------------------------------------------------------
    def _appearance_group(self, settings: Settings) -> QGroupBox:
        box = QGroupBox("المظهر")
        box.setFont(rtl.arabic_font(13, bold=True))
        lay = QHBoxLayout(box)
        lay.setSpacing(18)
        self._light = QRadioButton("فاتح")
        self._dark = QRadioButton("داكن")
        for rb in (self._light, self._dark):
            rb.setFont(rtl.arabic_font(12))
        self._theme_group = QButtonGroup(self)
        self._theme_group.addButton(self._light)
        self._theme_group.addButton(self._dark)
        (self._dark if settings.theme == "dark" else self._light).setChecked(True)
        lay.addWidget(self._light)
        lay.addWidget(self._dark)
        lay.addStretch(1)
        return box

    def _font_group(self) -> QGroupBox:
        box = QGroupBox("حجم الخط")
        box.setFont(rtl.arabic_font(13, bold=True))
        lay = QHBoxLayout(box)
        lay.setSpacing(12)
        minus = QPushButton("ـA")
        plus = QPushButton("A")
        for b in (minus, plus):
            b.setObjectName("stepBtn")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
        minus.setFont(rtl.arabic_font(11, bold=True))
        plus.setFont(rtl.arabic_font(15, bold=True))
        minus.clicked.connect(lambda: self._bump(-_STEP))
        plus.clicked.connect(lambda: self._bump(+_STEP))
        self._scale_label = QLabel()
        self._scale_label.setObjectName("scaleValue")
        self._scale_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scale_label.setMinimumWidth(64)
        self._scale_label.setFont(rtl.arabic_font(13, bold=True))
        lay.addWidget(plus)
        lay.addWidget(self._scale_label)
        lay.addWidget(minus)
        lay.addStretch(1)
        self._update_scale_label()
        return box

    def _reminder_group(self, settings: Settings) -> QGroupBox:
        box = QGroupBox("التذكير")
        box.setFont(rtl.arabic_font(13, bold=True))
        lay = QVBoxLayout(box)
        lay.setSpacing(12)

        self._enabled = QCheckBox("تفعيل التذكير الدوري")
        self._enabled.setFont(rtl.arabic_font(12))
        self._enabled.setChecked(settings.tasbih_reminder_enabled)
        lay.addWidget(self._enabled)

        row = QHBoxLayout()
        row.setSpacing(8)
        label = QLabel("كل")
        label.setFont(rtl.arabic_font(12))
        self._interval = QSpinBox()
        self._interval.setRange(1, 240)
        self._interval.setValue(max(1, settings.reminder_interval_minutes))
        self._interval.setFont(rtl.arabic_font(12))
        self._interval.setFixedWidth(90)
        minutes = QLabel("دقيقة")
        minutes.setFont(rtl.arabic_font(12))
        row.addWidget(label)
        row.addWidget(self._interval)
        row.addWidget(minutes)
        row.addStretch(1)
        lay.addLayout(row)

        text_label = QLabel("نص التذكير")
        text_label.setFont(rtl.arabic_font(12))
        lay.addWidget(text_label)
        self._text = QLineEdit(settings.tasbih_text)
        self._text.setFont(rtl.arabic_font(12))
        lay.addWidget(self._text)

        self._sound = QCheckBox("تشغيل صوت التذكير")
        self._sound.setFont(rtl.arabic_font(12))
        self._sound.setChecked(settings.reminder_sound_enabled)
        lay.addWidget(self._sound)
        return box

    def _buttons(self) -> QHBoxLayout:
        row = QHBoxLayout()
        save = QPushButton("حفظ")
        save.setObjectName("primaryBtn")
        save.setFont(rtl.arabic_font(13, bold=True))
        save.setCursor(Qt.CursorShape.PointingHandCursor)
        save.setDefault(True)
        save.clicked.connect(self.accept)
        cancel = QPushButton("إلغاء")
        cancel.setObjectName("ghostBtn")
        cancel.setFont(rtl.arabic_font(13))
        cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel.clicked.connect(self.reject)
        row.addWidget(save)
        row.addWidget(cancel)
        row.addStretch(1)
        return row

    # --- font helpers -----------------------------------------------------
    def _bump(self, delta: float) -> None:
        self._scale = round(min(_MAX_SCALE, max(_MIN_SCALE, self._scale + delta)), 2)
        self._update_scale_label()

    def _update_scale_label(self) -> None:
        self._scale_label.setText(f"{round(self._scale * 100)}%")

    # --- result -----------------------------------------------------------
    def get_values(self) -> dict:
        return {
            "theme": "dark" if self._dark.isChecked() else "light",
            "font_scale": self._scale,
            "reminder_enabled": self._enabled.isChecked(),
            "interval_minutes": self._interval.value(),
            "reminder_text": self._text.text().strip() or self._text.placeholderText(),
            "sound_enabled": self._sound.isChecked(),
        }
