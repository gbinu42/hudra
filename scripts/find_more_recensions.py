#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deeper recension miner: lower ratio, internal n-grams, expanded christology."""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict, Counter
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from find_hymn_near_dupes import (  # noqa: E402
    ROOT,
    extract_hymn_blocks,
    strip_norm,
    word_diff,
    is_ortho_only,
)

CACHE = ROOT / "scripts/_hymn_units_cache.json"
OUT = ROOT / "scripts/_more_recensions.json"

KNOWN_OPENS = {
    "ܒܪܝܟ ܚܢܢܐ",
    "ܠܝܡܐ ܕܡܪܚܡܢܘܬܟ",
    "ܐܬܢܐ ܥܠ ܪܒܘܬܗ",
    "ܥܕܬܐ ܡܟܝܪܬܗ",
    "ܡܢ ܫܡܝܐ ܢܚܬ",
    "ܒܪܝܟ ܛܒܐ",
    "ܛܘܒܝܟܝ ܡܪܝܡ",
    "ܐܝܢܘ ܗܘܢܐ",
    "ܗܘ ܕܡܢ ܓܘܚܐ",
    "ܩܢܘܡܐ ܬܠܬܐ",
    "ܐܝܟܢܐ ܐܘܕܐ",
    "ܨܠܝܒܟ ܡܚܣܐ",
    "ܒܪܫܝܬ ܐܝܬܘܗܝ",
    "ܒܐܢܐ ܐܢܐ ܠܚܡܐ",
    "ܪܫ ܩܠܐ ܡܢ",
    "ܕܢܚ ܠܗ ܟܘܟܒܐ",
}

# Substitution / presence patterns with theological force.
SUB_PATTERNS = [
    ("parsopa/qnoma", re.compile(r"ܦܪܨܘܦ"), re.compile(r"ܩܢܘܡ")),
    ("temple/body", re.compile(r"ܗܝܟܠ|ܢܘܣܐ|ܥܘܡܪܐ"), re.compile(r"ܦܓܪ")),
    ("dwell/take", re.compile(r"ܫܪܐ|ܫ̣ܪܐ"), re.compile(r"ܢܣܒ")),
    ("wrap/become", re.compile(r"ܐܬܥܛܦ|ܐܣܛܠ"), re.compile(r"ܐܬܒܪܢܫ|ܐܬܓܫܡ|ܗܘܐ ܒܣܪ|ܐܓܢ")),
    ("weave/take", re.compile(r"ܙܩܪ"), re.compile(r"ܢܣܒ")),
    ("clothe/become-man", re.compile(r"ܠܒܫ"), re.compile(r"ܗܘܐ ܒܪܢܫ|ܐܬܒܪܢܫ")),
    ("divinity/lord-of-all", re.compile(r"ܐܠܗܘܬ"), re.compile(r"ܡܪܟܠ|ܪܘܚܩܘܕܫ")),
    ("divinity/immortal", re.compile(r"ܐܠܗܘܬ"), re.compile(r"ܠܐ ܡܝܘܬ")),
    ("humanity/greatness", re.compile(r"ܐܢܫܘܬ"), re.compile(r"ܪܒܘܬ")),
    ("nature/like-man", re.compile(r"ܟܝܢܐ ܕܐܢܫ"), re.compile(r"ܐܝܟ ܒܪܢܫ")),
    ("theotokos", re.compile(r"ܝܠܕܬ ܡܫܝܚ|ܐܡܐ ܕܡܫܝܚ"), re.compile(r"ܝܠܕܬ ܐܠܗ|ܐܡܐ ܕܐܠܗ|ܐܡܗ ܕܐܠܗ")),
    ("christ/god", re.compile(r"ܡܫܝܚܐ"), re.compile(r"ܐܠܗܐ")),
    ("taken/embodied", re.compile(r"ܐܬܢܣܒ"), re.compile(r"ܐܬܓܫܡ")),
    ("doctors", re.compile(r"ܕܝܘܕܘܪ|ܬܐܕܘܪ|ܢܣܛܘܪ"), re.compile(r"ܓܪܝܓ|ܐܡܒܪ|ܐܦܪܝܡ|ܐܬܢܣ|ܝܘܐܢ|ܝܘܚܢܢ")),
    ("lordship/divinity", re.compile(r"ܡܪܘܬ"), re.compile(r"ܐܠܗܘܬ")),
    ("honor/qnoma", re.compile(r"ܐܝܩܪ"), re.compile(r"ܩܢܘܡ")),
    ("united-body/worshipped-body", re.compile(r"ܦܓܪܗ ܡܚܝܕ|ܡܚܝܕܐ"), re.compile(r"ܦܓܪܐ ܣܓܝܕ|ܣܓܝܕܐ")),
    ("properties/qnome", re.compile(r"ܒܩܢܘܡܝ"), re.compile(r"ܒܕܝܠܝܬ")),
    ("purple/nature", re.compile(r"ܐܪܓܘܢ"), re.compile(r"ܟܝܢܐ ܐܢܫ")),
]

NOISE_INSERT = re.compile(
    r"ܬܫܡܫܬܢ|ܐܒܘܢ ܕܒܫܡܝܐ|ܢܨܠܐ ܫܠܡܐ|ܥܘܢܝܬܐ ܕܓܘܐ|ܗܠܠܘܝ|"
    r"ܫܒܚܘ ܠܡܪܝܐ|ܣܝܡܝܢܢ ܬܘܟܠܢ"
)


def load_units():
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    idx = json.loads((ROOT / "data/index.json").read_text())
    syr, chd = [], []
    for meta in idx["prayers"]:
        pid = meta["itemId"]
        data = json.loads((ROOT / "data/prayers" / f"{pid}.json").read_text())
        html = data.get("html") or ""
        if not html:
            continue
        trad = (data.get("tradition") or meta.get("tradition") or ["?"])[0]
        for b in extract_hymn_blocks(html):
            rec = {
                "id": pid,
                "trad": trad,
                "holiday": meta.get("holiday"),
                "time": meta.get("prayerTime"),
                "genre": b["genre"],
                "text": b["text"],
                "norm": b["norm"],
                "n_tok": b["n_tok"],
                "open8": b["open8"],
            }
            if trad == "syriac":
                syr.append(rec)
            elif trad == "chaldean":
                chd.append(rec)
    CACHE.write_text(json.dumps({"syr": syr, "chd": chd}, ensure_ascii=False))
    return {"syr": syr, "chd": chd}


def dedup(units):
    seen = {}
    out = []
    for u in units:
        h = u["norm"]
        if h in seen:
            seen[h]["n_occ"] += 1
            continue
        u = dict(u)
        u["n_occ"] = 1
        seen[h] = u
        out.append(u)
    return out


def grams(toks, n=6):
    return [" ".join(toks[i : i + n]) for i in range(0, max(0, len(toks) - n + 1), 3)]


def classify_diff(syr: str, chd: str) -> list[str]:
    tags = []
    for name, a, b in SUB_PATTERNS:
        if (a.search(syr) and b.search(chd)) or (a.search(chd) and b.search(syr)):
            tags.append(name)
        elif a.search(syr) and not a.search(chd) and b.search(chd) and not b.search(syr):
            tags.append(name)
    return tags


def is_known(open8: str) -> bool:
    return any(open8.startswith(k) for k in KNOWN_OPENS)


def main():
    units = load_units()
    syr_u = dedup(units["syr"])
    chd_u = dedup(units["chd"])
    print(f"unique syr={len(syr_u)} chd={len(chd_u)}")

    inv_open8 = defaultdict(list)
    inv_open4 = defaultdict(list)
    inv_pfx = defaultdict(list)
    inv_gram = defaultdict(list)
    inv_tail = defaultdict(list)
    for i, u in enumerate(chd_u):
        toks = u["norm"].split()
        inv_open8[u["open8"]].append(i)
        inv_open4[" ".join(toks[:4])].append(i)
        inv_pfx[u["norm"][:40]].append(i)
        inv_tail[" ".join(toks[-8:])].append(i)
        for g in grams(toks, 6)[:12]:
            inv_gram[g].append(i)

    hits = []
    compared = 0
    seen_pair = set()
    for s in syr_u:
        toks = s["norm"].split()
        cand = set()
        cand.update(inv_open8.get(s["open8"], ()))
        cand.update(inv_open4.get(" ".join(toks[:4]), ()))
        cand.update(inv_pfx.get(s["norm"][:40], ()))
        cand.update(inv_tail.get(" ".join(toks[-8:]), ()))
        for g in grams(toks, 6)[:12]:
            cand.update(inv_gram.get(g, ()))
        for j in cand:
            c = chd_u[j]
            key = (s["norm"], c["norm"])
            if key in seen_pair:
                continue
            seen_pair.add(key)
            ls, lc = s["n_tok"], c["n_tok"]
            if min(ls, lc) / max(ls, lc) < 0.62:
                continue
            if s["norm"] == c["norm"]:
                continue
            compared += 1
            ratio = SequenceMatcher(None, s["norm"], c["norm"], autojunk=False).ratio()
            if ratio < 0.70 or ratio >= 0.9995:
                continue
            diffs, n_sub, n_ins, n_del = word_diff(s["norm"], c["norm"])
            total = n_sub + n_ins + n_del
            if total == 0:
                continue
            # allow larger recensions, but not wholesale rewrite
            if total > max(40, int(0.38 * max(ls, lc))):
                continue
            content = [d for d in diffs if not is_ortho_only(d["syr"], d["chd"])]
            if not content:
                continue
            # drop pure liturgical-glue inserts as the only signal
            tagged = []
            for d in content:
                if NOISE_INSERT.search((d["syr"] or "") + " " + (d["chd"] or "")):
                    continue
                tags = classify_diff(d["syr"] or "", d["chd"] or "")
                if tags:
                    tagged.append({**d, "tags": tags})
            if not tagged:
                continue
            hits.append(
                {
                    "ratio": round(ratio, 4),
                    "n_sub": n_sub,
                    "n_ins": n_ins,
                    "n_del": n_del,
                    "n_content": len(content),
                    "n_tagged": len(tagged),
                    "tags": sorted({t for d in tagged for t in d["tags"]}),
                    "known": is_known(s["open8"]),
                    "open": s["open8"],
                    "genre_s": s["genre"],
                    "genre_c": c["genre"],
                    "syr": {
                        "id": s["id"],
                        "holiday": s["holiday"],
                        "time": s["time"],
                        "n_occ": s["n_occ"],
                        "n_tok": s["n_tok"],
                    },
                    "chd": {
                        "id": c["id"],
                        "holiday": c["holiday"],
                        "time": c["time"],
                        "n_occ": c["n_occ"],
                        "n_tok": c["n_tok"],
                    },
                    "tagged": tagged[:10],
                    "other_content": [
                        d
                        for d in content
                        if d not in [{k: v for k, v in x.items() if k != "tags"} for x in tagged]
                    ][:6],
                    "syr_snip": s["norm"][:240],
                    "chd_snip": c["norm"][:240],
                    "syr_text": s["text"][:500],
                    "chd_text": c["text"][:500],
                }
            )

    # collapse by opening + tag signature
    uniq = {}
    for h in hits:
        sig = (h["open"][:40], tuple(h["tags"]), tuple((d["syr"][:40], d["chd"][:40]) for d in h["tagged"][:4]))
        prev = uniq.get(sig)
        occ = h["syr"]["n_occ"] + h["chd"]["n_occ"]
        if prev is None or occ > prev["syr"]["n_occ"] + prev["chd"]["n_occ"]:
            uniq[sig] = h
    hits_u = sorted(uniq.values(), key=lambda h: (h["known"], -h["n_tagged"], -h["ratio"]))
    new = [h for h in hits_u if not h["known"]]
    print(f"compared={compared} tagged_hits={len(hits)} unique={len(hits_u)} new={len(new)}")
    print("tag counts", Counter(t for h in hits_u for t in h["tags"]))

    print("\n=== NEW RECENSIONS ===")
    for i, h in enumerate(new[:50], 1):
        print(f"\n{i}. r={h['ratio']} tags={h['tags']} occ={h['syr']['n_occ']}+{h['chd']['n_occ']} e={h['n_sub']}+{h['n_ins']}+{h['n_del']}")
        print(f"   {h['open']}")
        print(f"   S:{h['syr']['holiday']} · {h['syr']['time']} · {h['syr']['id'][:8]}")
        print(f"   C:{h['chd']['holiday']} · {h['chd']['time']} · {h['chd']['id'][:8]}")
        for d in h["tagged"][:5]:
            print(f"     [{','.join(d['tags'])}] {d['syr'][:90]!r} → {d['chd'][:90]!r}")

    OUT.write_text(
        json.dumps(
            {
                "stats": {
                    "compared": compared,
                    "tagged_raw": len(hits),
                    "unique": len(hits_u),
                    "new": len(new),
                    "tag_counts": Counter(t for h in hits_u for t in h["tags"]),
                },
                "new": new[:80],
                "known_also": [h for h in hits_u if h["known"]][:20],
            },
            ensure_ascii=False,
            indent=2,
            default=int,
        )
    )
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
