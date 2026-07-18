#!/usr/bin/env python3
"""
Download Hudra prayers from https://hudra.org and save Syriac text as formatted files.

API:
  GET /CRUD/php_mysql/Prayers.php?action=getAllPrayers&page=N&itemsPerPage=50
  GET /CRUD/php_mysql/Prayers.php?action=getAllPrayersByChurch&lang=0&page=N&itemsPerPage=50&isSyriac=1&isChaldean=0
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from quill_to_text import quill_to_text  # noqa: E402

API = "https://hudra.org/CRUD/php_mysql/Prayers.php"
UA = "hudra-org-extractor/1.0 (+local research; curl-compatible)"
PAGE_SIZE = 50
MAX_RETRIES = 5


def api_get(params: dict) -> dict:
    # Empty query values trigger ModSecurity on the host — omit them.
    clean = {k: v for k, v in params.items() if v not in (None, "")}
    qs = urllib.parse.urlencode(clean)
    url = f"{API}?{qs}"
    last_err: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.load(resp)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            last_err = e
            wait = min(2 ** attempt, 30)
            print(f"  retry {attempt}/{MAX_RETRIES} after {e!r}; sleep {wait}s", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"API failed for {params}: {last_err}")


def safe_slug(text: str, fallback: str = "untitled") -> str:
    text = (text or "").strip()
    if not text:
        return fallback
    # Keep Syriac letters, digits, spaces; collapse others.
    text = re.sub(r"[^\w\u0700-\u074F\u0300-\u036F\s.-]+", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip(" .-")
    text = text.replace(" ", "_")
    return (text[:80] or fallback)


def fetch_church_ids(is_syriac: int, is_chaldean: int, out_path: Path, force: bool) -> set[str]:
    label = f"syriac={is_syriac}_chaldean={is_chaldean}"
    if out_path.exists() and not force:
        data = json.loads(out_path.read_text(encoding="utf-8"))
        ids = set(data.get("ids", []))
        print(f"Loaded {len(ids)} IDs for {label} from cache")
        return ids

    page = 1
    ids: list[str] = []
    total = None
    while True:
        data = api_get(
            {
                "action": "getAllPrayersByChurch",
                "lang": 0,
                "page": page,
                "itemsPerPage": PAGE_SIZE,
                "isSyriac": is_syriac,
                "isChaldean": is_chaldean,
            }
        )
        items = data.get("items") or []
        total = data.get("totalItems", total)
        for it in items:
            if it.get("itemId"):
                ids.append(it["itemId"])
        print(f"  church index {label} page {page}: +{len(items)} (have {len(ids)}/{total})")
        if not items or (total is not None and len(ids) >= int(total)):
            break
        page += 1
        time.sleep(0.15)

    out_path.write_text(
        json.dumps({"totalItems": total, "ids": ids}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return set(ids)


def fetch_all_prayer_pages(raw_dir: Path, force: bool) -> list[dict]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    # Probe total
    probe = api_get({"action": "getAllPrayers", "page": 1, "itemsPerPage": 1})
    total = int(probe.get("totalItems") or 0)
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    print(f"Fetching {total} prayers across {pages} pages…")

    all_items: list[dict] = []
    for page in range(1, pages + 1):
        path = raw_dir / f"page_{page:04d}.json"
        if path.exists() and not force:
            data = json.loads(path.read_text(encoding="utf-8"))
        else:
            data = api_get(
                {"action": "getAllPrayers", "page": page, "itemsPerPage": PAGE_SIZE}
            )
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            time.sleep(0.2)
        items = data.get("items") or []
        all_items.extend(items)
        print(f"  page {page}/{pages}: {len(items)} items (running {len(all_items)})")
    return all_items


def write_prayer_files(
    items: list[dict],
    syriac_ids: set[str],
    chaldean_ids: set[str],
    data_prayers: Path,
    text_root: Path,
    force: bool,
) -> dict:
    data_prayers.mkdir(parents=True, exist_ok=True)
    text_root.mkdir(parents=True, exist_ok=True)

    index: list[dict] = []
    by_holiday: dict[str, list[str]] = defaultdict(list)
    seen: set[str] = set()
    written = 0

    for i, item in enumerate(items, 1):
        item_id = item.get("itemId") or f"unknown-{i}"
        if item_id in seen:
            continue
        seen.add(item_id)

        name = item.get("itemName") or ""
        holiday = item.get("itemRelatedHoliday") or "ܠܐ_ܝܕܝܥܐ"
        week = item.get("week") or ""
        day = item.get("day") or ""
        prayer_time = item.get("prayerTime") or ""
        tradition = []
        if item_id in syriac_ids:
            tradition.append("syriac")
        if item_id in chaldean_ids:
            tradition.append("chaldean")
        if not tradition:
            tradition.append("unspecified")

        plain = quill_to_text(item.get("itemDesc"))

        record = {
            "itemId": item_id,
            "itemName": name,
            "itemRelatedHoliday": holiday,
            "week": week,
            "day": day,
            "prayerTime": prayer_time,
            "tradition": tradition,
            "text": plain,
            "source": "https://hudra.org",
        }

        json_path = data_prayers / f"{item_id}.json"
        if force or not json_path.exists():
            json_path.write_text(
                json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
            )

        # Formatted text tree: season / week / day / time
        season_dir = text_root / safe_slug(holiday, "unknown_season")
        week_dir = season_dir / safe_slug(week or "no_week", "no_week")
        day_dir = week_dir / safe_slug(day or "no_day", "no_day")
        day_dir.mkdir(parents=True, exist_ok=True)

        trad_tag = "+".join(tradition)
        fname = f"{safe_slug(prayer_time, 'prayer')}__{safe_slug(name, item_id[:8])}__{item_id[:8]}.txt"
        text_path = day_dir / fname

        header = [
            name,
            "",
            f"ܥܐܕܐ / Season: {holiday}",
            f"ܫܒܬܐ / Week: {week}",
            f"ܝܘܡܐ / Day: {day}",
            f"ܙܒܢܐ / Hour: {prayer_time}",
            f"Tradition: {trad_tag}",
            f"ID: {item_id}",
            f"Source: https://hudra.org",
            "",
            "─" * 40,
            "",
        ]
        body = "\n".join(header) + plain
        if force or not text_path.exists():
            text_path.write_text(body, encoding="utf-8")
            written += 1

        rel = str(text_path.relative_to(text_root))
        index.append(
            {
                "itemId": item_id,
                "itemName": name,
                "holiday": holiday,
                "week": week,
                "day": day,
                "prayerTime": prayer_time,
                "tradition": tradition,
                "path": rel,
                "chars": len(plain),
            }
        )
        by_holiday[holiday].append(rel)

        if i % 100 == 0:
            print(f"  processed {i}/{len(items)}")

    return {"index": index, "by_holiday": dict(by_holiday), "written": written}


def write_combined_corpus(index: list[dict], text_root: Path, out_path: Path) -> None:
    """One big UTF-8 file with all prayers in liturgical order."""
    parts: list[str] = [
        "ܗܘܕܪܐ — Prayers of the Hudra",
        "Source: https://hudra.org",
        f"Prayers: {len(index)}",
        "",
        "=" * 60,
        "",
    ]
    # Sort by holiday, week, day, prayer time, name
    ordered = sorted(
        index,
        key=lambda r: (
            r.get("holiday") or "",
            r.get("week") or "",
            r.get("day") or "",
            r.get("prayerTime") or "",
            r.get("itemName") or "",
        ),
    )
    for r in ordered:
        path = text_root / r["path"]
        if path.exists():
            parts.append(path.read_text(encoding="utf-8").rstrip())
            parts.append("")
            parts.append("=" * 60)
            parts.append("")
    out_path.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Re-download and overwrite")
    parser.add_argument(
        "--syriac-only",
        action="store_true",
        help="Keep only prayers flagged isSyriac=1 (Assyrian/Syriac church edition)",
    )
    args = parser.parse_args()

    raw_dir = ROOT / "data" / "raw"
    data_prayers = ROOT / "data" / "prayers"
    text_root = ROOT / "prayers"
    raw_dir.mkdir(parents=True, exist_ok=True)

    print("Indexing church editions…")
    syriac_ids = fetch_church_ids(1, 0, raw_dir / "ids_syriac.json", args.force)
    chaldean_ids = fetch_church_ids(0, 1, raw_dir / "ids_chaldean.json", args.force)

    items = fetch_all_prayer_pages(raw_dir / "pages", args.force)
    print(f"Downloaded listing: {len(items)} prayer records")

    if args.syriac_only:
        before = len(items)
        items = [it for it in items if it.get("itemId") in syriac_ids]
        print(f"Filtered to Syriac-church edition: {len(items)}/{before}")

    result = write_prayer_files(
        items, syriac_ids, chaldean_ids, data_prayers, text_root, args.force
    )
    index = result["index"]

    index_path = ROOT / "data" / "index.json"
    index_path.write_text(
        json.dumps(
            {
                "source": "https://hudra.org",
                "count": len(index),
                "syriacChurchCount": sum(1 for r in index if "syriac" in r["tradition"]),
                "chaldeanChurchCount": sum(
                    1 for r in index if "chaldean" in r["tradition"]
                ),
                "holidays": sorted(result["by_holiday"].keys()),
                "prayers": index,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    write_combined_corpus(index, text_root, ROOT / "prayers" / "ALL_PRAYERS.txt")

    # Per-season combined files
    by_h: dict[str, list[dict]] = defaultdict(list)
    for r in index:
        by_h[r["holiday"]].append(r)
    seasons_dir = text_root / "_by_season"
    seasons_dir.mkdir(parents=True, exist_ok=True)
    for holiday, rows in sorted(by_h.items()):
        write_combined_corpus(
            rows, text_root, seasons_dir / f"{safe_slug(holiday)}.txt"
        )

    print(
        f"Done. {len(index)} prayers → {text_root}/ "
        f"({result['written']} text files written this run)"
    )
    print(f"Index: {index_path}")
    print(f"Combined: {text_root / 'ALL_PRAYERS.txt'}")


if __name__ == "__main__":
    main()
