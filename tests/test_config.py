import json

from azkar.config import DEFAULT_TASBIH_TEXT, Settings, config_path, load_settings, save_settings


def test_first_run_creates_defaults(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    s = load_settings()
    assert s.reminder_interval_minutes == 10
    assert s.tasbih_text == DEFAULT_TASBIH_TEXT
    assert config_path().exists()


def test_roundtrip_preserves_arabic(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    s = load_settings()
    s.reminder_interval_minutes = 5
    s.tasbih_text = "اختبار النص العربي"
    save_settings(s)

    again = load_settings()
    assert again.reminder_interval_minutes == 5
    assert again.tasbih_text == "اختبار النص العربي"
    assert again.interval_ms == 5 * 60 * 1000

    # file is human-readable UTF-8 (not \u escapes)
    assert "اختبار" in config_path().read_text(encoding="utf-8")


def test_unknown_keys_ignored(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    config_path().write_text(
        json.dumps({"reminder_interval_minutes": 7, "obsolete": True}),
        encoding="utf-8",
    )
    s = load_settings()
    assert s.reminder_interval_minutes == 7


def test_debug_interval_overrides():
    assert Settings(debug_interval_seconds=3).interval_ms == 3000
