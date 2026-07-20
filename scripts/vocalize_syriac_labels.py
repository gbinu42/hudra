#!/usr/bin/env python3
"""
Persist East Syriac vocalization into catalog + prayer JSON labels.

Builds a bare→pointed lexicon from catalog days/hours/seasons and already
pointed titles, then rewrites unpointed Syriac fields in place so they can
be edited by hand afterward.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "catalog.json"
PRAYERS_DIR = ROOT / "data" / "prayers"
WEB_CATALOG = ROOT / "web" / "data" / "catalog.json"

MARK_RE = re.compile(r"[\u0730-\u074A\u0308\u0323\u032E\u0307]")
WORD_RE = re.compile(r"[\u0710-\u074F]+")
PROCLITICS = set("ܕܘܒܠ")

SEED = [
    "ܨܵܘܡܵܐ",
    "ܕܸܢܚܵܐ",
    "ܩܲܝܛܵܐ",
    "ܩܝܵܡܬ݂ܵܐ",
    "ܫܠܝܼܚܹ̈ܐ",
    "ܕܘܼܟܪܵܢܵܐ",
    "ܐܲܠܝܼܵܐ",
    "ܡܘܼܫܹܐ",
    "ܝܲܠܕܵܐ",
    "ܥܹܕ݂ܬ݂ܵܐ",
    "ܡܫܝܼܚܵܐ",
    "ܝܫܘܿܥ",
    "ܩܲܕܝܼܫܬ݂ܵܐ",
    "ܚܘܼܕܬ݂ܵܐ",
    "ܒܹܝܬ݂",
    "ܫܟܲܚܬ݂ܵܐ",
    "ܡܲܥܲܠܝܵܐ",
    "ܬܸܫܒܘܿܚܬ݂ܵܐ",
]


def strip_marks(s: str) -> str:
    return MARK_RE.sub("", s)


def has_pointing(s: str) -> bool:
    return bool(MARK_RE.search(s))


def remember(
    lex: dict[str, str],
    pointed: str,
    *,
    overwrite: bool = True,
    force: bool = False,
) -> None:
    bare = strip_marks(pointed)
    if not bare or bare == pointed:
        return
    prev = lex.get(bare)
    if prev is None:
        lex[bare] = pointed
        return
    if not overwrite:
        return
    if force or len(pointed) >= len(prev):
        lex[bare] = pointed


def build_lexicon(catalog: dict) -> dict[str, str]:
    lex: dict[str, str] = {}
    for w in SEED:
        remember(lex, w)

    for s in catalog.get("seasons", []):
        syr = s.get("syriac") or ""
        remember(lex, syr)
        for part in syr.split():
            remember(lex, part, overwrite=False)

    for h in catalog.get("hours", []):
        syr = h.get("syriac") or ""
        remember(lex, syr)
        for part in syr.split():
            remember(lex, part)

    for d in catalog.get("days", []):
        remember(lex, d.get("syriac") or "", force=True)

    for p in catalog.get("prayers", []):
        for key in ("week", "day", "hour"):
            val = p.get(key) or ""
            if val:
                remember(lex, val, overwrite=False)
        name = p.get("name") or ""
        if has_pointing(name):
            for w in WORD_RE.findall(name):
                if has_pointing(w):
                    remember(lex, w, overwrite=False)

    return lex


def lookup_word(lex: dict[str, str], word: str) -> str:
    if has_pointing(word):
        return word
    bare = strip_marks(word)
    hit = lex.get(bare)
    if hit:
        return hit
    if len(bare) > 1 and bare[0] in PROCLITICS:
        rest = lex.get(bare[1:])
        if rest:
            return bare[0] + rest
    return word


def vocalize(text: str, lex: dict[str, str]) -> str:
    if not text or text == "—":
        return text
    return WORD_RE.sub(lambda m: lookup_word(lex, m.group(0)), text)


def vocalize_field(obj: dict, key: str, lex: dict[str, str]) -> bool:
    val = obj.get(key)
    if not isinstance(val, str) or not val:
        return False
    new = vocalize(val, lex)
    if new != val:
        obj[key] = new
        return True
    return False


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    lex = build_lexicon(catalog)

    cat_changed = 0
    for s in catalog.get("seasons", []):
        if vocalize_field(s, "syriac", lex):
            cat_changed += 1
    for p in catalog.get("prayers", []):
        for key in ("name", "week", "day", "hour", "holiday"):
            if vocalize_field(p, key, lex):
                cat_changed += 1

    CATALOG.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if WEB_CATALOG.parent.exists():
        WEB_CATALOG.write_text(
            json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    prayer_files = 0
    if PRAYERS_DIR.exists():
        for path in sorted(PRAYERS_DIR.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            changed = False
            for key in (
                "itemName",
                "week",
                "day",
                "prayerTime",
                "itemRelatedHoliday",
            ):
                if vocalize_field(data, key, lex):
                    changed = True
            if changed:
                path.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                prayer_files += 1

    # Rebuild lexicon after first pass? One pass is enough for labels.
    print(
        f"Vocalized catalog fields touched: {cat_changed}; "
        f"prayer JSON files updated: {prayer_files}; "
        f"lexicon size: {len(lex)}"
    )


if __name__ == "__main__":
    main()
