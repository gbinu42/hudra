#!/usr/bin/env python3
"""Extract ܕܩܢܟܐ and ܕܐܪܙܐ onyatha from Divine Mysteries offices.

Writes web/data/qanka-raza.json for the listing page.
"""

from __future__ import annotations

import html as htmlmod
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "web" / "data" / "catalog.json"
PRAYERS = ROOT / "data" / "prayers"
OUT = ROOT / "web" / "data" / "qanka-raza.json"

RUBRIC_RE = re.compile(
    r"color\s*:\s*#(?:ee0000|ff0000|c00000|dc143c|e60000|2e74b5|2e75b6|"
    r"0f4761|104862|5b9bd5|4f81bd|365f91|376092|215e99|0070c0|00b0f0|"
    r"004e9a|004f88|0066cc|0563c1|467886|31849b)\b",
    re.I,
)
SPAN_SPLIT = re.compile(r"(</?span[^>]*>)", re.I)
TAG_RE = re.compile(r"<[^>]+>")
VOWELS = set("ܸܹܼ݂݄݈̱̮ܲܵܿ݁݃݇̄̇̈̃\u0308\u0323\u0331\u0307\u0303̤")
PUNCT = set("܀܁܂܃.:;*·\u00a0\u200b()[]،؛?!«»\"'/-/\\|–—")

# Qanke / raze labels must be the heading, not a mid-sentence mention.
# Chaldean Qurbana often writes ܘܢܦܩܝܢ ܒܥܘܢܝܬܐ ܕܩܢܟܐ as one rubric.
# Do not require end-of-string: ܥܘܢܝܬܐ ܕܩܢܟܐ ܒܩܠ and ܕܩܢܟܐ + psalm
# in the same span still start the onitha. Long ܘܢܦܩܝܢ ܒܗܕܐ … ܠܕܪܬܐ
# processional rubrics do not match this prefix.
QANKA_START = re.compile(
    r"^(?:ܘ?ܢܦܩ\w*\s+)?(?:ܒ?ܥܘܢܝ(?:ܬܐ|ܐ)\s+)?ܕܩܢܟ"
)
RAZA_START = re.compile(r"^(?:ܥܘܢܝ(?:ܬܐ|ܐ)\s+)?ܕܐܪܙ")
SKIP_RAZA = re.compile(r"ܡܪܡܝ|ܢܩܦ|ܠܩܛ|ܩܪܝܢ|ܩܕܝܫ|ܛܟܣ")
# Door / sealing of the qanke — not the onitha. ܢܦܩ is allowed in QANKA_START.
SKIP_QANKA = re.compile(r"ܬܪܥ|ܚܘܬܡ")
ONYA_RE = re.compile(r"^ܥܘܢܝ(?:ܬܐ|ܐ)?$")
MARMITHA_RE = re.compile(r"ܡܪܡܝ")
NAQPYATA_RE = re.compile(r"ܢܩܦ")
AQAPTA_RE = re.compile(r"ܐܩܦܬ")
# In-hymn cues to keep as <span class="rubric">.
KEEP_RUBRIC = re.compile(
    r"^(?:ܫܒܚ|ܬܢܝ|ܥܠܡ|ܒܩܠ|ܕܨܘܪܬܐ|ܗܝ\s+ܗܝ|ܪܫܩܠ|ܒܩܠܐ)"
)
# Psalm verses that often sit between marmitha and the real onitha.
PSALM_LINE = re.compile(
    r"^(?:ܘ?ܒܥܡܡܐ\s+ܣܓܝܐܐ|ܐܒܪܟ\s+ܠܡܪܝܐ|ܐܘܕܐ\s+ܠܟ|"
    r"ܟܗܢܝܟ\s+ܢܠܒܫܘܢ|ܡܛܠ\s+ܕܛܒܝܢ\s+ܪܚܡܝܟ|"
    r"ܡܫܒܚ\s+ܒܡܪܘܡܐ\s+ܡܪܝܐ\s+ܡܒܛܠ)"
)
# After the onitha the office continues with lections / the anaphora.
# Use ܩܪܝܢܐ (not ܩܪܝܢ) so melody ܠܟܘ ܩܪܝܢܢ is kept; ܫܘܪܝܐ not ܫܘܪܝ
# so ܒܫܘܪܝ melody names are kept. Do not stop on ܩܘܕܫ inside hymn text.
# Anchor ܫܠܝܚܐ / ܗܝܡܢܘܬ so hymn lines that mention an apostle or "faith"
# are not treated as the lection or Creed. ܘܐܡܪܝܢ starts congregational
# text (Creed, Lakhu Mara, …), not the onitha.
STOP_QANKA = re.compile(
    r"ܩܪܝܢܐ|ܫܘܪܝܐ|^ܫܠܝܚܐ|ܙܘܡܪܐ|ܐܘܢܓܠ|ܕܐܪܙ|ܚܒܪܗ|ܕܡܦܫܩ|^ܕܒܝܡ|^ܘܐܡܪܝܢ"
)
STOP_RAZA = re.compile(
    r"ܕܡܦܫܩ|^ܩܪܝܢܐ|^ܫܠܝܚܐ|ܐܘܢܓܠ|^ܕܒܝܡ|^ܗܝܡܢܘܬ|"
    r"^ܘܐܡܪܝܢ|ܘܡܩܕܫ|ܢܩܦ"
)
STOP_LECTION = re.compile(r"^(?:ܕ?ܡܦܫܩ|ܩܪܝܢܐ)\b")
LECTION_BOOKS = frozenset({
    "ܒܪܝܬܐ",
    "ܐܫܥܝܐ",
    "ܠܘܩܐ",
    "ܡܬܝ",
    "ܡܪܩܘܣ",
    "ܝܘܚܢܢ",
    "ܐܦܣܝ",
    "ܪܗܘܡܝ",
    "ܩܘܪܢܬ",
    "ܥܒܪܝ",
    "ܓܠܛܝ",
    "ܩܘܠܣܝ",
    "ܦܝܠܝܦ",
    "ܡܥܒܕ",
})
# Chapter/verse crumbs after a book name (ܒܪܝܬܐ ܐ), not hymn text (ܒܪܝܬܐ ܒܡܪܗ).
LECTION_REST = re.compile(r"^[\d()[\]:\-–—ܐܒܓܕܗܘܙܚܛܝܟܠܡܢܣܥܦܨܩܪܫܬ\s]*$")
SKIP_BODY = re.compile(r"^(?:ܬܢܝ|ܬܪܝܢܐ?)$")
# Rubrics that belong to the office around the hymn, not the onitha itself.
SKIP_KEEP = re.compile(r"ܘܡܬܩܕܫ|ܘܡܩܕܫ")
# ܪ̈ܲܒܲܝ ܒܵܬܹ̈ܐ “heads of houses” is lyric, not the bate hymn cue.
BATE_HOUSE_PREV = frozenset({"ܪܒܝ", "ܘܪܒܝ"})


def is_lection_heading(nlab: str) -> bool:
    """True for a lection label, not hymn lines that happen to start with ܒܪܝܬܐ."""
    if not nlab:
        return False
    if STOP_LECTION.search(nlab):
        return True
    toks = nlab.split()
    if toks[0] not in LECTION_BOOKS:
        return False
    rest = " ".join(toks[1:])
    if not rest:
        return True
    if len(toks) > 5:
        return False
    return bool(LECTION_REST.fullmatch(rest)) and all(len(t) <= 2 for t in toks[1:])


def strip_norm(s: str) -> str:
    out: list[str] = []
    for c in s:
        if c in VOWELS or c in PUNCT:
            continue
        if c.isspace() or c in "\u200e\u200f\u200c\u200d\ufeff":
            out.append(" ")
        else:
            out.append(c)
    return re.sub(r"\s+", " ", "".join(out)).strip()


def is_bema_cue(token: str) -> bool:
    """Whole-word ܕܒܹܝܡ (bema hymn), not e.g. ܕܒ݂ܝܼܫܘܿܥ."""
    return strip_norm(token) == "ܕܒܝܡ"


def is_bate_cue(token: str, *, rubric: bool) -> bool:
    """Bate hymn ܒܵܬܹ̈ܐ (taw with rbhasa), not lyric ܒ݂̈ܵܬ݂ܵܐ / ܒ݂ܵܬ݂̈ܵܐ “houses”."""
    if strip_norm(token) != "ܒܬܐ":
        return False
    if rubric:
        return True
    return "ܹ" in token


# ܩܥܝܢ ܘܐܡܪܝܢ “they cry and say” is lyric; a rubric ܘܐܵܡܪܝܼܢ is not.
AMRIN_LYRIC_PREV = frozenset({"ܩܥܝܢ", "ܩܥܝܢܢ", "ܫܘܝܐܝܬ", "ܠܫܢܝܗܘܢ"})


def is_amrin_cue(token: str) -> bool:
    """ܘܐܵܡܪܝܼܢ introduces congregational text, not ܐܵܡܪܝܼܢܲܢ “we say”."""
    return strip_norm(token) == "ܘܐܡܪܝܢ"


def hymn_type_cue_index(text: str, *, rubric: bool) -> int | None:
    """First token that starts bate, bema, or ܘܐܡܪܝܢ, or None."""
    toks = text.split()
    for i, tok in enumerate(toks):
        if is_bema_cue(tok):
            return i
        if is_amrin_cue(tok):
            prev_n = strip_norm(toks[i - 1]) if i else ""
            nxt = strip_norm(toks[i + 1]) if i + 1 < len(toks) else ""
            # Rubric, or a new piece (Lakhu Mara / Creed), not mid-verse “and they say”.
            if rubric or i == 0 or nxt.startswith("ܠܟ") or nxt.startswith("ܗܝܡܢ") or nxt.startswith("ܩܕܝܫ"):
                return i
            if prev_n in AMRIN_LYRIC_PREV:
                continue
            return i
        if is_bate_cue(tok, rubric=rubric):
            prev_n = strip_norm(toks[i - 1]) if i else ""
            if prev_n in BATE_HOUSE_PREV:
                continue
            return i
    return None


def split_before_hymn_type(text: str, *, rubric: bool) -> tuple[str, bool]:
    """Keep text before a bate/bema/ܘܐܡܪܝܢ cue; drop the cue and everything after."""
    idx = hymn_type_cue_index(text, rubric=rubric)
    if idx is None:
        return text, False
    return " ".join(text.split()[:idx]), True


def parse_runs(html: str) -> list[tuple[bool, str]]:
    paras = re.split(r"</p\s*>", html, flags=re.I)
    runs: list[tuple[bool, str]] = []
    for para in paras:
        parts = SPAN_SPLIT.split(para)
        rubric = False
        buf: list[str] = []

        def flush() -> None:
            nonlocal buf
            if not buf:
                return
            text = htmlmod.unescape(TAG_RE.sub("", "".join(buf)))
            text = re.sub(r"\s+", " ", text).strip()
            buf = []
            if text:
                runs.append((rubric, text))

        for part in parts:
            low = part.lower()
            if low.startswith("<span"):
                flush()
                rubric = bool(RUBRIC_RE.search(part))
                continue
            if low.startswith("</span"):
                flush()
                rubric = False
                continue
            if part.startswith("<"):
                if re.match(r"<br\b|<p\b", part, re.I):
                    flush()
                continue
            buf.append(part)
        flush()
        if runs and runs[-1][1] != "¶":
            runs.append((True, "¶"))
    return runs


def classify(nlab: str, prev_nlab: str) -> tuple[str | None, int]:
    """Return (kind, specificity). Bare ܥܘܢܝܐ after marmitha is not qanke."""
    if QANKA_START.match(nlab) and not SKIP_QANKA.search(nlab):
        return "qanka", 2
    if prev_nlab and NAQPYATA_RE.search(prev_nlab) and re.match(r"^ܕܐܪܙ", nlab):
        return None, 0
    if SKIP_RAZA.search(nlab):
        return None, 0
    if RAZA_START.match(nlab):
        spec = 2 if nlab.startswith("ܥܘܢܝ") else 1
        return "raza", spec
    return None, 0


# Melody titles (not the onitha); ܠܟܘ ܩܪܝܢܢ often precedes a psalm verse.
MELODY_CUE = re.compile(
    r"^(?:ܒ?ܩܠ|ܒ?ܠܟ(?:ܘ|\s+ܗܘ)\s+ܩܪܝܢܢ)\b"
)


def is_cue(nlab: str) -> bool:
    return bool(
        KEEP_RUBRIC.search(nlab)
        or MELODY_CUE.search(nlab)
        or SKIP_BODY.search(nlab)
    )


def has_hymn_text(parts: list[tuple[bool, str]]) -> bool:
    saw_bqal = False
    for _, text in parts:
        n = strip_norm(text)
        if not n:
            continue
        if re.match(r"^ܒܩܠ", n):
            saw_bqal = True
            continue
        if is_cue(n):
            continue
        if QANKA_START.match(n) or RAZA_START.match(n):
            continue
        if saw_bqal and len(n.split()) <= 6:
            saw_bqal = False
            continue
        if len(n.split()) >= 2:
            return True
    return False


def starts_with_onyatha_label(n: str) -> bool:
    toks = n.split()
    for i in range(1, min(5, len(toks) + 1)):
        phrase = " ".join(toks[:i])
        if QANKA_START.match(phrase) or RAZA_START.match(phrase):
            return True
    return False


def body_quality(n: str) -> int:
    """0 = reject, 1 = weak psalm/marmitha, 2+ = real onitha (length bonus)."""
    toks = n.split()
    if len(toks) < 6:
        return 0
    if starts_with_onyatha_label(n):
        return 2 + min(len(toks), 80)
    head = " ".join(toks[:8])
    if MARMITHA_RE.search(head) or AQAPTA_RE.search(head) or NAQPYATA_RE.search(head):
        return 0
    if PSALM_LINE.search(n) and len(toks) < 18:
        return 1
    return 2 + min(len(toks), 80)


def tidy_run(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^[\[\]]+|[\[\]]+$", "", text).strip()
    return text


def render_body(parts: list[tuple[bool, str]]) -> tuple[str, str]:
    """Plain text + HTML with rubric spans (red in the listing)."""
    html_bits: list[str] = []
    plain_bits: list[str] = []
    for is_rubric, text in parts:
        t, hit = split_before_hymn_type(tidy_run(text), rubric=is_rubric)
        t = tidy_run(t)
        if t:
            plain_bits.append(t)
            esc = htmlmod.escape(t, quote=False)
            if is_rubric:
                html_bits.append(f'<span class="rubric">{esc}</span>')
            else:
                html_bits.append(esc)
        if hit:
            break
    plain = re.sub(r"\s+", " ", " ".join(plain_bits)).strip(" .")
    return plain, " ".join(html_bits)


def extract_hymns(html: str) -> dict[str, dict | None]:
    runs = parse_runs(html)
    # kind -> (body, html_body, norm, quality, specificity)
    found: dict[str, tuple[str, str, str, int, int]] = {}
    cur: str | None = None
    cur_spec = 0
    buf: list[tuple[bool, str]] = []
    prev_nlab = ""

    def emit() -> None:
        nonlocal buf, cur, cur_spec
        if cur and buf:
            body, html_body = render_body(buf)
            n = strip_norm(body)
            q = body_quality(n)
            prev = found.get(cur)
            # Overwrite only a missing or weak (psalm/marmitha) slot — keep the
            # first real onitha when an office HTML contains more than one.
            better = False
            if q >= 2:
                better = prev is None or prev[3] < 2
            elif q == 1 and (prev is None or prev[3] < 1):
                better = True
            if better:
                found[cur] = (body, html_body, n, q, cur_spec)
        buf = []
        cur = None
        cur_spec = 0

    def abandon() -> None:
        """Drop a false start (marmitha/psalm) without saving."""
        nonlocal buf, cur, cur_spec
        buf = []
        cur = None
        cur_spec = 0

    def stop_for(kind: str, nlab: str) -> bool:
        if kind == "qanka":
            return bool(STOP_QANKA.search(nlab))
        return bool(STOP_RAZA.search(nlab))

    def absorb(text: str, *, rubric: bool) -> bool:
        """Append text before a bate/bema/ܘܐܡܪܝܢ cue. Return True if the onitha ends."""
        before, hit = split_before_hymn_type(text, rubric=rubric)
        before = tidy_run(before)
        n_before = strip_norm(before)
        # Bare body ܬܢܝ is skipped as SKIP_BODY; rubric ܬܢܝ stays as a cue.
        # Keep ܒܵܗ̇ (often before ܕܒܝܡ / ܒܬܐ); still drop the bate/bema cue itself.
        if before:
            if rubric or not SKIP_BODY.search(n_before):
                buf.append((rubric, before))
        if hit:
            emit()
            return True
        return False

    for is_rubric, text in runs:
        if text == "¶":
            continue
        nlab = strip_norm(text)
        if is_rubric:
            kind, spec = classify(nlab, prev_nlab)
            prev_nlab = nlab
            if kind:
                if cur == kind and not has_hymn_text(buf):
                    abandon()
                else:
                    emit()
                cur = kind
                cur_spec = spec
                # Keep ܕܩܢܟܐ / ܕܐܪܙܐ (and ܥܘܢܝܬܐ ܕ…) as the start of the piece.
                absorb(text, rubric=True)
                continue
            if ONYA_RE.match(nlab):
                # Marmitha aqapta/onyaya, not ܕܩܢܟܐ.
                if cur and not has_hymn_text(buf):
                    abandon()
                continue
            if cur and MARMITHA_RE.search(nlab):
                if not has_hymn_text(buf):
                    abandon()
                else:
                    emit()
                continue
            if cur and NAQPYATA_RE.search(nlab):
                emit()
                continue
            if cur and stop_for(cur, nlab):
                emit()
                continue
            if cur and SKIP_KEEP.search(nlab):
                continue
            if cur:
                absorb(text, rubric=True)
            continue
        if cur:
            if is_lection_heading(nlab) and buf:
                emit()
                continue
            if SKIP_BODY.search(nlab) or text.strip("[] \t") == "":
                continue
            absorb(text, rubric=False)
    emit()

    out: dict[str, dict | None] = {}
    for kind in ("qanka", "raza"):
        if kind in found:
            body, html_body, n, _q, _s = found[kind]
            toks = n.split()
            html_body = html_body[:4000]
            html_body = re.sub(r"<[^>]*$", "", html_body)
            if html_body.count("<span") > html_body.count("</span>"):
                html_body += "</span>"
            out[kind] = {
                "text": body[:2000].rstrip(),
                "html": html_body.rstrip(),
                "incipit": " ".join(toks[:10]),
            }
        else:
            out[kind] = None
    return out


def tradition_of(p: dict) -> str | None:
    t = p.get("tradition") or []
    has_s = "syriac" in t
    has_c = "chaldean" in t
    if has_s and not has_c:
        return "syriac"
    if has_c and not has_s:
        return "chaldean"
    if has_s and has_c:
        return "syriac"
    return None


CYCLE_FEAST_IDS = {
    "yalda",
    "circumcision",
    "denha-feast",
    "lazarus",
    "hosannas",
    "passover",
    "passion",
    "great-saturday",
    "easter",
    "ascension",
    "pentecost",
}

# Keep in sync with web/src/lib/feast-when.ts (Friday observances only).
FRIDAY_SEASON_WHEN = {
    "feast-2e89fa4": "3rd Friday of Denha",
    "feast-c39114": "8th Friday of Denha · 9 March if omitted",
    "feast-2be17f0": "7th Friday of Denha",
    "feast-4c89af9": "5th Friday of Denha",
    "feast-e391d9": "6th Friday of Denha",
    "feast-eb0d6d": "4th Friday of Denha",
    "feast-456c531": "1st Friday of Denha",
    "feast-4b785d5": "2nd Friday of Denha · 29 June",
    "feast-41cbbb4": "1st Friday of Elijah",
    "feast-2a29855": "7th Friday of Summer",
    "feast-2f5fe3c": "6th Friday of Summer",
    "feast-5755736": "Last Friday between Nativity and Denha",
    "feast-5c4de48": "Last Friday of the Apostles",
    "feast-2f4b12a": "3rd Friday of the Apostles",
    "feast-212f9da": "1st Friday of the Apostles",
    "feast-4aa5463": "1st Friday after Easter",
    "feast-40cd970": "Last Friday of Denha",
}
FRIDAY_WHEN_HINT = (
    ("after-nativity", "Nativity and Denha"),
    ("denha", "of Denha"),
    ("apostles", "of the Apostles"),
    ("summer", "of Summer"),
    ("elijah-cross", "of Elijah"),
    ("resurrection", "after Easter"),
)


def week_number_from_label(week: str) -> int | None:
    letter = week_letter_of(week)
    if not letter:
        return None
    i = WEEK_LETTERS.find(letter)
    return i + 1 if i >= 0 else None


def _english_ordinal(n: int) -> str:
    v = n % 100
    if 11 <= v <= 13:
        return f"{n}th"
    return {1: f"{n}st", 2: f"{n}nd", 3: f"{n}rd"}.get(n % 10, f"{n}th")


def feast_season_ids_for_cycle_friday(
    season_id: str, week_num: int, last_week: int | None
) -> list[str]:
    needle = next((h[1] for h in FRIDAY_WHEN_HINT if h[0] == season_id), "")
    if not needle:
        return []
    ord_s = _english_ordinal(week_num)
    ids: list[str] = []
    for fid, when in FRIDAY_SEASON_WHEN.items():
        if "Friday" not in when or needle not in when:
            continue
        if f"{ord_s} Friday" in when:
            ids.append(fid)
        if (
            last_week is not None
            and week_num == last_week
            and when.startswith("Last Friday")
        ):
            ids.append(fid)
    return list(dict.fromkeys(ids))


def merge_edition_from_feast(ferial: dict | None, feast: dict | None) -> dict | None:
    """Prefer dukhrana Mysteries hymns; fill any slot the ferial Friday lacks."""
    if not feast or not (feast.get("qanka") or feast.get("raza")):
        return ferial
    if not ferial or not (ferial.get("qanka") or ferial.get("raza")):
        return feast
    return {
        **feast,
        "qanka": feast.get("qanka") or ferial.get("qanka"),
        "raza": feast.get("raza") or ferial.get("raza"),
    }


def attach_feast_hymns_to_cycle_fridays(occasions: list[dict]) -> None:
    """Cycle Fridays are listed as commemorations; their ferial Qurbana often
    has only raze. Copy qanke/raze from the dukhrana Mysteries for that Friday."""
    by_sid: dict[str, list[dict]] = defaultdict(list)
    last_week: dict[str, int] = {}
    for o in occasions:
        by_sid[o["seasonId"]].append(o)
        if o.get("seasonGroup") == "cycle" and o.get("dayEn") == "Friday":
            n = week_number_from_label(o.get("week") or "")
            if n:
                last_week[o["seasonId"]] = max(last_week.get(o["seasonId"], 0), n)
    for o in occasions:
        if o.get("seasonGroup") != "cycle" or o.get("dayEn") != "Friday":
            continue
        n = week_number_from_label(o.get("week") or "")
        if not n:
            continue
        for fid in feast_season_ids_for_cycle_friday(
            o["seasonId"], n, last_week.get(o["seasonId"])
        ):
            feasts = by_sid.get(fid) or []
            if not feasts:
                continue
            feast = feasts[0]
            for trad in ("syriac", "chaldean"):
                o[trad] = merge_edition_from_feast(o.get(trad), feast.get(trad))
            if feast.get("holidayEn") and not o.get("holidayEn"):
                o["holiday"] = feast.get("holiday") or o.get("holiday") or ""
                o["holidayEn"] = feast["holidayEn"]


def edition_score(hymns: dict) -> int:
    score = 0
    if hymns.get("qanka"):
        score += 2 + len(hymns["qanka"]["text"])
    if hymns.get("raza"):
        score += 2 + len(hymns["raza"]["text"])
    return score


def is_single_day_season(season: dict) -> bool:
    return season.get("group") in ("feast", "commemoration", "baotha") or season.get(
        "id"
    ) in CYCLE_FEAST_IDS


# Office titles start with the liturgical weekday; catalog `day`/`dayEn` sometimes
# follow the printed page (Chaldean 2nd Sunday of Subara filed under Monday).
WEEKDAY_PREFIXES = [
    ("Sunday", "ܚܕܒܫܒܐ"),
    ("Monday", "ܬܪܝܢܒܫܒܐ"),
    ("Tuesday", "ܬܠܬܒܫܒܐ"),
    ("Wednesday", "ܐܪܒܥܒܫܒܐ"),
    ("Thursday", "ܚܡܫܒܫܒܐ"),
    ("Friday", "ܥܪܘܒܬܐ"),
]
DAY_ORDER = {
    "Sunday": 1,
    "Monday": 2,
    "Tuesday": 3,
    "Wednesday": 4,
    "Thursday": 5,
    "Friday": 6,
    "Saturday": 7,
}
WEEK_LETTERS = "ܐܒܓܕܗܘܙܚܛܝܟܠܡܢܣܥܦܨܩܪܫܬ"


def weekday_from_name(name: str) -> str | None:
    n = strip_norm(name)
    if not n:
        return None
    for en, prefix in WEEKDAY_PREFIXES:
        if n.startswith(prefix):
            return en
    return None


def weekday_token_from_name(name: str) -> str:
    if not weekday_from_name(name):
        return ""
    return (name or "").replace("\n", " ").strip().split()[0]


def canonical_day_en(p: dict) -> str:
    return weekday_from_name(p.get("name") or "") or (p.get("dayEn") or "")


def week_letter_of(week: str) -> str:
    """Numeral letter from a catalog week label (ܫܒܬܐ ܐ/ܒ/…)."""
    n = strip_norm(week or "")
    if not n:
        return ""
    m = re.search(r"ܫܒܬܐ\s*([ܐ-ܬ])", n)
    if m:
        return m.group(1)
    tok = n.split()[-1]
    return tok if len(tok) == 1 and tok in WEEK_LETTERS else ""


def rest_after_weekday(name: str) -> str:
    n = strip_norm(name or "")
    for _, prefix in WEEKDAY_PREFIXES:
        if n.startswith(prefix):
            return n[len(prefix) :].strip()
    return ""


def week_letters_after_weekday(name: str) -> list[str]:
    """Standalone ܐ/ܒ/… after ܥܪܘܒܬܐ / ܚܕܒܫܒܐ (not dual Cross+Elijah titles)."""
    rest = rest_after_weekday(name)
    if not rest:
        return []
    return [tok for tok in rest.split() if len(tok) == 1 and tok in WEEK_LETTERS]


def name_week_is_season_week(name: str) -> bool:
    """True when the name's letter is the season week, not a sub-count (ܕܒܬܪ …)."""
    named = week_letters_after_weekday(name)
    if len(named) != 1:
        return False
    toks = rest_after_weekday(name).split()
    i = 1 if toks and toks[0] == named[0] else 0
    after = " ".join(toks[i:])
    return not (after.startswith("ܕܒܬܪ") or after.startswith("ܒܬܪ"))


def canonical_week_key(p: dict) -> str:
    """Week letter for grouping. Catalog week, unless the name is a unique other season week."""
    catalog = week_letter_of(p.get("week") or "")
    named = week_letters_after_weekday(p.get("name") or "")
    if (
        catalog
        and len(named) == 1
        and named[0] != catalog
        and name_week_is_season_week(p.get("name") or "")
    ):
        return named[0]
    if catalog:
        return catalog
    if len(named) == 1:
        return named[0]
    if named:
        return named[-1]
    return strip_norm(p.get("week") or "")


def occasion_key(p: dict, season: dict) -> tuple:
    if is_single_day_season(season):
        return (p["seasonId"], "", "")
    return (
        p["seasonId"],
        canonical_week_key(p),
        canonical_day_en(p),
    )


def is_listed_day(p: dict, season: dict) -> bool:
    """Sundays, feasts, and commemorations that must appear even without Qurbana."""
    if p.get("seasonId") == "unassigned":
        return False
    g = season.get("group")
    if g in ("feast", "commemoration", "baotha"):
        return True
    if p["seasonId"] in CYCLE_FEAST_IDS:
        return True
    day = weekday_from_name(p.get("name") or "") or p.get("dayEn")
    if day == "Sunday":
        return True
    if g == "cycle" and day == "Friday":
        return True
    return False


def office_rank(p: dict) -> tuple:
    myst = 0 if p.get("hourEn") == "Divine Mysteries" else 1
    order = p.get("hourOrder") if p.get("hourOrder") is not None else 99
    return (myst, order, -(p.get("chars") or 0))


def empty_hymns() -> dict:
    return {"qanka": None, "raza": None}


def hymns_from(p: dict) -> dict:
    path = PRAYERS / f"{p['id']}.json"
    if not path.exists():
        return empty_hymns()
    return extract_hymns(json.loads(path.read_text()).get("html") or "")


def make_edition(p: dict, hymns: dict | None = None) -> dict:
    hymns = hymns or empty_hymns()
    return {
        "id": p["id"],
        "name": p.get("name") or "",
        "qanka": hymns.get("qanka"),
        "raza": hymns.get("raza"),
    }


def make_placeholder(p: dict) -> dict:
    """Listed day with no Mysteries office — keep the title, not a Ramsha id."""
    return {
        "id": "",
        "name": p.get("name") or "",
        "qanka": None,
        "raza": None,
    }


def _prefers_week(current: str, incoming: str, want_letter: str) -> bool:
    if not incoming:
        return False
    if not current:
        return True
    inc_l = week_letter_of(incoming)
    cur_l = week_letter_of(current)
    if want_letter:
        if inc_l == want_letter and cur_l != want_letter:
            return True
        if inc_l != want_letter:
            return False
    return len(incoming) > len(current)


def apply_day_fields(meta: dict, p: dict, season: dict) -> None:
    if is_single_day_season(season):
        return
    named = weekday_from_name(p.get("name") or "")
    day_en = named or (p.get("dayEn") or "")
    if day_en and (not meta["dayEn"] or named):
        meta["dayEn"] = day_en
        meta["dayOrder"] = DAY_ORDER.get(
            day_en,
            p.get("dayOrder") if p.get("dayOrder") is not None else meta["dayOrder"],
        )
        if named and p.get("dayEn") != named:
            tok = weekday_token_from_name(p.get("name") or "")
            if tok:
                meta["day"] = tok
        elif p.get("day") and (not meta["day"] or p.get("dayEn") == day_en):
            meta["day"] = p["day"]
    elif not meta["day"] and p.get("day"):
        meta["day"] = p["day"]
    if meta["dayOrder"] == 99 and p.get("dayOrder") is not None:
        meta["dayOrder"] = p["dayOrder"]


def fill_meta(meta: dict, p: dict, season: dict, *, week_letter: str = "") -> None:
    """Prefer non-empty weekday / title fields as later prayers arrive."""
    if not is_single_day_season(season) and p.get("week"):
        if _prefers_week(meta["week"], p["week"], week_letter):
            meta["week"] = p["week"]
    apply_day_fields(meta, p, season)
    if not meta["holiday"] and p.get("holiday"):
        meta["holiday"] = p["holiday"]
    if not meta["holidayEn"] and p.get("holidayEn"):
        meta["holidayEn"] = p["holidayEn"]


def new_meta(p: dict, season: dict) -> dict:
    single = is_single_day_season(season)
    meta = {
        "seasonId": p["seasonId"],
        "week": "" if single else (p.get("week") or ""),
        "day": "" if single else (p.get("day") or ""),
        "dayEn": "" if single else canonical_day_en(p),
        "dayOrder": 99,
        "holiday": p.get("holiday") or "",
        "holidayEn": p.get("holidayEn") or "",
    }
    apply_day_fields(meta, p, season)
    if meta["dayOrder"] == 99 and p.get("dayOrder") is not None:
        meta["dayOrder"] = p["dayOrder"]
    return meta


def main() -> None:
    cat = json.loads(CATALOG.read_text())
    seasons = {s["id"]: s for s in cat["seasons"]}
    prayers = cat["prayers"]
    myst = [p for p in prayers if p.get("hourEn") == "Divine Mysteries"]

    editions: dict[tuple, dict[str, dict]] = defaultdict(dict)
    meta: dict[tuple, dict] = {}

    for p in myst:
        season = seasons.get(p["seasonId"], {})
        trad = tradition_of(p)
        if not trad:
            continue
        hymns = hymns_from(p)
        key = occasion_key(p, season)
        rec = make_edition(p, hymns)
        prev = editions[key].get(trad)
        if prev is None or edition_score(rec) > edition_score(prev):
            editions[key][trad] = rec
        if key not in meta:
            meta[key] = new_meta(p, season)
        else:
            fill_meta(meta[key], p, season, week_letter=key[1])

    # Sundays, feasts, and commemorations with no (or only one) Mysteries office.
    by_key_trad: dict[tuple, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for p in prayers:
        season = seasons.get(p["seasonId"], {})
        if not is_listed_day(p, season):
            continue
        trad = tradition_of(p)
        if not trad:
            continue
        by_key_trad[occasion_key(p, season)][trad].append(p)

    myst_by_key_trad: dict[tuple, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for p in myst:
        trad = tradition_of(p)
        if not trad:
            continue
        season = seasons.get(p["seasonId"], {})
        myst_by_key_trad[occasion_key(p, season)][trad].append(p)

    for key, trads in by_key_trad.items():
        season = seasons.get(key[0], {})
        for trad, plist in trads.items():
            best = min(plist, key=office_rank)
            if key not in meta:
                meta[key] = new_meta(best, season)
            for p in plist:
                fill_meta(meta[key], p, season, week_letter=key[1])
            if trad not in editions[key]:
                myst_list = myst_by_key_trad[key].get(trad) or []
                if myst_list:
                    chosen = min(myst_list, key=office_rank)
                    editions[key][trad] = make_edition(chosen, hymns_from(chosen))
                else:
                    # No Qurbana for this day — do not attach Ramsha/Night as the office.
                    editions[key][trad] = make_placeholder(best)

    occasions = []
    for key, eds in editions.items():
        m = meta[key]
        season = seasons.get(m["seasonId"], {})
        name = (eds.get("syriac") or eds.get("chaldean") or {}).get("name") or ""
        occasions.append(
            {
                **m,
                "name": name,
                "seasonSyriac": season.get("syriac") or "",
                "seasonEnglish": season.get("english") or "",
                "seasonGroup": season.get("group") or "other",
                "seasonOrder": season.get("order") if season.get("order") is not None else 999,
                "syriac": eds.get("syriac"),
                "chaldean": eds.get("chaldean"),
            }
        )

    attach_feast_hymns_to_cycle_fridays(occasions)

    occasions.sort(
        key=lambda o: (
            o["seasonOrder"],
            o["week"],
            o["dayOrder"],
            o["name"],
        )
    )

    used_seasons = []
    seen = set()
    for o in occasions:
        sid = o["seasonId"]
        if sid in seen:
            continue
        seen.add(sid)
        s = seasons.get(sid)
        if s:
            used_seasons.append(
                {
                    "id": s["id"],
                    "syriac": s["syriac"],
                    "english": s["english"],
                    "group": s["group"],
                    "order": s["order"],
                }
            )

    n_q = sum(
        1
        for o in occasions
        for t in ("syriac", "chaldean")
        if o.get(t) and o[t].get("qanka")
    )
    n_r = sum(
        1
        for o in occasions
        for t in ("syriac", "chaldean")
        if o.get(t) and o[t].get("raza")
    )
    n_pair = sum(1 for o in occasions if o.get("syriac") and o.get("chaldean"))

    payload = {
        "counts": {
            "occasions": len(occasions),
            "paired": n_pair,
            "qanka": n_q,
            "raza": n_r,
        },
        "seasons": used_seasons,
        "occasions": occasions,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"Wrote {OUT} — occasions={len(occasions)} paired={n_pair} "
        f"qanka={n_q} raza={n_r}"
    )


if __name__ == "__main__":
    main()
