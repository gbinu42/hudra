#!/usr/bin/env python3
"""Build data/catalog.json — liturgical organization for the web reader."""

from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "index.json"
OUT = ROOT / "data" / "catalog.json"
WEB_COPY = ROOT / "web" / "data" / "catalog.json"

SEASON_META = [
    ("ܣܘܒܪܐ", "subara", "Annunciation", "Season of the Annunciation", 1),
    ("ܥܐܕܐ ܩܕܝܫܐ ܕܝܠܕܗ ܕܡܪܢ", "yalda", "Nativity", "Feast of the Nativity of our Lord", 2),
    ("ܚܕܒܫܒ̈ܐ ܕܒܬܪ ܝܠܕܐ", "after-nativity", "Sundays after Nativity", "Sundays following the Nativity", 3),
    ("ܥܐܕܐ ܕܓܙܘܪܬܗ ܕܡܪܢ", "circumcision", "Circumcision", "Feast of the Circumcision of our Lord", 4),
    ("ܕܢܚܐ0", "denha", "Epiphany", "Season of the Epiphany (Denha)", 5),
    ("ܥܐܕܐ ܕܕܢܚܐ", "denha-feast", "Feast of Epiphany", "Feast of the Epiphany", 6),
    ("ܨܘܡܐ ܪܒܐ", "great-fast", "Great Fast", "Season of the Great Fast (Lent)", 7),
    ("ܥܪܘܒܬܐ ܕܠܥܙܪ", "lazarus", "Friday of Lazarus", "Friday of Lazarus", 8),
    ("ܥܐܕܐ ܫܒܝܚܐ ܕܐܘܫܥܢ̈ܐ", "hosannas", "Hosannas", "Feast of Hosannas (Palm Sunday)", 9),
    ("ܚܡܫܒܫܒܐ ܕܦܨܚܐ", "passover", "Passover Thursday", "Thursday of the Passover", 10),
    ("ܥܪܘܒܬܐ ܕܚܫܐ", "passion", "Friday of the Passion", "Friday of the Passion", 11),
    ("ܫܒܬܐ ܪܒܬܐ", "great-saturday", "Great Saturday", "Great Saturday", 12),
    ("ܚܕܒܫܒܐ ܪܒܐ ܕܩܝܡܬܗ ܕܡܪܢ", "easter", "Great Sunday of Resurrection", "Great Sunday of the Resurrection", 13),
    ("ܩܝܡܬܐ", "resurrection", "Resurrection", "Season of the Resurrection", 14),
    ("ܥܐܕܐ ܩܕܝܫܐ ܕܣܘܠܩܗ ܕܡܪܢ", "ascension", "Ascension", "Feast of the Ascension of our Lord", 15),
    ("ܥܐܕܐ ܕܦܢܛܝܩܘܣܛܐ", "pentecost", "Pentecost", "Feast of Pentecost", 16),
    ("ܫܠܝ̈ܚܐ", "apostles", "Apostles", "Season of the Apostles", 17),
    ("ܩܝܛܐ", "summer", "Summer", "Season of the Summer (Qayta)", 18),
    ("ܐܠܝܐ - ܨܠܝܒܐ", "elijah-cross", "Elijah — Cross", "Season of Elijah and the Cross", 19),
    ("ܡܘܫܐ", "moses", "Moses", "Season of Moses", 20),
    ("ܩܘܕܫ ܥܕܬܐ - ܡܥܠܬܐ", "dedication", "Dedication of the Church", "Season of the Dedication of the Church", 21),
]

HOUR_ORDER = {
    "ܪܡܫܐ": 1,
    "ܣܘܒܥܐ": 2,
    "ܠܠܝܐ ܘܡܘܬܒܐ": 3,
    "ܩܠ̈ܐ ܕܫܗܪܐ": 4,
    "ܨܦܪܐ": 5,
    "ܥܕܢܐ": 7,
    "ܩܘܛܥܐ": 8,
    "ܐ̄ܪ̈ܙܐ ܐܠܗܝ̈ܐ": 9,
}

HOUR_EN = {
    "ܪܡܫܐ": "Evening (Ramsha)",
    "ܣܘܒܥܐ": "Compline (Sutoraya)",
    "ܠܠܝܐ ܘܡܘܬܒܐ": "Night & Mottava",
    "ܩܠ̈ܐ ܕܫܗܪܐ": "Qale d-Shahra",
    "ܨܦܪܐ": "Morning (Sapra)",
    "ܥܕܢܐ": "Third Hour",
    "ܩܘܛܥܐ": "Quta'a",
    "ܐ̄ܪ̈ܙܐ ܐܠܗܝ̈ܐ": "Divine Mysteries",
}

DAY_ORDER = {
    "ܚܕܒܫܒܐ": 1,
    "ܬܪܝܢܒܫܒܐ": 2,
    "ܬܠܬܒܫܒܐ": 3,
    "ܐܪܒܥܒܫܒܐ": 4,
    "ܚܡܫܒܫܒܐ": 5,
    "ܥܪܘܒܬܐ": 6,
    "ܫܒܬܐ": 7,
}

DAY_EN = {
    "ܚܕܒܫܒܐ": "Sunday",
    "ܬܪܝܢܒܫܒܐ": "Monday",
    "ܬܠܬܒܫܒܐ": "Tuesday",
    "ܐܪܒܥܒܫܒܐ": "Wednesday",
    "ܚܡܫܒܫܒܐ": "Thursday",
    "ܥܪܘܒܬܐ": "Friday",
    "ܫܒܬܐ": "Saturday",
}


def main() -> None:
    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    known = {s[0] for s in SEASON_META}
    holidays = sorted({p["holiday"] for p in idx["prayers"]})

    seasons: list[dict] = []
    for syr, slug, en, desc, order in SEASON_META:
        seasons.append(
            {
                "id": slug,
                "syriac": "ܕܢܚܐ" if syr == "ܕܢܚܐ0" else syr,
                "english": en,
                "description": desc,
                "order": order,
                "group": "cycle",
                "sourceHoliday": syr,
            }
        )

    order = 100
    for h in holidays:
        if h in known or h in ("ܠܐ_ܝܕܝܥܐ", ""):
            continue
        ascii_slug = (
            re.sub(
                r"[^a-z0-9]+",
                "-",
                unicodedata.normalize("NFKD", h).encode("ascii", "ignore").decode().lower(),
            ).strip("-")
        )
        slug = ascii_slug or f"feast-{abs(hash(h)) % 10**8:x}"
        if h.startswith("ܕܘܟܪܢܐ"):
            group = "commemoration"
            en = f'Commemoration — {h.replace("ܕܘܟܪܢܐ ܕ", "").strip()}'
        elif h.startswith("ܥܐܕܐ") or h.startswith("ܥܪܘܒܬܐ"):
            group = "feast"
            en = "Feast"
        elif "ܒܥܘܬܐ" in h:
            group = "baotha"
            en = "Rogation"
        else:
            group = "other"
            en = "Other"
        seasons.append(
            {
                "id": slug,
                "syriac": h,
                "english": en,
                "description": h,
                "order": order,
                "group": group,
                "sourceHoliday": h,
            }
        )
        order += 1

    seasons.append(
        {
            "id": "unassigned",
            "syriac": "ܠܐ ܝܕܝܥܐ",
            "english": "Unassigned",
            "description": "Prayers without a season tag",
            "order": 999,
            "group": "other",
            "sourceHoliday": "ܠܐ_ܝܕܝܥܐ",
        }
    )

    holiday_to_season = {s["sourceHoliday"]: s["id"] for s in seasons}
    prayers_out = []
    for p in idx["prayers"]:
        holiday = p["holiday"] or "ܠܐ_ܝܕܝܥܐ"
        prayers_out.append(
            {
                "id": p["itemId"],
                "name": p["itemName"],
                "holiday": holiday,
                "seasonId": holiday_to_season.get(holiday, "unassigned"),
                "week": p["week"] or "",
                "day": p["day"] or "",
                "dayEn": DAY_EN.get(p["day"] or "", ""),
                "hour": p["prayerTime"] or "",
                "hourEn": HOUR_EN.get(p["prayerTime"] or "", p["prayerTime"] or "Hour"),
                "hourOrder": HOUR_ORDER.get(p["prayerTime"] or "", 99),
                "dayOrder": DAY_ORDER.get(p["day"] or "", 99),
                "tradition": p["tradition"],
                "chars": p["chars"],
            }
        )

    counts: dict[str, int] = defaultdict(int)
    for p in prayers_out:
        counts[p["seasonId"]] += 1
    for s in seasons:
        s["count"] = counts.get(s["id"], 0)
    seasons = [s for s in seasons if s["count"] > 0 or s["group"] == "cycle"]
    seasons.sort(key=lambda s: s["order"])

    catalog = {
        "source": "https://hudra.org",
        "generatedFor": "Hudra liturgical browser",
        "counts": {
            "prayers": len(prayers_out),
            "seasons": len(seasons),
            "syriac": sum(1 for p in prayers_out if "syriac" in p["tradition"]),
            "chaldean": sum(1 for p in prayers_out if "chaldean" in p["tradition"]),
        },
        "hours": [
            {"syriac": k, "english": HOUR_EN[k], "order": v}
            for k, v in sorted(HOUR_ORDER.items(), key=lambda x: x[1])
            if k in HOUR_EN
        ],
        "days": [
            {"syriac": k, "english": DAY_EN[k], "order": v}
            for k, v in sorted(DAY_ORDER.items(), key=lambda x: x[1])
        ],
        "seasons": seasons,
        "prayers": prayers_out,
    }

    text = json.dumps(catalog, ensure_ascii=False)
    OUT.write_text(text, encoding="utf-8")
    if WEB_COPY.parent.exists():
        WEB_COPY.parent.mkdir(parents=True, exist_ok=True)
        WEB_COPY.write_text(text, encoding="utf-8")
        print(f"Wrote {OUT} and {WEB_COPY}")
    else:
        print(f"Wrote {OUT}")
    print(f"{catalog['counts']['prayers']} prayers · {catalog['counts']['seasons']} seasons")


if __name__ == "__main__":
    main()
