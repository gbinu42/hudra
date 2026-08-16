#!/usr/bin/env python3
"""
Download Hudra psalms (mazmora) from the Bible API.

API:
  GET /CRUD/php_mysql/Bible.php?action=getAllBibles&page=N&itemsPerPage=50&lang=0
  GET /CRUD/php_mysql/Bible.php?action=getBibleById&itemId=<uuid>&lang=0
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from quill_to_text import quill_to_html, quill_to_text  # noqa: E402

API = "https://hudra.org/CRUD/php_mysql/Bible.php"
UA = "hudra-extractor/1.0 (+local research; curl-compatible)"
PAGE_SIZE = 50
MAX_RETRIES = 5


def api_get(params: dict) -> dict:
    clean = {k: v for k, v in params.items() if v not in (None, "")}
    qs = urllib.parse.urlencode(clean)
    url = f"{API}?{qs}"
    last_err: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.load(resp)
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            json.JSONDecodeError,
        ) as e:
            last_err = e
            wait = min(2**attempt, 30)
            print(f"  retry {attempt}/{MAX_RETRIES} after {e!r}; sleep {wait}s", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"API failed for {params}: {last_err}")


def fetch_listing(raw_dir: Path, force: bool) -> list[dict]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    probe = api_get(
        {"action": "getAllBibles", "page": 1, "itemsPerPage": 1, "lang": 0}
    )
    total = int(probe.get("totalItems") or 0)
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    print(f"Fetching {total} psalm listings across {pages} pages…")

    all_items: list[dict] = []
    for page in range(1, pages + 1):
        path = raw_dir / f"page_{page:04d}.json"
        if path.exists() and not force:
            data = json.loads(path.read_text(encoding="utf-8"))
        else:
            data = api_get(
                {
                    "action": "getAllBibles",
                    "page": page,
                    "itemsPerPage": PAGE_SIZE,
                    "lang": 0,
                }
            )
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            time.sleep(0.2)
        items = data.get("items") or []
        all_items.extend(items)
        print(f"  page {page}/{pages}: {len(items)} items (running {len(all_items)})")
    return all_items


def parse_number(raw: object) -> int:
    """Parse API number field (\"1\", \"000\", …) to int for sorting."""
    s = str(raw or "").strip()
    if not s:
        return 0
    try:
        return int(s)
    except ValueError:
        digits = "".join(ch for ch in s if ch.isdigit())
        return int(digits) if digits else 0


def fetch_and_write(
    listings: list[dict],
    detail_dir: Path,
    data_psalms: Path,
    text_root: Path,
    force: bool,
) -> list[dict]:
    detail_dir.mkdir(parents=True, exist_ok=True)
    data_psalms.mkdir(parents=True, exist_ok=True)
    text_root.mkdir(parents=True, exist_ok=True)

    index: list[dict] = []
    written = 0
    seen: set[str] = set()

    for i, listing in enumerate(listings, 1):
        item_id = listing.get("itemId")
        if not item_id or item_id in seen:
            continue
        seen.add(item_id)

        detail_path = detail_dir / f"{item_id}.json"
        if detail_path.exists() and not force:
            detail = json.loads(detail_path.read_text(encoding="utf-8"))
        else:
            detail = api_get(
                {"action": "getBibleById", "itemId": item_id, "lang": 0}
            )
            detail_path.write_text(
                json.dumps(detail, ensure_ascii=False), encoding="utf-8"
            )
            time.sleep(0.15)

        name = detail.get("itemName") or listing.get("itemName") or ""
        number_raw = detail.get("number")
        if number_raw is None:
            number_raw = listing.get("number")
        order = listing.get("order")
        if order is None:
            order = parse_number(number_raw)
        number = parse_number(number_raw)
        raw_desc = detail.get("itemDesc")
        plain = quill_to_text(raw_desc)
        html_body = quill_to_html(raw_desc)

        record = {
            "itemId": item_id,
            "itemName": name,
            "number": number,
            "numberRaw": str(number_raw) if number_raw is not None else "",
            "order": int(order) if order is not None else number,
            "text": plain,
            "html": html_body,
        }

        json_path = data_psalms / f"{item_id}.json"
        if force or not json_path.exists():
            json_path.write_text(
                json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            written += 1

        num_label = f"{number:03d}" if number else "000"
        text_path = text_root / f"{num_label}__{item_id[:8]}.txt"
        header = [
            name,
            "",
            f"Psalm number: {number}",
            f"ID: {item_id}",
            "",
            "─" * 40,
            "",
        ]
        if force or not text_path.exists():
            text_path.write_text("\n".join(header) + plain, encoding="utf-8")

        index.append(
            {
                "itemId": item_id,
                "itemName": name,
                "number": number,
                "numberRaw": record["numberRaw"],
                "order": record["order"],
                "chars": len(plain),
                "path": str(text_path.relative_to(text_root)),
            }
        )

        if i % 25 == 0 or i == len(listings):
            print(f"  processed {i}/{len(listings)}")

    def sort_key(r: dict) -> tuple:
        n = int(r.get("number") or 0)
        if 11801 <= n <= 11822:
            return (118, n - 11800, r.get("itemName") or "")
        return (n, 0, r.get("itemName") or "")

    index.sort(key=sort_key)
    print(f"  wrote/updated {written} psalm JSON files")
    return index


def write_combined(index: list[dict], text_root: Path, out_path: Path) -> None:
    parts = [
        "ܡܙܡܘܪ̈ܐ — Psalms of the Hudra",
        f"Psalms: {len(index)}",
        "",
        "=" * 60,
        "",
    ]
    for r in index:
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
    args = parser.parse_args()

    raw_dir = ROOT / "data" / "raw" / "bible"
    data_psalms = ROOT / "data" / "psalms"
    text_root = ROOT / "psalms"
    raw_dir.mkdir(parents=True, exist_ok=True)

    listings = fetch_listing(raw_dir / "pages", args.force)
    print(f"Downloaded listing: {len(listings)} psalm records")

    index = fetch_and_write(
        listings,
        raw_dir / "details",
        data_psalms,
        text_root,
        args.force,
    )

    index_path = ROOT / "data" / "psalms_index.json"
    index_path.write_text(
        json.dumps(
            {
                "count": len(index),
                "psalms": index,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    write_combined(index, text_root, text_root / "ALL_PSALMS.txt")

    print(f"Done. {len(index)} psalms → {data_psalms}/ and {text_root}/")
    print(f"Index: {index_path}")


if __name__ == "__main__":
    main()
