#!/usr/bin/env python3
"""
Restore letters that a legacy Syriac font stored as ligature glyphs.

Some prayers were typed in a font whose ligatures sat on rarely used Syriac
code points. Rendered with a Unicode font they show the wrong letters
(ܨܠܘܿܞ̣ܵ for ܨܠܘܿܬ݂ܵܐ, ܡܫܲܒܲܚܧܵ for ܡܫܲܒܲܚܬܵܐ). Every rule below was checked
against clean copies of the same prayers elsewhere in the corpus.

  1. U+071E ܞ (isolated) and U+0727 ܧ (final) are the taw–alaph ligature.
     The marks typed after the glyph belong to the taw, so
     ܞ̣ܵ → ܬ݂ܵܐ and ܧܵ → ܬܵܐ. A dot below on the taw is rukkakha (U+0742).
     When the next word was run on (ܘܐܵܘܝܘܼܞ̣ܵܘܩܘܼܝܵܡܵܐ) a space is restored.
  1b. Standing alone, ܞܵ is the yodh–he ligature of the divine name:
     ܞܵ ܡܵܪܝܵܐ → ܝܲܗ ܡܵܪܝܵܐ (Exod 15:2, as in the clean copy c63a47a0).
  2. U+071C ܜ word-final is the he–yodh ligature (ܐܝܼܬ݂ܵܘܜ → ܐܝܼܬ݂ܵܘܗܝ);
     elsewhere in a word it stands for teth (ܜܲܠܵܐ → ܛܲܠܵܐ).
  3. U+0724 ܤ final semkath typed inside a word → ܣ (ܠܝܵܘܤܸܦ → ܠܝܵܘܣܸܦ).
  4. U+0714 ܔ after ܗܝ is a stray glyph (ܥܲܒ݂ܕܵܘ̈ܗܝܔ → ܥܲܒ݂ܕܵܘ̈ܗܝ).
     In book abbreviations (ܡܠܟ̈ܔ:) it is the abbreviation tail and is kept.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

MARKS = "\u0300-\u036f\u0730-\u074a"
LETTERS = "\u0710-\u072f\u074d-\u074f"
DOT_BELOW = "\u0323"
RUKKAKHA = "\u0742"

TAW_ALAPH = re.compile(f"[\u071e\u0727]([{MARKS}]*)([{LETTERS}])?")
YAH = re.compile(f"(?<![{LETTERS}{MARKS}])\u071e\u0735(?![{LETTERS}{MARKS}])")
HE_YODH = re.compile(f"\u071c([{MARKS}]*)(?![{LETTERS}{MARKS}])")
TETH_GARSHUNI = "\u071c"
FINAL_SEMKATH = "\u0724"
STRAY_GAMAL = re.compile(f"(\u0717[{MARKS}]*\u071d[{MARKS}]*)\u0714([{MARKS}]*)")

CORRUPT = "\u071e\u0727\u071c\u0724"


def _taw_alaph(m: re.Match) -> str:
    marks = m.group(1).replace(DOT_BELOW, RUKKAKHA)
    after = m.group(2)
    return "\u072c" + marks + "\u0710" + (" " + after if after else "")


def _stray_gamal(m: re.Match) -> str:
    head, marks = m.group(1), m.group(2)
    if marks == DOT_BELOW and head == "\u0717\u0747\u071d":
        return "\u0717\u0323\u0747\u071d"  # ܗ݇ܝܔ̣ → ܗ̣݇ܝ, as in the clean copies
    return head + marks


def fix_ligatures(text: str) -> str:
    text = YAH.sub("\u071d\u0732\u0717", text)
    text = TAW_ALAPH.sub(_taw_alaph, text)
    text = HE_YODH.sub(lambda m: "\u0717\u071d" + m.group(1), text)
    text = text.replace(TETH_GARSHUNI, "\u071b")
    text = text.replace(FINAL_SEMKATH, "\u0723")
    text = STRAY_GAMAL.sub(_stray_gamal, text)
    return text


def _self_check() -> None:
    cases = {
        "ܨܠܘܿܞ̣ܵ.": "ܨܠܘܿܬ݂ܵܐ.",
        "ܡܫܲܒܲܚܧܵ:": "ܡܫܲܒܲܚܬܵܐ:",
        "ܠܲܡܚܝܼܠܘܼܞ̣ܵ ܕܣܵܓ݂ܘܿܕܲܝ̈ܟ": "ܠܲܡܚܝܼܠܘܼܬ݂ܵܐ ܕܣܵܓ݂ܘܿܕܲܝ̈ܟ",
        "ܥܹܕܞܵ": "ܥܹܕܬܵܐ",
        "ܬܸܫܡܸܫܧ ܕܠܸܠܝܵܐ": "ܬܸܫܡܸܫܬܐ ܕܠܸܠܝܵܐ",
        "ܘܐܵܘܝܘܼܞ̣ܵܘܩܘܼܝܵܡܵܐ": "ܘܐܵܘܝܘܼܬ݂ܵܐ ܘܩܘܼܝܵܡܵܐ",
        " ܞܵ ܡܵܪܝܵܐ": " ܝܲܗ ܡܵܪܝܵܐ",
        "ܕܐܝܼܬ݂ܵܘܜ ܡ̣ܢ": "ܕܐܝܼܬ݂ܵܘܗܝ ܡ̣ܢ",
        "ܕܣܵܓ݂ܘܿܕ݂ܵܘ̈ܜ:": "ܕܣܵܓ݂ܘܿܕ݂ܵܘ̈ܗܝ:",
        "ܜܲܠܵܐ ܕܪ̈ܲܚܡܲܝܟ": "ܛܲܠܵܐ ܕܪ̈ܲܚܡܲܝܟ",
        "ܠܝܵܘܤܸܦ": "ܠܝܵܘܣܸܦ",
        "ܥܲܒ݂ܕܵܘ̈ܗܝܔ ܘܗܘ̤": "ܥܲܒ݂ܕܵܘ̈ܗܝ ܘܗܘ̤",
        "ܫܦܝܼܥܵܐ ܗ݇ܝܔ̣ ܛܲܝܒ݁ܘܼܬ݂ܵܟ̣": "ܫܦܝܼܥܵܐ ܗ̣݇ܝ ܛܲܝܒ݁ܘܼܬ݂ܵܟ̣",
        "ܒ: ܡܠܟ̈ܔ: ܒ: 1": "ܒ: ܡܠܟ̈ܔ: ܒ: 1",
    }
    for src, want in cases.items():
        got = fix_ligatures(src)
        assert got == want, f"{src!r}: got {got!r}, want {want!r}"


def _corpus_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for rel in ("data/prayers", "data/psalms", "web/data"):
        d = root / rel
        if d.is_dir():
            files.extend(d.glob("*.json"))
    for name in ("index.json", "psalms_index.json", "catalog.json"):
        files.append(root / "data" / name)
    for rel in ("prayers", "psalms"):
        d = root / rel
        if d.is_dir():
            files.extend(d.rglob("*.txt"))
    return files


def _apply(root: Path) -> None:
    changed = 0
    for path in _corpus_files(root):
        if not path.is_file():
            continue
        raw = path.read_text(encoding="utf-8")
        new = fix_ligatures(raw)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            changed += 1
    left = sum(
        sum(p.read_text(encoding="utf-8").count(c) for c in CORRUPT)
        for p in _corpus_files(root)
        if p.is_file()
    )
    print(f"Restored ligature letters in {changed} files; {left} ligature code points left.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Restore letters stored as legacy ligature glyphs. Runs the rule "
            "self-check by default; rewriting the corpus requires --apply."
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
