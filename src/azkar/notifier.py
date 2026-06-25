"""Native Windows toast notifications, via ``windows-toasts`` (WinRT).

Falls back to a system-tray balloon if the toast backend is unavailable, so a
reminder is never silently lost.
"""
from __future__ import annotations

from typing import Optional

from . import APP_DISPLAY_NAME


class Notifier:
    def __init__(
        self,
        app_name: str = APP_DISPLAY_NAME,
        icon_path: Optional[str] = None,
        tray=None,
    ):
        self._app_name = app_name
        self._icon_path = icon_path
        self._tray = tray  # QSystemTrayIcon, used only as a fallback
        self._toaster = None
        try:
            from windows_toasts import WindowsToaster

            self._toaster = WindowsToaster(app_name)
        except Exception:
            self._toaster = None

    def notify(self, title: str, body: str) -> None:
        if self._toaster is not None and self._show_native(title, body):
            return
        self._show_tray(title, body)

    def _show_native(self, title: str, body: str) -> bool:
        try:
            from windows_toasts import Toast, ToastDisplayImage, ToastImagePosition

            toast = Toast()
            toast.text_fields = [title, body] if title else [body]
            if self._icon_path:
                try:
                    toast.AddImage(
                        ToastDisplayImage.fromPath(
                            self._icon_path,
                            position=ToastImagePosition.AppLogo,
                            circleCrop=True,
                        )
                    )
                except Exception:
                    pass
            self._toaster.show_toast(toast)
            return True
        except Exception:
            return False

    def _show_tray(self, title: str, body: str) -> None:
        if self._tray is not None:
            try:
                self._tray.showMessage(title or self._app_name, body)
            except Exception:
                pass
