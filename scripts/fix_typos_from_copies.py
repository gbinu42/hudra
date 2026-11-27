#!/usr/bin/env python3
"""
Fix misspelled words by comparing repeated passages.

Most prayers occur many times in the corpus. A clause found once or twice
that differs from a clause found three or more times in a single word, by
one or two letters, is a typo candidate (ܠܥܡܝܢ for ܠܥܠܡܝܢ, ܡܨܚܡܢܐ for
ܡܪܚܡܢܐ). TYPOS lists the candidates that were reviewed and accepted by
consonants: the wrong spelling occurs nowhere else in the corpus and the
right one is the common word. Candidates that may be a genuine reading were
left out: a different proclitic (ܘ/ܕ/ܠ/ܒ), a different suffix person or
number, or a wrong form that is itself a real word (ܕܒܚܗ, ܢܬܛܒܥ, ܬܪܚܦ).

The pointed form of the replacement is taken from the matching copies, so
the fix brings the vowels of the clean text with it.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path

TYPOS = {
    "ܐܚܕܕ": "ܐܚܕ", "ܐܢܘ": "ܐܢܘܢ", "ܐܪܡܡ": "ܐܪܝܡ", 
    "ܐܬܓܠܚ": None, "ܐܬܠܟܠ": "ܐܬܢܟܠ", "ܐܬܥܛܝܒ": None, "ܐܬܬܥܝܪܪܝ": "ܐܬܬܥܝܪܝ",
    "ܒܐܪܒܥܦܝܬܐ": "ܒܐܪܒܥܦܢܝܬܐ", "ܒܕܟܘܬ": "ܒܕܟܝܘܬ", "ܒܗܠܠܝܢܢ": "ܡܗܠܠܝܢܢ",
    "ܒܘܟܬܟ": "ܒܘܪܟܬܟ", "ܒܚܛܗܘܝ": "ܒܚܛܗܘܗܝ", "ܒܚܢܟ": "ܒܚܢܢܟ",
    "ܒܠܡܟܘܬ": "ܒܡܠܟܘܬ", "ܒܪܚܐ": "ܒܪܘܚܐ", "ܒܪܝܟܒ": "ܒܪܝܟܘ", "ܒܬܥܪܐ": "ܒܬܗܪܐ",
    "ܓܒܒܪ": "ܓܢܒܪ", "ܓܒܠܐ": "ܓܒܝܐ", "ܓܕܫܝ": "ܓܕܫ", "ܕܐܝܠܢ": "ܕܐܝܠܝܢ",
    "ܕܐܪܕܪܟܢ": "ܕܐܕܪܟܢ", "ܕܒܒܝܠ": "ܕܒܒܠ", "ܕܒܓ": "ܕܒܓܙܐ", "ܕܓܡܪܪ": "ܕܓܡܪ",
    "ܕܙܚܝܘܟ": "ܕܙܝܚܘܟ", "ܕܛܝܒܘܪܬܟ": "ܕܛܝܒܘܬܟ", "ܕܝܗ": "ܕܝܗܒ", "ܕܟܕܪܬ": "ܕܟܬܪܬ",
    "ܕܟܠܗܘ": "ܕܟܠܗܘܢ", "ܕܠܟܠܗܝܢ": "ܕܟܠܗܝܢ", "ܕܢܒܠܫܘܢ": "ܕܢܠܒܫܘܢ",
    "ܕܢܗܗܘܢ": "ܕܢܗܘܘܢ", "ܕܢܟܠܗܘܢ": "ܕܢܟܠܘܢ", "ܕܥܘܥܠܐ": "ܕܥܘܠܐ",
    "ܕܨܒܢܝܐ": "ܕܨܒܝܢܐ", "ܕܩܘܪܕܫܐ": "ܕܩܘܕܫܐ", "ܕܪܒܥ": "ܕܪܒ",
    "ܕܬܗܝܡܢܬܘܢ": "ܕܐܬܗܝܡܢܬܘܢ", "ܕܬܘܬܘܒܘܬܢ": "ܕܬܘܬܒܘܬܢ", "ܕܬܡܡ": "ܕܬܡܢ",
    "ܗܝܟܚܐ": "ܗܝܟܠܐ", "ܗܝܢܡܘܬܐ": "ܗܝܡܢܘܬܐ", "ܗܟܦܬ": "ܗܦܟܬ",
    "ܘܐܟܬܥܒܘ": "ܘܐܟܬܒܘ", "ܘܐܡܪܡ": "ܘܐܡܪ", "ܘܐܣܪܕܬ": "ܘܐܣܬܪܕܬ",
    "ܘܐܬܪܚܡܠܥܝ": "ܘܐܬܪܚܡܥܠܝ", "ܘܒܒܗܬܬ": "ܘܒܗܬܬ", "ܘܒܚܚܐ": "ܘܒܚܝܐ",
    "ܘܙܥܙܘ": "ܘܙܥܘ", "ܘܝܚܝܬ": "ܘܬܚܝܬ", "ܘܟܐ": "ܘܠܐ", "ܘܠܒܒܬܘܢܗܝ": "ܘܠܒܒܬܘܢܝܗܝ",
    "ܘܡܓܒܢ": "ܘܡܒܓܢ", "ܘܡܫܥܝ": "ܘܫܡܥܝ", "ܘܥܒܕܬܗܝ": "ܘܥܒܕܬܝܗܝ",
    "ܘܪܚܡܘܝ": "ܘܪܚܡܘܗܝ", "ܘܪܚܡܥܠܢ": "ܘܪܚܡܥܠܝܢ", "ܘܫܘܩܢܐ": "ܘܫܘܒܩܢܐ",
    "ܘܫܬܡܠܝ": "ܐܫܬܡܠܝ", "ܚܒܐ": "ܚܘܒܐ", "ܚܗܘ": "ܕܗܘ", "ܛܘܒܘܝ": "ܛܘܒܘܗܝ",
    "ܛܘܒܝܗܗܘܢ": "ܛܘܒܝܗܘܢ", "ܛܘܒܝܗܘܘܢ": "ܛܘܒܝܗܘܢ", "ܛܝܒܘܪܬܗ": "ܛܝܒܘܬܗ",
    "ܛܝܒܘܬܐܟ": "ܛܝܒܘܬܟ", "ܝܫܥܘܥ": None, "ܟܠܗܢ": "ܟܠܗܘܢ",
    "ܠܙܝܩܐ": "ܠܙܕܝܩܐ", "ܠܛܪܘܡܐ": "ܠܛܪܘܢܐ", "ܠܡܙܝܪܬܢ": "ܠܙܡܝܪܬܢ",
    "ܠܡܦܕܝܗܘܢ": "ܠܡܦܝܕܝܗܘܢ", "ܠܢܚܝ": "ܠܢܝܚ", "ܠܥܝܬܢܝ": "ܛܥܝܬܢܝ",
    "ܠܥܡܝܢ": "ܠܥܠܡܝܢ", "ܠܩܘܣܢܛܝܢܘܣ": "ܠܩܘܣܛܢܛܝܢܘܣ", "ܠܫܡܐܟ": "ܠܫܡܟ",
    "ܡܗܠܝܢ": "ܡܗܠܠܝܢ", "ܡܠ": "ܟܠ", "ܡܨܚܡܢܐ": "ܡܪܚܡܢܐ", "ܡܩܒܥܠܝܢ": "ܡܩܒܠܝܢ",
    "ܡܫܕܕ": "ܡܫܕܪ", "ܢܕܚܟ": "ܢܕܚܠ", "ܢܗܗܘܢ": "ܢܗܘܘܢ", "ܢܘܡܬܢ": "ܝܘܡܬܢ",
    "ܢܚܫܘܟܐ": "ܒܚܫܘܟܐ", "ܢܡܥܠܢ": "ܢܡܠܠܢ", "ܢܣܘܢܐ": "ܢܣܝܘܢܐ",
    "ܢܣܚܢܘܢܗ": "ܢܚܣܢܘܢܗ", "ܢܬܬܘ": "ܢܬܬܘܐ", "ܣܒܕܐ": "ܣܒܪܐ", "ܥܡܡ": "ܥܡܡܐ",
    "ܦܪܘܘܩ": "ܦܪܘܩ", "ܦܪܩܠܛܐ": "ܦܪܩܠܝܛܐ", "ܨܨܠܘܬܗ": "ܨܠܘܬܗ", "ܩܕܗ": "ܩܕܡ",
    "ܩܕܡܟ": "ܩܕܡܝܟ", "ܩܘܒܢܐ": "ܩܘܪܒܢܐ", "ܩܘܕܡܗܝ": "ܩܘܕܡܘܗܝ",
    "ܩܘܕܡܟ": "ܩܘܕܡܝܟ", "ܩܘܪܫܬܐ": "ܩܘܫܬܐ", "ܩܪܩܬܗ": "ܦܪܩܬܗ", "ܩܪܩܬܢ": "ܦܪܩܬܢ",
    "ܪܚܡܗܘܝ": "ܪܚܡܘܗܝ", "ܫܘܪܩܢܐ": "ܫܘܒܩܢܐ", "ܬܥܘܥ": "ܬܥܘܠ",
    "ܬܪܝܨܢܐܝܬ": "ܬܪܝܨܐܝܬ", "ܬܪܥܘܪܬܐ": "ܬܪܥܘܬܐ", "ܬܬܟܪ": "ܬܬܕܟܪ",
}
# None: the right word depends on the passage; it is read from the matching copies.

LETTERS = "\u0710-\u072f\u074d-\u074f"
WORD = re.compile(f"[{LETTERS}][{LETTERS}\u0300-\u036f\u0730-\u074a\u0640]*")
CLAUSE_BREAK = re.compile(r"[\n.:\u0700*\u061b;,\u060c\u0706\u0707()\[\]]+")


def skeleton(word: str) -> str:
    return "".join(c for c in word if "\u0710" <= c <= "\u072f" or "\u074d" <= c <= "\u074f")


def _clauses(text: str):
    for clause in CLAUSE_BREAK.split(text):
        words = WORD.findall(clause)
        if len(words) >= 4:
            yield tuple(skeleton(w) for w in words), words


def _json_files(root: Path) -> list[Path]:
    files = list((root / "data" / "prayers").glob("*.json"))
    files += list((root / "data" / "psalms").glob("*.json"))
    return files


def build_replacements(root: Path) -> dict[str, str]:
    """Map each misspelled pointed word to the pointed word of its matching copies."""
    counts: collections.Counter = collections.Counter()
    pointed: dict[tuple, list[list[str]]] = collections.defaultdict(list)
    for path in _json_files(root):
        text = json.loads(path.read_text(encoding="utf-8"))["text"]
        for sk, words in _clauses(text):
            counts[sk] += 1
            if len(pointed[sk]) < 40:
                pointed[sk].append(words)

    masked: dict[tuple, list[tuple]] = collections.defaultdict(list)
    for sk, n in counts.items():
        if n >= 3:
            for i in range(len(sk)):
                masked[(sk[:i], sk[i + 1:])].append(sk)

    votes: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for sk, n in counts.items():
        if n > 2:
            continue
        for i, w in enumerate(sk):
            if w not in TYPOS:
                continue
            want = TYPOS[w]
            for other in masked.get((sk[:i], sk[i + 1:]), ()):
                right = other[i]
                if right == w or (want and right != want) or counts[other] < 3 * n:
                    continue
                if want is None and abs(len(right) - len(w)) > 1:
                    continue
                for words in pointed[sk]:
                    for copy in pointed[other]:
                        votes[words[i]][copy[i]] += 1
    return {bad: c.most_common(1)[0][0] for bad, c in votes.items()}


def _apply_to(text: str, pattern: re.Pattern, table: dict[str, str]) -> str:
    return pattern.sub(lambda m: table[m.group(0)], text)


def _apply(root: Path) -> None:
    table = build_replacements(root)
    if not table:
        print("No typos left to fix.")
        return
    for bad, good in sorted(table.items(), key=lambda kv: skeleton(kv[0])):
        print(f"  {bad} → {good}")
    alts = "|".join(sorted(map(re.escape, table), key=len, reverse=True))
    pattern = re.compile(f"(?<![{LETTERS}\u0300-\u036f\u0730-\u074a\u0640])(?:{alts})(?![{LETTERS}\u0300-\u036f\u0730-\u074a\u0640])")

    changed = 0
    paths = _json_files(root) + [p for p in (root / "web" / "data").glob("*.json")]
    for path in paths:
        raw = path.read_text(encoding="utf-8")
        new = _apply_to(raw, pattern, table)
        if new != raw:
            json.loads(new)
            path.write_text(new, encoding="utf-8")
            changed += 1
    for rel in ("prayers", "psalms"):
        for path in (root / rel).rglob("*.txt"):
            raw = path.read_text(encoding="utf-8")
            new = _apply_to(raw, pattern, table)
            if new != raw:
                path.write_text(new, encoding="utf-8")
                changed += 1
    print(f"Fixed {len(table)} misspelled words in {changed} files.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fix reviewed typos by comparing repeated passages. Lists the fixes; --apply rewrites."
    )
    parser.add_argument("--apply", action="store_true", help="rewrite the corpus in place")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.apply:
        _apply(root)
    else:
        for bad, good in sorted(build_replacements(root).items(), key=lambda kv: skeleton(kv[0])):
            print(f"  {bad} → {good}")
