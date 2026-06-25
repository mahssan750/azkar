"""Light / dark theming for the main window and settings dialog.

A single QSS template is filled from a palette dict (``string.Template`` with
``$name`` placeholders, so the QSS ``{ }`` braces stay literal). The current
theme is a module-level value set from settings.
"""
from __future__ import annotations

from string import Template

_THEME = "light"

LIGHT = {
    "window_bg": "#eef2f0",
    "header_top": "#1f7a5a", "header_bottom": "#155c43",
    "header_title": "#ffffff", "header_sub": "#cfe9df",
    "tab_bg": "#dfe7e3", "tab_text": "#3b4a44",
    "tab_sel_bg": "#1f7a5a", "tab_sel_text": "#ffffff", "tab_hover": "#cdd9d3",
    "card_bg": "#ffffff", "card_text": "#1d2b25",
    "accent": "#1f7a5a", "accent_hover": "#25946d", "accent_press": "#155c43",
    "done_bg": "#e9f6ef", "done_accent": "#2faa78",
    "check_border": "#b9c6c0", "check_bg": "#ffffff", "check_checked": "#2faa78",
    "hadith_accent": "#c8a85a", "hadith_title": "#155c43",
    "expl_bg": "#f3f7f5", "expl_text": "#44524c",
    "delete_text": "#9aa6a0", "delete_hover_bg": "#fdecea", "delete_hover_text": "#d33b30",
    "addbar_bg": "#ffffff", "addbar_border": "#dfe6e2",
    "input_bg": "#f4f6f5", "input_border": "#dfe6e2", "input_text": "#1d2b25",
    "footer_bg": "#e3ece8", "footer_text": "#155c43", "footer_border": "#d3ded8",
    "scroll_handle": "#c3d2cb",
    "empty_text": "#8a9994", "info": "#1f7a5a", "hijri": "#fbe7bd",
}

DARK = {
    "window_bg": "#131d18",
    "header_top": "#186a4d", "header_bottom": "#0e1813",
    "header_title": "#ffffff", "header_sub": "#bfe0d2",
    "tab_bg": "#20302a", "tab_text": "#b9c6c0",
    "tab_sel_bg": "#2faa78", "tab_sel_text": "#0f1813", "tab_hover": "#2a3b34",
    "card_bg": "#1c2823", "card_text": "#e7efea",
    "accent": "#2faa78", "accent_hover": "#38c089", "accent_press": "#258a61",
    "done_bg": "#143a2c", "done_accent": "#2faa78",
    "check_border": "#45554d", "check_bg": "#1c2823", "check_checked": "#2faa78",
    "hadith_accent": "#c8a85a", "hadith_title": "#9fcdb8",
    "expl_bg": "#16221d", "expl_text": "#b9c8c1",
    "delete_text": "#8a978f", "delete_hover_bg": "#3a2422", "delete_hover_text": "#e1675c",
    "addbar_bg": "#16221d", "addbar_border": "#2a3b34",
    "input_bg": "#20302a", "input_border": "#34433b", "input_text": "#e7efea",
    "footer_bg": "#16221d", "footer_text": "#9fcdb8", "footer_border": "#243029",
    "scroll_handle": "#34433b",
    "empty_text": "#7d8c85", "info": "#2faa78", "hijri": "#f1d493",
}


def set_theme(name: str) -> None:
    global _THEME
    _THEME = "dark" if name == "dark" else "light"


def current_theme() -> str:
    return _THEME


def palette() -> dict:
    return DARK if _THEME == "dark" else LIGHT


_MAIN = Template("""
QWidget#central { background: $window_bg; }

QWidget#header {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 $header_top, stop:1 $header_bottom);
}
QLabel#headerTitle    { color: $header_title; }
QLabel#headerSubtitle { color: $header_sub; }
QPushButton#gearBtn { background: transparent; color: $header_title; border: none; font-size: 19px; }
QPushButton#gearBtn:hover { color: #ffffff; }

QTabWidget::pane { border: none; background: transparent; }
QTabBar { qproperty-drawBase: 0; }
QTabBar::tab {
    background: $tab_bg; color: $tab_text;
    padding: 9px 18px; margin: 8px 4px 0 4px;
    border-radius: 9px; font-weight: bold;
}
QTabBar::tab:selected { background: $tab_sel_bg; color: $tab_sel_text; }
QTabBar::tab:hover:!selected { background: $tab_hover; }

QScrollArea#scroll, QWidget#listContainer { background: transparent; border: none; }
QLabel#emptyState { color: $empty_text; }
QLabel#cardText { color: $card_text; }

QFrame#counterCard { background: $card_bg; border-radius: 14px; border-right: 4px solid $accent; }
QFrame#counterCard[done="true"] { background: $done_bg; border-right: 4px solid $done_accent; }
QPushButton#countBtn { background: $accent; color: #ffffff; border: none; border-radius: 18px; padding: 0 14px; }
QPushButton#countBtn:hover   { background: $accent_hover; }
QPushButton#countBtn:pressed { background: $accent_press; }
QFrame#counterCard[done="true"] QPushButton#countBtn { background: $done_accent; }
QLabel#infoBadge { color: $info; }
QCheckBox#doneCheck { color: $card_text; spacing: 6px; }
QCheckBox#doneCheck::indicator { width: 20px; height: 20px; border-radius: 6px;
    border: 2px solid $check_border; background: $check_bg; }
QCheckBox#doneCheck::indicator:checked { background: $check_checked; border-color: $check_checked; }

QFrame#hadithCard { background: $card_bg; border-radius: 14px; border-right: 4px solid $hadith_accent; }
QLabel#hadithNum { background: $accent; color: #ffffff; border-radius: 19px; }
QLabel#hadithTitle { color: $hadith_title; }
QPushButton#explToggle { background: transparent; color: $accent; border: none; text-align: right; padding: 2px 0; }
QPushButton#explToggle:hover { color: $accent_hover; }
QLabel#explText { color: $expl_text; background: $expl_bg; border-radius: 10px; padding: 12px; }

QFrame#simpleCard { background: $card_bg; border-radius: 14px; border-right: 4px solid $accent; }
QPushButton#cardDelete { background: transparent; color: $delete_text; border: none; border-radius: 17px; font-size: 15px; }
QPushButton#cardDelete:hover { background: $delete_hover_bg; color: $delete_hover_text; }
QFrame#addBar { background: $addbar_bg; border-top: 1px solid $addbar_border; }
QLineEdit#addInput { background: $input_bg; border: 1px solid $input_border; border-radius: 10px; padding: 10px 12px; color: $input_text; }
QLineEdit#addInput:focus { border: 1px solid $accent; }
QPushButton#addButton { background: $accent; color: #ffffff; border: none; border-radius: 10px; padding: 10px 22px; }
QPushButton#addButton:hover   { background: $accent_hover; }
QPushButton#addButton:pressed { background: $accent_press; }

QLabel#headerSubtitle { color: $header_sub; }
QLabel#hijriDate { color: $hijri; }
QFrame#footer { background: $footer_bg; border-top: 1px solid $footer_border; }
QLabel#footerDua { color: $footer_text; }
QPushButton#contactBtn { background: transparent; color: $footer_text; border: none; }
QPushButton#contactBtn:hover { color: $accent; text-decoration: underline; }

QScrollBar:vertical { background: transparent; width: 10px; margin: 4px; }
QScrollBar::handle:vertical { background: $scroll_handle; border-radius: 5px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: $accent; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
""")


_SETTINGS = Template("""
QDialog#settingsDialog { background: $window_bg; }
QLabel { color: $card_text; }
QGroupBox {
    color: $card_text; font-weight: bold;
    border: 1px solid $addbar_border; border-radius: 12px;
    margin-top: 14px; padding: 14px 14px 12px 14px; background: $card_bg;
}
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top right;
    right: 14px; padding: 0 6px; }
QRadioButton, QCheckBox { color: $card_text; spacing: 7px; }
QRadioButton::indicator, QCheckBox::indicator { width: 18px; height: 18px; }
QCheckBox::indicator { border-radius: 5px; border: 2px solid $check_border; background: $check_bg; }
QCheckBox::indicator:checked { background: $check_checked; border-color: $check_checked; }
QRadioButton::indicator { border-radius: 9px; border: 2px solid $check_border; background: $check_bg; }
QRadioButton::indicator:checked { background: $check_checked; border-color: $check_checked; }
QSpinBox, QLineEdit {
    background: $input_bg; border: 1px solid $input_border; border-radius: 8px;
    padding: 6px 8px; color: $input_text;
}
QSpinBox:focus, QLineEdit:focus { border: 1px solid $accent; }
QPushButton#stepBtn {
    background: $tab_bg; color: $card_text; border: none; border-radius: 9px;
    font-weight: bold; min-width: 34px; min-height: 30px;
}
QPushButton#stepBtn:hover { background: $tab_hover; }
QLabel#scaleValue { color: $card_text; font-weight: bold; }
QPushButton#primaryBtn {
    background: $accent; color: #ffffff; border: none; border-radius: 10px;
    padding: 9px 24px; font-weight: bold;
}
QPushButton#primaryBtn:hover { background: $accent_hover; }
QPushButton#ghostBtn {
    background: transparent; color: $card_text; border: 1px solid $input_border;
    border-radius: 10px; padding: 9px 20px;
}
QPushButton#ghostBtn:hover { border-color: $accent; color: $accent; }
""")


def main_window_qss() -> str:
    return _MAIN.substitute(palette())


def settings_qss() -> str:
    return _SETTINGS.substitute(palette())
