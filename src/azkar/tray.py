"""The system-tray icon and its right-click menu (Arabic).

Wired with plain callbacks so it stays decoupled from the app internals.
"""
from __future__ import annotations

from typing import Callable

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

Callbacks = dict[str, Callable]


class TrayIcon(QSystemTrayIcon):
    def __init__(
        self,
        icon: QIcon,
        app_name: str,
        callbacks: Callbacks,
        *,
        paused: bool,
        autostart: bool,
        sound: bool = True,
        parent=None,
    ):
        super().__init__(icon, parent)
        self._callbacks = callbacks
        self.setToolTip(app_name)

        menu = QMenu()

        open_window = QAction("إظهار النافذة الرئيسية", menu)
        open_window.triggered.connect(callbacks["open_window"])
        menu.addAction(open_window)

        menu.addSeparator()

        remind_now = QAction("تذكير الآن", menu)
        remind_now.triggered.connect(callbacks["remind_now"])
        menu.addAction(remind_now)

        self._pause_action = QAction("إيقاف التذكير", menu)
        self._pause_action.setCheckable(True)
        self._pause_action.setChecked(paused)
        self._pause_action.toggled.connect(self._on_pause_toggled)
        menu.addAction(self._pause_action)

        self._sound_action = QAction("صوت التذكير", menu)
        self._sound_action.setCheckable(True)
        self._sound_action.setChecked(sound)
        self._sound_action.toggled.connect(callbacks["set_sound"])
        menu.addAction(self._sound_action)

        show_startup = QAction("إظهار رسالة البداية", menu)
        show_startup.triggered.connect(callbacks["show_startup"])
        menu.addAction(show_startup)

        menu.addSeparator()

        autostart_action = QAction("بدء التشغيل مع ويندوز", menu)
        autostart_action.setCheckable(True)
        autostart_action.setChecked(autostart)
        autostart_action.toggled.connect(callbacks["set_autostart"])
        menu.addAction(autostart_action)

        menu.addSeparator()

        quit_action = QAction("خروج", menu)
        quit_action.triggered.connect(callbacks["quit"])
        menu.addAction(quit_action)

        self.setContextMenu(menu)
        self.activated.connect(self._on_activated)

    def _on_pause_toggled(self, checked: bool) -> None:
        self._pause_action.setText("استئناف التذكير" if checked else "إيقاف التذكير")
        self._callbacks["set_paused"](checked)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._callbacks["open_window"]()
