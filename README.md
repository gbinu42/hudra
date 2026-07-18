# hudra.org

Extracted Syriac text of the prayers of the **Hudra** (East Syriac breviary) from [hudra.org](https://hudra.org).

## Contents

| | |
|---|---|
| Prayers | **3,314** (Syriac-script liturgical texts) |
| Assyrian / Syriac-church edition | 1,508 |
| Chaldean-church edition | 1,808 |
| Liturgical seasons / commemorations | 80 |
| Average prayer length | ~20k characters |

## Layout

```
prayers/
  ALL_PRAYERS.txt          # Full corpus in one UTF-8 file
  _by_season/              # One combined file per season/feast
  <season>/<week>/<day>/   # Individual formatted .txt prayers
data/
  index.json               # Flat prayer index
  catalog.json             # Liturgical organization for the web app
  prayers/<uuid>.json      # Per-prayer JSON (metadata + plain text)
  raw/                     # Cached API responses (optional to keep)
web/                       # Next.js reader
scripts/
  extract_prayers.py       # Re-download + convert
  build_catalog.py         # Build liturgical catalog
  quill_to_text.py         # Quill Delta → plain text
```

Each `.txt` file has a short header (name, season, week, day, hour, tradition, source id) followed by the Syriac body. Rubrics that were red in the source are separated with blank lines.

## Web reader

A Next.js app in `web/` browses the corpus by liturgical season:

```bash
cd web
npm install
npm run dev
```

Then open http://localhost:3000.

Organization (see `data/catalog.json`): Annunciation → Nativity → Epiphany → Great Fast → Resurrection → Apostles → Summer → Elijah–Cross → Moses → Dedication, plus commemorations.

## Re-extract

Requires Python 3.10+ (stdlib only):

```bash
python3 scripts/extract_prayers.py
python3 scripts/extract_prayers.py --syriac-only   # Assyrian/Syriac edition only
python3 scripts/extract_prayers.py --force         # ignore caches
# After extract, refresh the web catalog:
python3 scripts/build_catalog.py && cp data/catalog.json web/data/catalog.json
```

Source API: `https://hudra.org/CRUD/php_mysql/Prayers.php`
