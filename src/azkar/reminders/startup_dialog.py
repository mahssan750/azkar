"""The login reminder: a modal dialog shown right after the app starts.

Reminds you to say "بسم الله" and to set your intention for the work ahead.
"""
from __future__ import annotations

from PySide6.QtGui import QIcon

from .. import APP_DISPLAY_NAME
from ..ui.widgets import ArabicMessageDialog

STARTUP_TEXT = "لا تنسى أن تقول بسم الله\nولا تنسى أن تحضر النية لهذا العمل"


def show_startup_dialog(icon: QIcon | None = None) -> None:
    dialog = ArabicMessageDialog(
        STARTUP_TEXT,
        title=APP_DISPLAY_NAME,
        button_text="آمين",
        icon=icon,
    )
    dialog.center_on_screen()
    dialog.exec()
