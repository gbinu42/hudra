#!/usr/bin/env python3
"""
Normalize mis-encoded Syriac consonant dots in the prayer/psalm corpus.

East Syriac Madnhaya — common corpus confusions:
  1. U+073C HBASA-ESASA DOTTED on BGDKPT → U+0742 RUKKAKHA
     (on other letters U+073C is the legitimate /i/ vowel — keep)
  2. U+073F RWAHA on BGDKPT → U+0741 QUSHSHAYA
     (on other letters U+073F is the legitimate /o/ vowel — keep)

Generic combining dots → Syriac marks when the base letter fits:
  3. U+0323 COMBINING DOT BELOW on BGDKPT → U+0742 RUKKAKHA
  4. U+0307 COMBINING DOT ABOVE on BGDKPT → U+0741 QUSHSHAYA
  5. U+0324 COMBINING DIAERESIS BELOW on ܬ → U+0740 FEMININE DOT

Soft pe (East Syriac convention):
  6. U+0742 on ܦ → U+032E COMBINING BREVE BELOW

Dotless dalath-rish misused as resh:
  7. U+0716 ܖ → U+072A ܪ. Plural resh is ܪ with syame.
     Mark order: consonant mods, then syame, then vowels
     (letter-syame-vowel, e.g. ܪ̈ܲ). Merge ܖܪ / ܪܖ clusters
     so only one base remains.

Chaldean "min" (from) particle (applied only to Chaldean texts):
  8. Bare particle ܡܢ / wrong ܡ݂ܢ → ܡ̣ܢ (U+0323 COMBINING DOT BELOW)
     Proclitics ܘ / ܕ kept: ܘܡ̣ܢ, ܕܡ̣ܢ.
     Do NOT touch already-pointed ܡܲܢ / ܡ̇ܢ / ܡܵܢ / ܡܸܢ / ܡܼܢ.
     Interrogative/relative "who" with ܠ or ܒ: ܠܡܢ → ܠܡܲܢ, ܒܡܢ → ܒܡܲܢ.

Never delete diacritics: if no remapping rule applies, the mark is kept.
When soft + hard end up on the same letter, keep soft and drop qushshaya.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

BGDKPT = set("ܒܓܕܟܦܬ")
TAW = "ܬ"
PE = "ܦ"
DOTLESS_RISH = "\u0716"  # ܖ — should be ܪ in this corpus
RISH = "\u072a"  # ܪ

HBASA = "\u073c"  # vowel /i/ — misused as rukkakha on BGDKPT
RWAHA = "\u073f"  # vowel /o/ — misused as qushshaya on BGDKPT
RUKKAKHA = "\u0742"
QUSHSHAYA = "\u0741"
FEMININE = "\u0740"
DOT_BELOW = "\u0323"
DOT_ABOVE = "\u0307"
DIAERESIS_BELOW = "\u0324"
BREVE_BELOW = "\u032e"
SYAME = "\u0308"
PTAHA = "\u0732"  # /a/ — used on ܡܲܢ "who"

# Syriac letter; used as a lookaround boundary for the mn particle.
_SYR_LETTER = r"\u0710-\u072F"
# Wrong soft marks sometimes placed on mim for "min".
_MN_SOFT = f"[{RUKKAKHA}{BREVE_BELOW}]"

# Consonant modifiers (excluding syame) that should precede vowel points.
CONSONANT_MODS = {RUKKAKHA, QUSHSHAYA, FEMININE, BREVE_BELOW}
VOWELS = {chr(c) for c in range(0x0730, 0x0740)}


def _remap_mark(base: str, mark: str) -> str:
    """Map a single combining mark; never drop — return mark unchanged if no rule."""
    if mark == HBASA and base in BGDKPT:
        return RUKKAKHA
    if mark == RWAHA and base in BGDKPT:
        return QUSHSHAYA
    if mark == DOT_BELOW and base in BGDKPT:
        return RUKKAKHA
    if mark == DOT_ABOVE and base in BGDKPT:
        return QUSHSHAYA
    if mark == DIAERESIS_BELOW and base == TAW:
        return FEMININE
    return mark


def _order_marks(marks: list[str]) -> list[str]:
    """Soft/hard mods, then syame, then other, then vowels (letter-syame-vowel)."""
    mods = [m for m in marks if m in CONSONANT_MODS]
    syame = [m for m in marks if m == SYAME]
    other = [
        m
        for m in marks
        if m not in CONSONANT_MODS and m not in VOWELS and m != SYAME
    ]
    vowels = [m for m in marks if m in VOWELS]
    return mods + syame + other + vowels


def fix_dots(text: str) -> str:
    if not text:
        return text

    result: list[str] = []
    pending_marks: list[str] = []  # from a dropped ܖ merging into the next ܪ
    i = 0
    n = len(text)
    while i < n:
        char = text[i]

        if not unicodedata.category(char).startswith("M"):
            base = char
            marks: list[str] = []
            i += 1
            while i < n and unicodedata.category(text[i]).startswith("M"):
                marks.append(text[i])
                i += 1

            # ܖ → ܪ; merge into a neighbouring ܪ when present (avoid ܪܪ̈)
            if base == DOTLESS_RISH:
                if i < n and text[i] in (RISH, DOTLESS_RISH):
                    pending_marks.extend(marks)
                    continue
                # Previous emitted base is already rish — fold marks in
                j = len(result) - 1
                while j >= 0 and unicodedata.category(result[j]).startswith("M"):
                    j -= 1
                if j >= 0 and result[j] == RISH:
                    existing = result[j + 1 :]
                    del result[j + 1 :]
                    combined = list(existing) + _order_marks(
                        _finalize_marks(RISH, marks)
                    )
                    seen: set[str] = set()
                    deduped: list[str] = []
                    for m in combined:
                        if m not in seen:
                            deduped.append(m)
                            seen.add(m)
                    result.extend(_order_marks(deduped))
                    continue
                base = RISH

            if base == RISH and pending_marks:
                marks = pending_marks + marks
                pending_marks = []
            elif pending_marks:
                result.append(RISH)
                result.extend(
                    _order_marks(_finalize_marks(RISH, pending_marks))
                )
                pending_marks = []

            result.append(base)
            result.extend(_order_marks(_finalize_marks(base, marks)))
        else:
            # Orphan combining mark (no base in stream) — keep as-is.
            result.append(char)
            i += 1

    if pending_marks:
        result.append(RISH)
        result.extend(_order_marks(_finalize_marks(RISH, pending_marks)))

    out = "".join(result)
    # Plural "our bodies": ܦܲܓ݂ܪ̈ܲܝܢ (syame then vowel).
    out = out.replace("ܦܲܓ݂ܪܪ̈", "ܦܲܓ݂ܪ̈")
    out = out.replace("ܦܲܓ݂ܪܲ̈", "ܦܲܓ݂ܪ̈ܲ")
    out = out.replace("ܦܲܓ݂ܪܲܝܢ", "ܦܲܓ݂ܪ̈ܲܝܢ")
    return out


def _finalize_marks(base: str, marks: list[str]) -> list[str]:
    new_marks = [_remap_mark(base, m) for m in marks]

    if base == PE:
        new_marks = [BREVE_BELOW if m == RUKKAKHA else m for m in new_marks]

    has_soft = RUKKAKHA in new_marks or BREVE_BELOW in new_marks
    if has_soft:
        new_marks = [m for m in new_marks if m != QUSHSHAYA]

    seen: set[str] = set()
    unique: list[str] = []
    for m in new_marks:
        if m not in seen:
            unique.append(m)
            seen.add(m)
    return unique


# ܠܡܢ / ܒܡܢ (± prior ܘ/ܕ) → who with ptāḥā; bare/ܘ/ܕ ܡܢ → Chaldean ܡ̣ܢ.
_WHO_MN_RE = re.compile(
    rf"(?<![{_SYR_LETTER}])([ܘܕ]?[ܠܒ])ܡ{_MN_SOFT}?ܢ(?![{_SYR_LETTER}])"
)
_FROM_MN_RE = re.compile(
    rf"(?<![{_SYR_LETTER}])([ܘܕ]?)ܡ(?:{_MN_SOFT})?ܢ(?![{_SYR_LETTER}])"
)


def fix_chaldean_min(text: str) -> str:
    """Point the Chaldean 'min' (from) particle; keep 'man' (who) distinct."""
    if not text or "ܡ" not in text:
        return text

    def who_sub(m: re.Match[str]) -> str:
        return m.group(1) + "ܡ" + PTAHA + "ܢ"

    def from_sub(m: re.Match[str]) -> str:
        return m.group(1) + "ܡ" + DOT_BELOW + "ܢ"

    # Who first so ܠܡܢ / ܒܡܢ are not turned into underdot "from".
    text = _WHO_MN_RE.sub(who_sub, text)
    text = _FROM_MN_RE.sub(from_sub, text)
    return text


def process_file(path: Path, *, chaldean_min: bool = False) -> int:
    content = path.read_text(encoding="utf-8")
    new_content = fix_dots(content)
    if chaldean_min:
        new_content = fix_chaldean_min(new_content)
    if new_content != content:
        path.write_text(new_content, encoding="utf-8")
        return 1
    return 0


def process_json_file(path: Path, *, chaldean_min: bool = False) -> int:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return 0

    # Auto-detect Chaldean tradition on prayer records when not forced.
    trad = data.get("tradition") or []
    if isinstance(trad, str):
        trad = [trad]
    apply_min = chaldean_min or ("chaldean" in trad)

    changed = False
    for key in ("text", "html", "itemDesc", "itemName", "prayerTime", "itemRelatedHoliday"):
        if key in data and isinstance(data[key], str):
            new_val = fix_dots(data[key])
            if apply_min:
                new_val = fix_chaldean_min(new_val)
            if new_val != data[key]:
                data[key] = new_val
                changed = True

    if changed:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return 1
    return 0


def process_index(path: Path, *, chaldean_min: bool = False) -> bool:
    if not path.exists():
        return False
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = False

    def walk(node):
        nonlocal changed
        if isinstance(node, dict):
            # Prayer entries in index carry tradition; only then apply min.
            trad = node.get("tradition") or []
            if isinstance(trad, str):
                trad = [trad]
            apply_min = chaldean_min or ("chaldean" in trad)
            for k, v in node.items():
                if isinstance(v, str):
                    new_v = fix_dots(v)
                    if apply_min:
                        new_v = fix_chaldean_min(new_v)
                    if new_v != v:
                        node[k] = new_v
                        changed = True
                else:
                    walk(v)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                if isinstance(v, str):
                    new_v = fix_dots(v)
                    # Bare strings in lists: dots only (no tradition context).
                    if new_v != v:
                        node[i] = new_v
                        changed = True
                else:
                    walk(v)

    walk(data)
    if changed:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return changed


if __name__ == "__main__":
    ROOT = Path(__file__).resolve().parents[1]

    # Self-check examples from the corpus report
    assert fix_dots("ܘܣܲܒܼܪܵܐ") == "ܘܣܲܒ݂ܪܵܐ"
    assert fix_dots("ܬܿ") == "ܬ݁"
    assert fix_dots("ܟܼ") == "ܟ݂"
    assert fix_dots("ܚܘܼܕܪܵܐ") == "ܚܘܼܕܪܵܐ"  # hbasa on waw stays
    assert fix_dots("ܡܲܙܡܘܿܪܵܐ") == "ܡܲܙܡܘܿܪܵܐ"  # rwaha on waw stays
    assert fix_dots("ܕܦܲܓ݂ܪ̈ܲܝܢ") == "ܕܦܲܓ݂ܪ̈ܲܝܢ"
    assert fix_dots("ܦܲܓ݂ܖܪ̈ܲܝܗܘܿܢ") == "ܦܲܓ݂ܪ̈ܲܝܗܘܿܢ"
    assert fix_dots("ܐܘܖܼܪܚܵܐ") == "ܐܘܪܼܚܵܐ"
    assert fix_dots("ܖ̈ܲ") == "ܪ̈ܲ"
    assert fix_dots("ܪܲ̈") == "ܪ̈ܲ"
    assert fix_chaldean_min("ܡܢ ܒܝܼܫܵܐ") == "ܡ̣ܢ ܒܝܼܫܵܐ"
    assert fix_chaldean_min("ܘܡܢ ܥܵܠܲܡ") == "ܘܡ̣ܢ ܥܵܠܲܡ"
    assert fix_chaldean_min("ܕܡܢ ܩܕ݂ܝܼܡ") == "ܕܡ̣ܢ ܩܕ݂ܝܼܡ"
    assert fix_chaldean_min("ܡ݂ܢ ܫܡܲܝܵܐ") == "ܡ̣ܢ ܫܡܲܝܵܐ"
    assert fix_chaldean_min("ܠܡܢ ܣܵܓ݂ܕܝܼܬ݁ܘܿܢ") == "ܠܡܲܢ ܣܵܓ݂ܕܝܼܬ݁ܘܿܢ"
    assert fix_chaldean_min("ܒܡܢ ܚܲܟ݁ܝܼܡ") == "ܒܡܲܢ ܚܲܟ݁ܝܼܡ"
    assert fix_chaldean_min("ܡܲܢ ܕܨܵܒܹܐ") == "ܡܲܢ ܕܨܵܒܹܐ"  # already who
    assert fix_chaldean_min("ܡ̇ܢ ܕ") == "ܡ̇ܢ ܕ"
    assert fix_chaldean_min("ܡܸܢ ܒܝܼܫܵܐ") == "ܡܸܢ ܒܝܼܫܵܐ"  # Assyrian pointing kept

    # Map short txt-hash → whether Chaldean (from prayer JSON).
    chaldean_ids: set[str] = set()
    prayers_dir = ROOT / "data" / "prayers"
    if prayers_dir.exists():
        for p in prayers_dir.glob("*.json"):
            try:
                trad = json.loads(p.read_text(encoding="utf-8")).get("tradition") or []
            except Exception:
                continue
            if isinstance(trad, str):
                trad = [trad]
            if "chaldean" in trad:
                chaldean_ids.add(p.stem)
                chaldean_ids.add(p.stem[:8])

    changed_json = 0
    for d in ("data/prayers", "data/psalms"):
        d_path = ROOT / d
        if d_path.exists():
            for p in d_path.glob("*.json"):
                changed_json += process_json_file(p)

    changed_txt = 0
    for d in ("prayers", "psalms"):
        d_path = ROOT / d
        if d_path.exists():
            for p in d_path.rglob("*.txt"):
                # Filenames end with __<8-char-hash>.txt for prayers.
                stem = p.stem
                hash8 = stem.rsplit("__", 1)[-1] if "__" in stem else ""
                is_chal = hash8 in chaldean_ids or stem in chaldean_ids
                changed_txt += process_file(p, chaldean_min=is_chal)

    for name in ("index.json", "psalms_index.json", "catalog.json"):
        process_index(ROOT / "data" / name)

    print(
        f"Fixed diacritics in {changed_json} JSON files "
        f"and {changed_txt} text files."
    )
