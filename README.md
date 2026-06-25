# أذكار — Azkar Reminder

A small Windows 10/11 tray app that helps you remember Allah while using your
computer.

- **At login** it shows a dialog:
  > لا تنسى أن تقول بسم الله ولا تنسى أن تحضر النية لهذا العمل
- **Every 10 minutes** it shows a native Windows toast (with a knock-knock sound):
  > قل سبحان الله والحمد لله
- **A modern tabbed main window** (opens on launch; double-click the tray icon
  to reopen it):
  - **أذكار الصباح** — morning azkar with tap counters and "done" checkboxes.
  - **أذكار المساء** — evening azkar, same.
  - **الأربعون النووية** — the 40 (42) hadith of an-Nawawi, each with an
    expandable explanation.
  - **أذكاري** — add and keep your own azkar.
  - The **Hijri date** is shown in the header (computed offline, fine-tuned
    online about once a month).
- **Daily azkar reminders**: morning azkar at 04:50 and evening azkar at 16:00.
- **Thursday evening** (ليلة الجمعة): a reminder to send salawat upon the Prophet ﷺ.
- A footer on every tab: a du'a (*لا تنسونا من صالح دعائكم*) and a **تواصل معنا**
  link that opens an email to the author.

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

A tray icon shows up and the main window opens. The startup reminder dialog only
appears when the app is launched **at login** (not on a manual open). Right-click
the tray icon for: إظهار النافذة الرئيسية (open window), الإعدادات (settings),
تذكير الآن (remind now), إيقاف/استئناف التذكير (pause/resume), صوت التذكير (sound),
إظهار رسالة البداية, بدء التشغيل مع ويندوز (start with Windows), خروج (quit).

## Settings

Open **الإعدادات** from the tray menu or the ⚙ gear in the window to change:

- **Theme** — light or dark.
- **Font size** — bigger / smaller (A+ / A−).
- **Reminder** — enable/disable, interval in minutes, the reminder text, and sound.

Everything is also stored in `%APPDATA%\Azkar\config.json` (created on first run):

| Key | Default | Meaning |
| --- | --- | --- |
| `reminder_interval_minutes` | `10` | Minutes between toasts |
| `startup_dialog_enabled` | `true` | Show the login dialog (login launches only) |
| `tasbih_reminder_enabled` | `true` | Enable the recurring toast |
| `reminder_sound_enabled` | `true` | Play the knock-knock sound with each reminder |
| `run_at_login` | `true` | Launch automatically at sign-in |
| `theme` | `"light"` | `"light"` or `"dark"` |
| `font_scale` | `1.0` | UI font scale (0.7–1.6) |
| `morning_azkar_reminder_time` | `"04:50"` | Daily morning-azkar reminder (HH:MM) |
| `evening_azkar_reminder_time` | `"16:00"` | Daily evening-azkar reminder (HH:MM) |
| `friday_salawat_time` | `"18:00"` | Thursday-evening salawat reminder (HH:MM) |
| `morning_azkar_reminder_enabled` / `evening_…` / `friday_salawat_enabled` | `true` | Enable each scheduled reminder |
| `hijri_adjustment` | `0` | Day offset for the Hijri date (auto-synced) |
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
