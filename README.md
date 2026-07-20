# hudra.org

Extracted Syriac text of the prayers and psalms of the **Hudra** (East Syriac breviary) from [hudra.org](https://hudra.org).

## Contents

| | |
|---|---|
| Prayers | **3,314** (Syriac-script liturgical texts) |
| Psalms (mazmora) | **188** |
| Assyrian / Syriac-church edition | 1,508 |
| Chaldean-church edition | 1,808 |
| Liturgical seasons / commemorations | 80 |
| Average prayer length | ~20k characters |

## Layout

```
prayers/
  ALL_PRAYERS.txt          # Full prayer corpus in one UTF-8 file
  _by_season/              # One combined file per season/feast
  <season>/<week>/<day>/   # Individual formatted .txt prayers
psalms/
  ALL_PSALMS.txt           # Full psalter in one UTF-8 file
  <nnn>__<id>.txt          # Individual numbered psalms
data/
  index.json               # Flat prayer index
  psalms_index.json        # Flat psalm index
  catalog.json             # Liturgical organization for the web app
  prayers/<uuid>.json      # Per-prayer JSON (metadata + plain text / HTML)
  psalms/<uuid>.json       # Per-psalm JSON (metadata + plain text / HTML)
  raw/                     # Cached API responses (optional to keep)
web/                       # Next.js reader
scripts/
  extract_prayers.py       # Re-download + convert prayers
  extract_psalms.py        # Re-download + convert psalms (Bible.php)
  build_catalog.py         # Build liturgical catalog
  quill_to_text.py         # Quill Delta → plain text / HTML
```

Each `.txt` file has a short header followed by the Syriac body. Rubrics that were red in the source are separated with blank lines.

## Web reader

A Next.js app in `web/` browses the corpus by liturgical season and psalm number:

```bash
cd web
npm install
npm run dev
```

Then open http://localhost:3000.

Routes include `/browse` (seasons), `/psalms` (psalter), `/calendar`, `/search`, and readers at `/prayer/[id]` and `/psalm/[id]`.

## Re-extract

Requires Python 3.10+ (stdlib only):

```bash
python3 scripts/extract_prayers.py
python3 scripts/extract_prayers.py --syriac-only   # Assyrian/Syriac edition only
python3 scripts/extract_prayers.py --force         # ignore caches
python3 scripts/extract_psalms.py
python3 scripts/extract_psalms.py --force
# After extract, refresh the web catalog:
python3 scripts/build_catalog.py
```

Source APIs:

- Prayers: `https://hudra.org/CRUD/php_mysql/Prayers.php`
- Psalms: `https://hudra.org/CRUD/php_mysql/Bible.php`
