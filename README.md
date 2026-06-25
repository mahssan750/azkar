# أذكار — Azkar Reminder

A small Windows 10/11 tray app that helps you remember Allah while using your
computer.

- **At login** it shows a dialog:
  > لا تنسى أن تقول بسم الله ولا تنسى أن تحضر النية لهذا العمل
- **Every 10 minutes** it shows a native Windows toast:
  > قل سبحان الله والحمد لله
- **A modern tabbed main window** (opens on launch; double-click the tray icon
  to reopen it):
  - **أذكار الصباح** — morning azkar with tap counters and "done" checkboxes.
  - **أذكار المساء** — evening azkar, same.
  - **الأربعون النووية** — the 40 (42) hadith of an-Nawawi, each with an
    expandable explanation.
  - **أذكاري** — add and keep your own azkar.
- A du'a footer on every tab: *لا تنسونا من صالح دعائكم*.

It runs quietly in the system tray and is built to grow — content lives in
JSON files under `content/data/`, so adding more is data, not code.

## Download (Windows) — easiest

1. Go to the [**Releases**](https://github.com/mahssan750/azkar/releases/latest) page.
2. Download **`Azkar.exe`** and save it somewhere permanent (e.g.
   `Documents\Azkar\` — not your Downloads folder, since it registers itself to
   start at login from wherever it lives).
3. Double-click it. Windows SmartScreen may warn because the app isn't
   code-signed — click **More info → Run anyway**.

That's it: the startup reminder appears, an icon shows in the system tray, and a
reminder pops up every 10 minutes.

## Requirements (for building from source)

- Windows 10 or 11
- Python 3.10+ (developed on 3.12)

## Setup (development)

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip install -e .
```

## Run

```powershell
# windowed (normal use)
.\.venv\Scripts\azkar.exe
# or, to see logs/tracebacks in the console:
.\.venv\Scripts\python.exe -m azkar
```

The startup dialog appears, a tray icon shows up, and a toast fires on the
configured interval. Right-click the tray icon for: تذكير الآن (remind now),
إيقاف/استئناف التذكير (pause/resume), إظهار رسالة البداية (show startup dialog),
بدء التشغيل مع ويندوز (start with Windows), خروج (quit).

## Settings

Edit `%APPDATA%\Azkar\config.json` (created on first run):

| Key | Default | Meaning |
| --- | --- | --- |
| `reminder_interval_minutes` | `10` | Minutes between toasts |
| `startup_dialog_enabled` | `true` | Show the login dialog |
| `tasbih_reminder_enabled` | `true` | Enable the recurring toast |
| `run_at_login` | `true` | Launch automatically at sign-in |
| `tasbih_text` | `"قل سبحان الله والحمد لله"` | The toast text |
| `tasbih_shuffle` | `false` | Rotate phrases from `tasbih.json` instead |
| `debug_interval_seconds` | `0` | If > 0, overrides the interval (for testing) |

## Run at login

Enabled by default. The app registers itself under
`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`; toggle it from the tray
menu or with `run_at_login` in the config. In development this points at the
venv launcher, so for a permanent install build the executable (below) and let
it register itself on first run.

## Build a standalone .exe

```powershell
.\scripts\build_exe.ps1   # output: dist\Azkar.exe (single file)
```

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Project layout

```
src/azkar/
  app.py            tray + scheduler wiring, entry point
  config.py         settings (JSON in %APPDATA%\Azkar)
  autostart.py      run-at-login (HKCU Run key)
  scheduler.py      QTimer-based, holds many reminders
  notifier.py       native toasts (windows-toasts) + tray fallback
  reminders/        startup_dialog.py, tasbih_toast.py  (+ base.py)
  content/          JSON provider, dataset loader, user store + data/
  ui/               main_window.py, pages.py, cards.py, rtl.py, widgets.py, icon.py
```

### Adding a feature later

- **A new tab:** build a page in `ui/pages.py` (reuse the card widgets in
  `ui/cards.py`) and `addTab(...)` it in `ui/main_window.py`.
- **A new recurring reminder:** subclass `reminders/base.Reminder`, then
  `scheduler.add_interval_reminder(name, interval_ms, reminder.run)` in `app.py`.
- **New content:** drop a JSON file in `content/data/` and load it with
  `content.dataset.load_dataset("yourfile.json")`.

## Content credits

Islamic texts are public domain; the JSON was normalised from open datasets —
see [src/azkar/content/data/SOURCES.md](src/azkar/content/data/SOURCES.md).

## License

[MIT](LICENSE) © 2026 mahssan750
