"""Application entry point: wires the tray, scheduler, and reminders together.

The app lives in the system tray. A manual launch opens the main window; a login
launch (``--startup``) shows the startup reminder dialog instead. The recurring
tasbih toast runs in the background either way.
"""
from __future__ import annotations

import sys

from PySide6.QtCore import QSharedMemory, QTimer
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox, QSystemTrayIcon

from . import APP_DISPLAY_NAME, APP_ID, APP_NAME, autostart
from . import hijri as hijri_mod
from .autostart import STARTUP_FLAG
from .clock_scheduler import ClockScheduler, parse_hhmm
from .config import load_settings, save_settings
from .notifier import Notifier
from .sound import play_knock
from .paths import icon_png_path
from .reminders.startup_dialog import show_startup_dialog
from .reminders.tasbih_toast import TasbihToastReminder
from .scheduler import ReminderScheduler
from .tray import TrayIcon
from .ui import rtl, theme
from .ui.icon import make_icon, save_png
from .ui.main_window import MainWindow
from .ui.rtl import apply_rtl
from .ui.settings_dialog import SettingsDialog


class AzkarApp:
    def __init__(self, app: QApplication, *, startup: bool = False):
        self.app = app
        self.settings = load_settings()
        self.window: MainWindow | None = None

        # appearance must be set before any window is built
        theme.set_theme(self.settings.theme)
        rtl.set_font_scale(self.settings.font_scale)

        self.icon = make_icon()
        app.setWindowIcon(self.icon)

        # PNG used as the toast logo (best-effort).
        self._icon_png = str(icon_png_path()) if save_png(icon_png_path()) else None

        self.tray = TrayIcon(
            self.icon,
            APP_DISPLAY_NAME,
            callbacks={
                "open_window": self.open_window,
                "open_settings": self.open_settings,
                "remind_now": self.remind_now,
                "set_paused": self.set_paused,
                "set_sound": self.set_sound,
                "show_startup": self.show_startup,
                "set_autostart": self.set_autostart,
                "quit": self.quit,
            },
            paused=False,
            autostart=autostart.is_enabled(),
            sound=self.settings.reminder_sound_enabled,
        )
        self.tray.show()

        self.notifier = Notifier(APP_DISPLAY_NAME, icon_path=self._icon_png, tray=self.tray)

        self.scheduler = ReminderScheduler()
        self.tasbih = TasbihToastReminder(self.notifier, self.settings)
        self.scheduler.add_interval_reminder(
            self.tasbih.name,
            self.settings.interval_ms,
            self.tasbih.run,
            enabled=self.settings.tasbih_reminder_enabled,
        )

        # Time-of-day reminders: morning/evening azkar, Thursday-evening salawat.
        self.clock = ClockScheduler()
        self._register_timed_reminders()

        # Hijri date: show immediately (local), then adjust online ~monthly.
        self._hijri_text = hijri_mod.format_hijri(self.settings.hijri_adjustment)
        self.hijri_sync = hijri_mod.HijriSync(self.settings, save_settings)
        self.hijri_sync.updated.connect(self._on_hijri_updated)
        self.hijri_sync.maybe_sync()

        # Honour the saved "run at login" preference.
        autostart.sync(self.settings.run_at_login)

        if startup:
            # Launched at login: show only the startup reminder; stay in the tray.
            if self.settings.startup_dialog_enabled:
                QTimer.singleShot(400, self.show_startup)
        else:
            # Launched manually (double-click): open the main window, no dialog.
            self.open_window()

    # --- scheduled reminders & hijri --------------------------------------
    def _register_timed_reminders(self) -> None:
        s = self.settings
        mh, mm = parse_hhmm(s.morning_azkar_reminder_time, (4, 50))
        self.clock.add_daily(
            "morning", mh, mm,
            lambda: self._notify("أذكار الصباح", "حان وقت أذكار الصباح"),
            enabled=s.morning_azkar_reminder_enabled,
        )
        eh, em = parse_hhmm(s.evening_azkar_reminder_time, (16, 0))
        self.clock.add_daily(
            "evening", eh, em,
            lambda: self._notify("أذكار المساء", "حان وقت أذكار المساء"),
            enabled=s.evening_azkar_reminder_enabled,
        )
        fh, fm = parse_hhmm(s.friday_salawat_time, (18, 0))
        self.clock.add_daily(
            "friday_salawat", fh, fm,
            lambda: self._notify(
                "ليلة الجمعة",
                "لا تنس الإكثار من الصلاة على النبي صلى الله عليه وسلم ليلة الجمعة ويومها",
            ),
            weekday=3,  # Thursday (Mon=0 .. Sun=6)
            enabled=s.friday_salawat_enabled,
        )

    def _notify(self, title: str, body: str) -> None:
        sound = self.settings.reminder_sound_enabled
        if sound:
            play_knock()
        self.notifier.notify(title, body, silent=sound)

    def _on_hijri_updated(self) -> None:
        self._hijri_text = hijri_mod.format_hijri(self.settings.hijri_adjustment)
        if self.window is not None:
            self.window.set_hijri(self._hijri_text)

    # --- tray callbacks ---------------------------------------------------
    def open_window(self) -> None:
        if self.window is None:
            self.window = MainWindow(
                self.icon, on_settings=self.open_settings, hijri_text=self._hijri_text
            )
        self.window.reveal()

    def open_settings(self) -> None:
        dialog = SettingsDialog(self.settings, icon=self.icon)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._apply_settings(dialog.get_values())

    def _apply_settings(self, values: dict) -> None:
        s = self.settings
        s.theme = values["theme"]
        s.font_scale = values["font_scale"]
        s.tasbih_reminder_enabled = values["reminder_enabled"]
        s.reminder_interval_minutes = values["interval_minutes"]
        s.tasbih_text = values["reminder_text"]
        s.reminder_sound_enabled = values["sound_enabled"]
        save_settings(s)

        # apply live
        theme.set_theme(s.theme)
        rtl.set_font_scale(s.font_scale)
        self.scheduler.set_interval(self.tasbih.name, s.interval_ms)
        self.scheduler.set_enabled(self.tasbih.name, s.tasbih_reminder_enabled)
        self.tray.set_sound_checked(s.reminder_sound_enabled)
        if self.window is not None:
            self.window.apply_appearance()

    def remind_now(self) -> None:
        self.tasbih.run()

    def set_paused(self, paused: bool) -> None:
        if paused:
            self.scheduler.pause()
        else:
            self.scheduler.resume()

    def set_sound(self, enabled: bool) -> None:
        self.settings.reminder_sound_enabled = enabled
        save_settings(self.settings)

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

    started_at_login = STARTUP_FLAG in sys.argv[1:]
    app._azkar = AzkarApp(app, startup=started_at_login)  # type: ignore[attr-defined]
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
