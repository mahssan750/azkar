from azkar.content.user_store import UserAzkarStore


def test_seeds_on_first_run(tmp_path):
    store = UserAzkarStore(path=tmp_path / "u.json")
    # seeded from the bundled azkar.json (currently 3 entries)
    assert len(store.all()) >= 1
    assert (tmp_path / "u.json").exists()


def test_add_dedupe_and_persist(tmp_path):
    p = tmp_path / "u.json"
    store = UserAzkarStore(path=p)
    before = len(store.all())

    assert store.add("سبحان الله") is True
    assert store.add("  سبحان الله  ") is False  # trimmed duplicate
    assert store.add("   ") is False  # blank ignored
    assert len(store.all()) == before + 1

    # persisted across instances
    again = UserAzkarStore(path=p)
    assert "سبحان الله" in again.all()


def test_remove(tmp_path):
    p = tmp_path / "u.json"
    store = UserAzkarStore(path=p)
    store.add("الحمد لله")
    assert store.remove("الحمد لله") is True
    assert store.remove("الحمد لله") is False
    assert "الحمد لله" not in store.all()
