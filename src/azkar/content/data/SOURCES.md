# Content sources

The Islamic text bundled with this app is in the public domain (Qur'an and
hadith). The structured JSON was normalised from these open datasets:

- **Morning & evening azkar** (`morning_azkar.json`, `evening_azkar.json`) —
  from [ahegazy/muslimKit](https://github.com/ahegazy/muslimKit)
  (`docs/json/azkar_sabah.json`, `azkar_massa.json`), based on *Hisn al-Muslim*.
- **The 40 Hadith of an-Nawawi** (`arbaeen_nawawi.json`, 42 hadith) — from
  [osamayy/40-hadith-nawawi-db](https://github.com/osamayy/40-hadith-nawawi-db).

Each azkar record has `text`, a `count` (recommended repetitions) and an
optional `virtue`. Each hadith record has a `number`, the `text` (matn) and an
optional `explanation` (شرح).
