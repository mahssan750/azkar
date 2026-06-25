import json
import random

from azkar.content.json_provider import JsonContentProvider


def _write(tmp_path, name, data):
    p = tmp_path / name
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return p


def test_shuffle_covers_all_without_immediate_repeats(tmp_path):
    items = ["a", "b", "c", "d"]
    prov = JsonContentProvider(path=_write(tmp_path, "x.json", items), rng=random.Random(0))

    seen, last = [], None
    for _ in range(40):
        choice = prov.next()
        assert choice != last  # never the same item twice in a row
        last = choice
        seen.append(choice)
    assert set(seen) == set(items)  # every item appears


def test_object_entries_use_text_key(tmp_path):
    data = [{"text": "x", "book": "B"}, {"text": "y"}]
    prov = JsonContentProvider(path=_write(tmp_path, "h.json", data))
    assert set(prov.all()) == {"x", "y"}


def test_single_item_repeats(tmp_path):
    prov = JsonContentProvider(path=_write(tmp_path, "one.json", ["only"]))
    assert prov.next() == "only"
    assert prov.next() == "only"


def test_empty_file_returns_blank(tmp_path):
    prov = JsonContentProvider(path=_write(tmp_path, "e.json", []))
    assert prov.next() == ""
    assert prov.all() == []
