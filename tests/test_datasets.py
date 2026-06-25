from azkar.content.dataset import load_dataset


def test_morning_and_evening_have_text_and_counts():
    for filename in ("morning_azkar.json", "evening_azkar.json"):
        items = load_dataset(filename)
        assert len(items) >= 20, filename
        for it in items:
            assert it.get("text", "").strip()
            assert int(it.get("count", 1)) >= 1


def test_hadith_dataset_is_complete_and_numbered():
    items = load_dataset("arbaeen_nawawi.json")
    assert len(items) == 42
    assert [it.get("number") for it in items] == list(range(1, 43))
    for it in items:
        assert it.get("text", "").strip()
