#!/usr/bin/env python3
"""
Repair stray, doubled and stand-in diacritics in the prayer/psalm corpus.

  1. Stand-ins for linea occultans (U+0747): U+0749 SYRIAC MUSIC and
     U+064E ARABIC FATHA (ܐܲܢ݉ܬ → ܐܲܢ݇ܬ, ܫܲܢَܬܵܐ → ܫܲܢ݇ܬܵܐ). A dot below
     typed after the line is put first (ܗَ̣ → ܗ̣݇), as in the clean copies.
  2. Stand-ins for rukkakha: U+064D ARABIC KASRATAN and U+0330 TILDE BELOW
     on ܟ (ܬܸܫ̈ܒܚܵܬ̣ܵܟٍ → ܬܸܫ̈ܒܚܵܬ̣ܵܟ݂). On ܦ the tilde is dropped
     (ܘܦ̰ܲܨܝܼ → ܘܦܲܨܝܼ, as in the other copies).
  3. U+0731 PTHAHA BELOW is not East Syriac. On a letter that already has a
     vowel it is dropped (ܗܵܕܹܱܐ → ܗܵܕܹܐ); otherwise it becomes pthaha
     (ܢܨܱܠܹܐ → ܢܨܲܠܹܐ).
  4. Zero-width non-joiners and BOMs inside words are removed; they cut a
     word apart when rendered (ܨ‌ܠܘܿܬ݂ܵܟ݂).
  5. A mark separated from its letter. The extractor split prayers at colour
     changes, so a dot that followed a red word landed after a paragraph
     break or inside the next <span> (ܢܡܸܢܵܟ</span>݂܀). Such marks move back
     onto the letter they followed. A mark standing alone between spaces
     or after punctuation is dropped, since it only renders as a dotted
     circle (ܥܠܲܝ ̣, ܕܟ̣ܠ.̈). Marks after a tatweel stay; the source stretches
     words that way on purpose.
  6. The same mark typed twice on one letter is collapsed
     (ܒܲܲܝܢܵܬܲܢ → ܒܲܝܢܵܬܲܢ, ܓܲܪ̈̈ܡܲܝ → ܓܲܪ̈ܡܲܝ).
  7. One-off typos checked against clean copies of the same passage or the
     sense of the line (WORD_FIXES; ܐܲܪܒܲܥܫܲܒܵܐ had lost its alaph).
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MARKS = "̀-ͯܰ-ً݊-ٟ"
LETTERS = "ܐ-ܯݍ-ݏ"
TATWEEL = "ـ"
VOWELS = set("ܱܴܷܸܹܻܼܾܰܲܳܵܶܺܽܿ")

LINEA = "݇"
RUKKAKHA = "݂"
DOT_BELOW = "̣"
PTHAHA = "ܲ"
PTHAHA_BELOW = "ܱ"

WORD_FIXES = {
    "ܘܲܙܟ݂ ܵܘ": "ܘܲܙܟ݂ܵܘ",
    "ܘܲܙܟ݂ ܵܐ": "ܘܲܙܟ݂ܵܐ",
    "ܡܝܼܟ݂ ܵܐ": "ܡܝܼܟ݂ܵܐ",
    "ܬܲܠܓܵܐ ܸܚܘܲܪ": "ܬܲܠܓܵܐ ܚܸܘܲܪ",
    "ܘܲܒ݂ܪܱܵ": "ܘܲܒ݂ܪܵܐ",
    "ܡܸܬܷ݁ܲܪܟܵܐ": "ܡܸܬ݁ܕܲܪܟܵܐ",
    "ܨܹܷܝܕ݂": "ܨܹܝܕ݂",
    "ܢܲܣܠܹܘhy": "ܢܲܣܠܹܝܘܗܝ",
    "ܕܲܢܩܲܒ݁ܠܘܼܢ ܸܘܼܫܡܵܐ": "ܕܲܢܩܲܒ݁ܠܘܼܢ ܪܘܼܫܡܵܐ",
    "ܐܲܠܨܸ݁ܬ̣ ܲܒ݂ܥܸܠܕܒ݂ܵܒܲܝ": "ܐܲܠܨܸ݁ܬ̣ ܠܲܒ݂ܥܸܠܕܒ݂ܵܒܲܝ",
}
MISSING_ALAPH = re.compile(f"(?<![{LETTERS}{MARKS}])ܲ?ܪܒܲܥܫܲܒܵܐ ܕܸܫܬܵܐ")

LINEA_STANDIN = re.compile("[َ݉]")
LINEA_THEN_DOT = re.compile(LINEA + DOT_BELOW)
KAPH_RUKKAKHA_STANDIN = re.compile("ܟ([ٍ̰])")
PE_TILDE = re.compile("ܦ̰")
CLUSTER = re.compile(f"([{LETTERS}])([{MARKS}]+)")
INVISIBLE = re.compile("[‌﻿]")
SEP = "(?:<[^>]+>|&nbsp;|\\s)+"
SEPARATED = re.compile(
    f"([{LETTERS}{TATWEEL}][{MARKS}]*)?((?:{SEP}[{MARKS}]+)+)(?=(.?))",
    re.S,
)
SEP_MARKS = re.compile(f"({SEP})([{MARKS}]+)", re.S)
AFTER_PUNCT = re.compile(f"(?<=[^{LETTERS}{MARKS}{TATWEEL}\\s>;])[{MARKS}]+")
DOUBLED = re.compile(f"([{MARKS}])\\1+")


def _pthaha_below(m: re.Match) -> str:
    letter, marks = m.group(1), m.group(2)
    if PTHAHA_BELOW not in marks:
        return m.group(0)
    if any(c in VOWELS and c != PTHAHA_BELOW for c in marks):
        return letter + marks.replace(PTHAHA_BELOW, "")
    return letter + marks.replace(PTHAHA_BELOW, PTHAHA)


def _separated(m: re.Match) -> str:
    base, run, after = m.group(1), m.group(2), m.group(3)
    pieces = SEP_MARKS.findall(run)
    sep = "".join(s for s, _ in pieces)
    marks = "".join(k for _, k in pieces)
    span_break = "\n" in sep or "<" in sep or "&nbsp;" in sep
    if base and span_break:
        return base + marks + sep
    if base and re.match(f"[{LETTERS}]", after):
        return m.group(0)  # a mark typed before the next word's letter; left for review
    return (base or "") + sep


def fix_marks(text: str) -> str:
    for bad, good in WORD_FIXES.items():
        text = text.replace(bad, good)
    text = MISSING_ALAPH.sub("ܐܲܪܒܲܥܫܲܒܵܐ ܕܸܫܬܵܐ", text)
    text = LINEA_STANDIN.sub(LINEA, text)
    text = LINEA_THEN_DOT.sub(DOT_BELOW + LINEA, text)
    text = KAPH_RUKKAKHA_STANDIN.sub("ܟ" + RUKKAKHA, text)
    text = PE_TILDE.sub("ܦ", text)
    text = CLUSTER.sub(_pthaha_below, text)
    text = INVISIBLE.sub("", text)
    text = SEPARATED.sub(_separated, text)
    text = AFTER_PUNCT.sub("", text)
    text = DOUBLED.sub(r"\1", text)
    return text


def _self_check() -> None:
    cases = {
        "ܕܐܲܢ݉ܬܘܼ": "ܕܐܲܢ݇ܬܘܼ",
        "ܫܲܢَܬܵܐ": "ܫܲܢ݇ܬܵܐ",
        "ܗَ̣ܘܵܐ": "ܗ̣݇ܘܵܐ",
        "ܬܸܫ̈ܒܚܵܬ̣ܵܟٍ*": "ܬܸܫ̈ܒܚܵܬ̣ܵܟ݂*",
        "ܡܸܠܬ̣ܵܟ̰.": "ܡܸܠܬ̣ܵܟ݂.",
        "ܘܦ̰ܲܨܝܼ": "ܘܦܲܨܝܼ",
        "ܢܨܱܠܹܐ": "ܢܨܲܠܹܐ",
        "ܕܲܢܨܱܲܚܘ": "ܕܲܢܨܲܚܘ",
        "ܗܵܕܹܱܐ": "ܗܵܕܹܐ",
        "ܨ‌ܠܘܿܬ݂ܵܟ݂": "ܨܠܘܿܬ݂ܵܟ݂",
        "ܢܡܸܢܵܟ\n\n ݂܀ ܥܲܠ": "ܢܡܸܢܵܟ݂\n\n ܀ ܥܲܠ",
        'ܢܡܸܢܵܟ</span>݂܀': 'ܢܡܸܢܵܟ݂</span>܀',
        'ܝܲܡܝܼܢܵܟ<span style="color:#ee0000">݂.*': 'ܝܲܡܝܼܢܵܟ݂<span style="color:#ee0000">.*',
        "ܡܵܪܲܢ ܚܘܼܣ ܥܠܲܝ ̣\n\nܥܵܠܲܡ": "ܡܵܪܲܢ ܚܘܼܣ ܥܠܲܝ \n\nܥܵܠܲܡ",
        "ܡܵܪܵܐ ܕܟ̣ܠ.̈\n\nܘܥܵܢ": "ܡܵܪܵܐ ܕܟ̣ܠ.\n\nܘܥܵܢ",
        "ܕܟ̣ܠ.\n\n̈\n\nܘܥܵܢ": "ܕܟ̣ܠ.\n\n\n\nܘܥܵܢ",
        "ܒܲܨܠܵـ̈ـܘܵܬ݂ܗ": "ܒܲܨܠܵـ̈ـܘܵܬ݂ܗ",
        "ܬܢܝܼ̣\n\n ̣\n\nܫܲܒܲܚ": "ܬܢܝܼ̣\n\n \n\nܫܲܒܲܚ",
        "ܕܲܨܠܘܿܬ\n\n݂\n\nܵܐ": "ܕܲܨܠܘܿܬ݂ܵ\n\n\n\nܐ",
        "ܒܲܲܝܢܵܬܲܢ": "ܒܲܝܢܵܬܲܢ",
        "ܓܲܪ̈̈ܡܲܝ": "ܓܲܪ̈ܡܲܝ",
        "ܕܲܢܨܱܲܚܘ ܘܲܙܟ݂ ܵܘ:": "ܕܲܢܨܲܚܘ ܘܲܙܟ݂ܵܘ:",
        "ܡܸܬܷ݁ܲܪܟܵܐ.": "ܡܸܬ݁ܕܲܪܟܵܐ.",
        "ܲܪܒܲܥܫܲܒܵܐ ܕܸܫܬܵܐ": "ܐܲܪܒܲܥܫܲܒܵܐ ܕܸܫܬܵܐ",
        '">ܪܒܲܥܫܲܒܵܐ ܕܸܫܬܵܐ': '">ܐܲܪܒܲܥܫܲܒܵܐ ܕܸܫܬܵܐ',
        "ܐܲܪܒܲܥܫܲܒܵܐ ܕܸܫܬܵܐ": "ܐܲܪܒܲܥܫܲܒܵܐ ܕܸܫܬܵܐ",
    }
    for src, want in cases.items():
        got = fix_marks(src)
        assert got == want, f"{src!r}: got {got!r}, want {want!r}"


def _walk(value):
    if isinstance(value, str):
        return fix_marks(value)
    if isinstance(value, list):
        return [_walk(v) for v in value]
    if isinstance(value, dict):
        return {k: _walk(v) for k, v in value.items()}
    return value


def _json_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for rel in ("data/prayers", "data/psalms", "web/data"):
        d = root / rel
        if d.is_dir():
            files.extend(d.glob("*.json"))
    for name in ("index.json", "psalms_index.json", "catalog.json"):
        files.append(root / "data" / name)
    return [p for p in files if p.is_file()]


def _dump_like(data, raw: str) -> str:
    for indent in (2, None):
        out = json.dumps(data, ensure_ascii=False, indent=indent)
        if json.dumps(json.loads(raw), ensure_ascii=False, indent=indent) == raw.rstrip("\n"):
            return out + ("\n" if raw.endswith("\n") else "")
    raise ValueError("unrecognised JSON layout")


def _apply(root: Path) -> None:
    changed = 0
    for path in _json_files(root):
        raw = path.read_text(encoding="utf-8")
        new = _dump_like(_walk(json.loads(raw)), raw)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            changed += 1
    for rel in ("prayers", "psalms"):
        for path in (root / rel).rglob("*.txt"):
            raw = path.read_text(encoding="utf-8")
            new = fix_marks(raw)
            if new != raw:
                path.write_text(new, encoding="utf-8")
                changed += 1
    print(f"Repaired diacritics in {changed} files.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Repair stray and stand-in Syriac marks. Runs the rule self-check "
            "by default; rewriting the corpus requires --apply."
        )
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="rewrite the prayer/psalm corpus in place",
    )
    args = parser.parse_args()

    _self_check()
    if not args.apply:
        print("Self-check passed. Re-run with --apply to rewrite the corpus.")
        raise SystemExit(0)
    _apply(Path(__file__).resolve().parents[1])
