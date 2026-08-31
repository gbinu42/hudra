#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compare hymn *bodies* across editions (skip rubrics + shuraye)."""

from __future__ import annotations

import json
import re
import html as htmlmod
from collections import defaultdict, Counter
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "scripts/_hymn_near_dupes.json"

VOWELS = set("ܸܹܼ݂݄݈̱̮ܲܵܿ݁݃݇̄̇̈̃\u0308\u0323\u0331\u0307\u0303̤")
PUNCT = set('܀܁܂܃.:;*·\u00a0\u200b()[]،؛?!«»"\'-/\\|–—')
RUBRIC_RE = re.compile(
    r'color\s*:\s*#(?:ee0000|ff0000|c00000|dc143c|e60000|2e74b5|2e75b6|'
    r'0f4761|104862|5b9bd5|4f81bd|365f91|376092|215e99|0070c0|00b0f0|'
    r'004e9a|004f88|0066cc|0563c1|467886|31849b)\b',
    re.I,
)
TAG_RE = re.compile(r"<[^>]+>")
SPAN_SPLIT = re.compile(r"(</?span[^>]*>)", re.I)

# Genre labels that start a hymn unit (normalized consonants).
HYMN_GENRE = re.compile(
    r"(?:^| )"
    r"(?:ܥܘܢܝܬܐ|ܥܘܢܝܬ|ܥܘܢܝܐ|ܥܘܢܝ̈ܬܐ|"
    r"ܩܠܐ|ܩܠܬܐ|ܩܠ̈ܐ|"
    r"ܬܫܒܘܚܬܐ|"
    r"ܡܕܪܫܐ|"
    r"ܣܘܓܝܬܐ|"
    r"ܫܘܚܠܦ|ܫܘܚܠܦܐ|"
    r"ܒܬ̈ܐ|ܒܬܐ)"
    r"(?: |$)"
)

# Sections we do not treat as hymns.
SKIP_GENRE = re.compile(
    r"(?:^| )"
    r"(?:ܨܠܘܬܐ|ܨܠܘܬ|"
    r"ܡܙܡܘܪܐ|ܡܙܡܘܪ|"
    r"ܗܘܠܠܐ|"
    r"ܩܢܘܢܐ|"
    r"ܟܪܘܙܘܬܐ|"
    r"ܚܙܝ|"
    r"ܫܒܚ|ܥܠܡ|"
    r"ܐܩܦ|"
    r"ܢܩܘܡ|"
    r"ܘܐܡܪ|ܘܥܢܝܢ|ܘܡܩܦ)"
    r"(?: |$)"
)

BOILERPLATE_STARTS = (
    "ܐܒܘܢ ܕܒܫܡܝܐ",
    "ܫܘܒܚܐ ܠܐܒܐ ܘܠܒܪܐ",
    "ܢܩܘܡ ܠܨܠܘܬܐ",
    "ܢܨܠܐ ܫܠܡܐ",
    "ܒܪܟ ܡܪܝ",
    "ܡܢ ܥܠܡ ܘܥܕܡܐ",
    "ܗܠܠܘܝܗ ܗܠܠܘܝܗ",
    "ܫܘܒܚܐ ܠܟ ܐܠܗܐ",
)

THEO_HINTS = (
    "ܦܪܨܘܦ",
    "ܩܢܘܡ",
    "ܟܝܢ",
    "ܝܠܕܬ",
    "ܐܡܐ ܕܐܠܗ",
    "ܐܡܗ ܕܐܠܗ",
    "ܐܡܐ ܕܡܫܝܚ",
    "ܝܠܕܬ ܐܠܗ",
    "ܝܠܕܬ ܡܫܝܚ",
    "ܡܚܝܕ",
    "ܐܝܩܪ",
    "ܕܝܠܝܬ",
    "ܐܠܗܘܬ",
    "ܐܢܫܘܬ",
    "ܒܪܘܬ",
    "ܐܘܣܝ",
    "ܨܒܝܢ",
    "ܣܓܝܕ",
    "ܬܠܝܬܝܘܬ",
    "ܡܪܝܡ",
    "ܒܬܘܠ",
)


def strip_norm(s: str) -> str:
    out = []
    for c in s:
        if c in VOWELS or c in PUNCT:
            continue
        if c.isspace():
            out.append(" ")
        else:
            out.append(c)
    return re.sub(r"\s+", " ", "".join(out)).strip()


def is_psalm_like(norm: str, raw_black: str) -> bool:
    if not norm:
        return True
    toks = norm.split()
    if len(toks) < 8:
        return True
    stars = raw_black.count("*") + raw_black.count("\u002a")
    if stars >= 4 and stars / max(len(toks), 1) > 0.08:
        return True
    # numbered psalm verses: "1 ܫܒܚܘ" or many isolated digits
    if re.search(r"(?:^|\s)\d{1,3}\s+\S", raw_black) and stars >= 2:
        return True
    hallel = toks.count("ܗܠܠܘܝܗ") + toks.count("ܐܗܠܠܘܝܗ")
    if hallel >= 4 and hallel / len(toks) > 0.12:
        return True
    if any(norm.startswith(b) for b in BOILERPLATE_STARTS):
        return True
    return False


def parse_html_runs(html: str) -> list[tuple[bool, str]]:
    """Return [(is_rubric, text), ...] in document order."""
    if not html:
        return []
    # Work paragraph by paragraph so we don't glue unrelated hymns.
    paras = re.split(r"</p\s*>", html, flags=re.I)
    runs: list[tuple[bool, str]] = []
    for para in paras:
        parts = SPAN_SPLIT.split(para)
        rubric = False
        buf: list[str] = []
        flushed_any = False

        def flush():
            nonlocal buf, flushed_any
            if not buf:
                return
            text = htmlmod.unescape(TAG_RE.sub("", "".join(buf)))
            text = re.sub(r"\s+", " ", text).strip()
            buf = []
            if text:
                runs.append((rubric, text))
                flushed_any = True

        for part in parts:
            if part.lower().startswith("<span"):
                flush()
                rubric = bool(RUBRIC_RE.search(part))
                continue
            if part.lower().startswith("</span"):
                flush()
                rubric = False
                continue
            if part.startswith("<"):
                # other tags: treat as soft break if block-ish
                if re.match(r"<br\b|<p\b", part, re.I):
                    flush()
                continue
            buf.append(part)
        flush()
        if flushed_any:
            runs.append((True, "¶"))  # paragraph boundary as pseudo-rubric break
    return runs


def extract_hymn_blocks(html: str) -> list[dict]:
    runs = parse_html_runs(html)
    blocks: list[dict] = []
    current_genre = None
    in_hymn = False
    black_parts: list[str] = []
    red_long_parts: list[str] = []  # qanona-style onitha in red

    def emit():
        nonlocal black_parts, red_long_parts, current_genre, in_hymn
        black = re.sub(r"\s+", " ", " ".join(black_parts)).strip()
        red_long = re.sub(r"\s+", " ", " ".join(red_long_parts)).strip()
        # Prefer black hymn body; if empty, keep long red poetic refrain.
        body = black if len(strip_norm(black).split()) >= 20 else red_long
        black_parts = []
        red_long_parts = []
        if not body:
            return
        if is_psalm_like(strip_norm(body), body):
            return
        n = strip_norm(body)
        toks = n.split()
        if len(toks) < 25:
            return
        blocks.append(
            {
                "genre": current_genre or "?",
                "text": body,
                "norm": n,
                "n_tok": len(toks),
                "open8": " ".join(toks[:8]),
            }
        )

    for is_rubric, text in runs:
        if text == "¶":
            # paragraph break inside a hymn: keep accumulating
            continue
        nlab = strip_norm(text)
        if is_rubric:
            if HYMN_GENRE.search(" " + nlab + " ") or HYMN_GENRE.search(nlab):
                emit()
                current_genre = nlab[:40]
                in_hymn = True
                continue
            if SKIP_GENRE.search(" " + nlab + " ") and len(nlab.split()) <= 12:
                emit()
                in_hymn = False
                current_genre = None
                continue
            # short rubric / shuraya (psalm incipit): skip text, stay in hymn
            if in_hymn:
                nt = nlab.split()
                if len(nt) >= 25 and not is_psalm_like(nlab, text):
                    # long red poetic block (qanona onitha)
                    red_long_parts.append(text)
                # else: rubric label or shuraya — drop
            continue
        # non-rubric
        if in_hymn:
            black_parts.append(text)
        else:
            # orphan black poetic block? only keep if clearly hymn-length and not psalm
            # Start implicit unit for mothwa-style where genre rubric was missed.
            if len(strip_norm(text).split()) >= 40 and not is_psalm_like(strip_norm(text), text):
                if not black_parts:
                    current_genre = current_genre or "orphan"
                    in_hymn = True
                black_parts.append(text)
    emit()
    return blocks


def word_diff(a: str, b: str) -> list[dict]:
    ta, tb = a.split(), b.split()
    sm = SequenceMatcher(None, ta, tb, autojunk=False)
    diffs = []
    n_sub_tok = 0
    n_ins = n_del = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        left = " ".join(ta[i1:i2])
        right = " ".join(tb[j1:j2])
        diffs.append({"op": tag, "syr": left, "chd": right})
        if tag == "replace":
            n_sub_tok += max(i2 - i1, j2 - j1)
        elif tag == "insert":
            n_ins += j2 - j1
        else:
            n_del += i2 - i1
    return diffs, n_sub_tok, n_ins, n_del


def is_ortho_only(a: str, b: str) -> bool:
    """True if the only difference is spacing/concatenation or 1–2 letters."""
    aa, bb = a.replace(" ", ""), b.replace(" ", "")
    if aa == bb:
        return True
    if abs(len(aa) - len(bb)) <= 2 and SequenceMatcher(None, aa, bb).ratio() >= 0.92:
        return True
    return False


def diff_is_theo(d: dict) -> bool:
    blob = (d.get("syr") or "") + " " + (d.get("chd") or "")
    return any(h in blob for h in THEO_HINTS)


def main() -> None:
    idx = json.loads((ROOT / "data/index.json").read_text())
    prayers = idx["prayers"]

    syr_units: list[dict] = []
    chd_units: list[dict] = []
    genre_counts = Counter()
    n_prayers = 0
    n_html_missing = 0

    for meta in prayers:
        pid = meta["itemId"]
        jp = ROOT / "data/prayers" / f"{pid}.json"
        data = json.loads(jp.read_text())
        html = data.get("html") or ""
        if not html:
            n_html_missing += 1
            continue
        n_prayers += 1
        trad = (data.get("tradition") or meta.get("tradition") or ["?"])[0]
        blocks = extract_hymn_blocks(html)
        for b in blocks:
            genre_counts[b["genre"][:20]] += 1
            rec = {
                **b,
                "id": pid,
                "trad": trad,
                "holiday": meta.get("holiday"),
                "time": meta.get("prayerTime"),
                "week": meta.get("week"),
                "day": meta.get("day"),
            }
            if trad == "syriac":
                syr_units.append(rec)
            elif trad == "chaldean":
                chd_units.append(rec)

    print(f"prayers with html: {n_prayers} missing_html={n_html_missing}")
    print(f"hymn units syriac={len(syr_units)} chaldean={len(chd_units)}")
    print("top genres", genre_counts.most_common(15))

    # Dedup within tradition by exact norm (keep one witness).
    def dedup(units: list[dict]) -> list[dict]:
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

    syr_u = dedup(syr_units)
    chd_u = dedup(chd_units)
    print(f"unique norms syriac={len(syr_u)} chaldean={len(chd_u)}")

    # Index chaldean by opening keys + char prefix.
    inv_open: dict[str, list[int]] = defaultdict(list)
    inv_open4: dict[str, list[int]] = defaultdict(list)
    inv_pfx: dict[str, list[int]] = defaultdict(list)
    inv_mid: dict[str, list[int]] = defaultdict(list)
    for i, u in enumerate(chd_u):
        toks = u["norm"].split()
        inv_open[u["open8"]].append(i)
        inv_open4[" ".join(toks[:4])].append(i)
        inv_pfx[u["norm"][:48]].append(i)
        if len(toks) >= 20:
            inv_mid[" ".join(toks[12:18])].append(i)

    pairs = []
    compared = 0
    for s in syr_u:
        toks = s["norm"].split()
        cand_idx = set()
        for key_map, key in (
            (inv_open, s["open8"]),
            (inv_open4, " ".join(toks[:4])),
            (inv_pfx, s["norm"][:48]),
            (inv_mid, " ".join(toks[12:18]) if len(toks) >= 20 else ""),
        ):
            if key:
                cand_idx.update(key_map.get(key, ()))
        if not cand_idx:
            continue
        for j in cand_idx:
            c = chd_u[j]
            # length filter
            ls, lc = s["n_tok"], c["n_tok"]
            if min(ls, lc) / max(ls, lc) < 0.72:
                continue
            if s["norm"] == c["norm"]:
                continue
            compared += 1
            ratio = SequenceMatcher(None, s["norm"], c["norm"], autojunk=False).ratio()
            if ratio < 0.82 or ratio >= 0.999:
                continue
            diffs, n_sub, n_ins, n_del = word_diff(s["norm"], c["norm"])
            total_edit = n_sub + n_ins + n_del
            # "a few words" — not wholesale rewrite
            if total_edit > max(28, int(0.18 * max(ls, lc))):
                continue
            if total_edit == 0:
                continue
            content_diffs = [d for d in diffs if not is_ortho_only(d["syr"], d["chd"])]
            if not content_diffs:
                kind = "orthographic"
            else:
                kind = "lexical"
            theo_diffs = [d for d in content_diffs if diff_is_theo(d)]
            pairs.append(
                {
                    "ratio": round(ratio, 4),
                    "n_sub": n_sub,
                    "n_ins": n_ins,
                    "n_del": n_del,
                    "n_content": len(content_diffs),
                    "n_theo": len(theo_diffs),
                    "kind": kind,
                    "has_theo": bool(theo_diffs),
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
                    "diffs": content_diffs[:12] if content_diffs else diffs[:8],
                    "theo_diffs": theo_diffs[:8],
                    "syr_snip": s["norm"][:220],
                    "chd_snip": c["norm"][:220],
                }
            )

    # Dedup pairs by (open8, frozenset of diff tuples) so repeated feast use collapses.
    uniq = {}
    for p in pairs:
        sig = (
            p["open"],
            tuple((d["op"], d["syr"], d["chd"]) for d in p["diffs"]),
        )
        prev = uniq.get(sig)
        if prev is None or p["syr"]["n_occ"] + p["chd"]["n_occ"] > prev["syr"]["n_occ"] + prev["chd"]["n_occ"]:
            uniq[sig] = p
    pairs_u = sorted(
        uniq.values(),
        key=lambda p: (
            0 if p["has_theo"] else 1,
            -p["n_content"],
            -p["ratio"],
        ),
    )
    print(f"candidate comparisons={compared} near-dup pairs={len(pairs)} unique={len(pairs_u)}")
    print(
        "kinds",
        Counter(p["kind"] for p in pairs_u),
        "theo",
        sum(1 for p in pairs_u if p["has_theo"]),
        "lexical",
        sum(1 for p in pairs_u if p["kind"] == "lexical"),
    )

    # Print a readable digest
    print("\n=== THEO-MARKED LEXICAL PAIRS ===")
    theo_pairs = [p for p in pairs_u if p["has_theo"] and p["kind"] == "lexical"]
    for i, p in enumerate(theo_pairs[:40], 1):
        print(f"\n{i}. r={p['ratio']} edits={p['n_sub']}+{p['n_ins']}+{p['n_del']} occ={p['syr']['n_occ']}/{p['chd']['n_occ']}")
        print(f"   {p['open'][:70]}")
        print(f"   syr {p['syr']['holiday']} · {p['syr']['time']} · {p['syr']['id'][:8]}")
        print(f"   chd {p['chd']['holiday']} · {p['chd']['time']} · {p['chd']['id'][:8]}")
        for d in p["theo_diffs"] or p["diffs"][:6]:
            print(f"     [{d['op']}] {d['syr'][:80]!r} → {d['chd'][:80]!r}")

    print("\n=== OTHER LEXICAL (no theo hint) top 25 ===")
    other = [p for p in pairs_u if p["kind"] == "lexical" and not p["has_theo"]]
    for i, p in enumerate(other[:25], 1):
        print(f"\n{i}. r={p['ratio']} n_content={p['n_content']} occ={p['syr']['n_occ']}/{p['chd']['n_occ']}")
        print(f"   {p['open'][:70]}")
        for d in p["diffs"][:5]:
            print(f"     [{d['op']}] {d['syr'][:90]!r} → {d['chd'][:90]!r}")

    payload = {
        "stats": {
            "prayers": n_prayers,
            "units_syr": len(syr_units),
            "units_chd": len(chd_units),
            "unique_syr": len(syr_u),
            "unique_chd": len(chd_u),
            "pairs_raw": len(pairs),
            "pairs_unique": len(pairs_u),
            "theo_lexical": len(theo_pairs),
            "lexical": sum(1 for p in pairs_u if p["kind"] == "lexical"),
            "orthographic": sum(1 for p in pairs_u if p["kind"] == "orthographic"),
            "genres": genre_counts.most_common(20),
        },
        "theo_pairs": theo_pairs[:60],
        "other_lexical": other[:40],
        "orthographic_sample": [p for p in pairs_u if p["kind"] == "orthographic"][:15],
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
