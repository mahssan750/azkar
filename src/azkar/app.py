"""Application entry point: wires the tray, scheduler, and reminders together.

The app has no main window — it lives in the system tray. On launch it shows
the startup dialog and begins the recurring tasbih toast.
"""
from __future__ import annotations

import sys

from PySide6.QtCore import QSharedMemory, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from . import APP_DISPLAY_NAME, APP_ID, APP_NAME, autostart
from .config import load_settings, save_settings
from .notifier import Notifier
from .paths import icon_png_path
from .reminders.startup_dialog import show_startup_dialog
from .reminders.tasbih_toast import TasbihToastReminder
from .scheduler import ReminderScheduler
from .tray import TrayIcon
from .ui.icon import make_icon, save_png
from .ui.main_window import MainWindow
from .ui.rtl import apply_rtl


class AzkarApp:
    def __init__(self, app: QApplication):
        self.app = app
        self.settings = load_settings()
        self.window: MainWindow | None = None

        self.icon = make_icon()
        app.setWindowIcon(self.icon)

        # PNG used as the toast logo (best-effort).
        self._icon_png = str(icon_png_path()) if save_png(icon_png_path()) else None

        self.tray = TrayIcon(
            self.icon,
            APP_DISPLAY_NAME,
            callbacks={
                "open_window": self.open_window,
                "remind_now": self.remind_now,
                "set_paused": self.set_paused,
                "show_startup": self.show_startup,
                "set_autostart": self.set_autostart,
                "quit": self.quit,
            },
            paused=False,
            autostart=autostart.is_enabled(),
        )
        self.tray.show()

        self.notifier = Notifier(APP_DISPLAY_NAME, icon_path=self._icon_png, tray=self.tray)

        self.scheduler = ReminderScheduler()
        self.tasbih = TasbihToastReminder(self.notifier, self.settings)
        if self.settings.tasbih_reminder_enabled:
            self.scheduler.add_interval_reminder(
                self.tasbih.name, self.settings.interval_ms, self.tasbih.run
            )

        # Honour the saved "run at login" preference.
        autostart.sync(self.settings.run_at_login)

        # Show the login dialog once the tray has settled.
        if self.settings.startup_dialog_enabled:
            QTimer.singleShot(400, self.show_startup)

    # --- tray callbacks ---------------------------------------------------
    def open_window(self) -> None:
        if self.window is None:
            self.window = MainWindow(self.icon)
        self.window.reveal()

    def remind_now(self) -> None:
        self.tasbih.run()

    def set_paused(self, paused: bool) -> None:
        if paused:
            self.scheduler.pause()
        else:
            self.scheduler.resume()

    def show_startup(self) -> None:
        show_startup_dialog(self.icon)

    def set_autostart(self, enabled: bool) -> None:
        autostart.sync(enabled)
        self.settings.run_at_login = enabled
        save_settings(self.settings)

    def quit(self) -> None:
        self.tray.hide()
        self.app.quit()


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_DISPLAY_NAME)
    app.setQuitOnLastWindowClosed(False)

    # Make Windows attribute toasts (and taskbar) to this app, not "python".
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
    except Exception:
        pass

    # Single-instance guard — keep the handle alive for the whole process.
    singleton = QSharedMemory(f"{APP_NAME}-singleton")
    if not singleton.create(1):
        QMessageBox.information(None, APP_DISPLAY_NAME, "البرنامج يعمل بالفعل.")
        return 0
    app._azkar_singleton = singleton  # type: ignore[attr-defined]

    apply_rtl(app)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, APP_DISPLAY_NAME, "شريط النظام (System Tray) غير متوفر.")
        return 1

    app._azkar = AzkarApp(app)  # type: ignore[attr-defined]  # keep a strong ref
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
