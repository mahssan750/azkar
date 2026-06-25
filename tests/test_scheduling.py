import datetime

from azkar.clock_scheduler import parse_hhmm
from azkar.hijri import format_hijri, needs_sync


def test_parse_hhmm_valid_and_invalid():
    assert parse_hhmm("04:50") == (4, 50)
    assert parse_hhmm("16:00") == (16, 0)
    assert parse_hhmm("bad", (9, 9)) == (9, 9)
    assert parse_hhmm("25:99", (0, 0)) == (0, 0)


def test_needs_sync():
    assert needs_sync("") is True
    today = datetime.date.today().isoformat()
    assert needs_sync(today) is False
    old = (datetime.date.today() - datetime.timedelta(days=40)).isoformat()
    assert needs_sync(old) is True


def test_format_hijri_known_date():
    # 2026-06-26 is 11 Muharram 1448 (Umm al-Qura)
    text = format_hijri(adjustment=0, date=datetime.date(2026, 6, 26))
    assert "محرم" in text
    assert "١١" in text and "١٤٤٨" in text
    assert text.endswith("هـ")
