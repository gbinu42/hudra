#!/usr/bin/env python3
"""Add colored HTML bodies to prayer JSON files from cached Quill deltas."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from quill_to_text import quill_to_html, quill_to_text  # noqa: E402

PAGES = ROOT / "data" / "raw" / "pages"
PRAYERS = ROOT / "data" / "prayers"


def main() -> None:
    pages = sorted(PAGES.glob("page_*.json"))
    if not pages:
        raise SystemExit(f"No pages in {PAGES}")

    updated = 0
    missing_files = 0
    for page_path in pages:
        data = json.loads(page_path.read_text(encoding="utf-8"))
        for item in data.get("items") or []:
            item_id = item.get("itemId")
            if not item_id:
                continue
            path = PRAYERS / f"{item_id}.json"
            if not path.exists():
                missing_files += 1
                continue
            record = json.loads(path.read_text(encoding="utf-8"))
            raw = item.get("itemDesc")
            html_body = quill_to_html(raw)
            plain = quill_to_text(raw)
            record["html"] = html_body
            # Refresh plain text too so it stays in sync
            if plain.strip():
                record["text"] = plain
            path.write_text(
                json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            updated += 1
            if updated % 200 == 0:
                print(f"  {updated} prayers…")

    print(f"Updated {updated} prayers with HTML ({missing_files} missing files)")


if __name__ == "__main__":
    main()
