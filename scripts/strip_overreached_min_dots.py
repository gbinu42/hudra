#!/usr/bin/env python3
"""One-off: remove the mid-word ܡ̣ܢ dots left by the old fix_syriac_dots rule.

Until the word boundary in fix_chaldean_min was widened to cover combining
marks, a vowel point next to the particle looked like a word boundary, so
ܡܢ inside a pointed word was given the "from" dot (ܡ̣ܢܲܚܡܵܢܵܐ, ܥܲܡ̣ܢ).

Only mark-adjacent dots are stripped, since that is the only shape the old
rule could produce. Forms whose ܡ̣ܢ is followed by a letter — the particle
with a pronominal suffix, ܡ̣ܢܗܘܿܢ / ܡ̣ܢܢ / ܡ̣ܢܟ݂ — predate the rule and are
left untouched, as is the standalone particle.

Dry run by default; pass --apply to write.
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOT_BELOW = "\u0323"
MARK = "\u0300-\u036F\u0730-\u074A"
WORD_CHAR = f"{MARK}\u0710-\u072F\u074D-\u074F"

WORD_RE = re.compile(f"[{WORD_CHAR}]+")
MIN = f"ܡ{DOT_BELOW}ܢ"
# Nothing but proclitics in front of the particle — ܡ̣ܢ, ܕܡ̣ܢ, ܘܲܕ݂ܡ̣ܢ, ܘܠܲܕ݂ܡ̣ܢ.
# The rule only models a single proclitic, so vocalized pairs land here even
# though their dot is correct; they must survive the sweep.
PARTICLE_RE = re.compile(f"^[ܘܕܠܒ{MARK}]*{MIN}$")
# The dot the old rule could add: a combining mark abuts the particle.
OVERREACH_RE = re.compile(f"(?<=[{MARK}])ܡ{DOT_BELOW}ܢ|ܡ{DOT_BELOW}ܢ(?=[{MARK}])")


def clean_word(word: str) -> str:
    if MIN not in word or PARTICLE_RE.match(word):
        return word
    if not OVERREACH_RE.search(word):
        return word
    return OVERREACH_RE.sub(lambda m: m.group(0).replace(DOT_BELOW, ""), word)


def clean_text(text: str) -> tuple[str, Counter]:
    found: Counter = Counter()

    def sub(m: re.Match[str]) -> str:
        word = m.group(0)
        fixed = clean_word(word)
        if fixed != word:
            found[f"{word} → {fixed}"] += 1
        return fixed

    return WORD_RE.sub(sub, text), found


def iter_files():
    for rel in ("prayers", "psalms"):
        yield from (ROOT / rel).rglob("*.txt")
    yield from (ROOT / "data").rglob("*.json")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write changes")
    args = ap.parse_args()

    totals: Counter = Counter()
    changed_files = 0

    for path in iter_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if MIN not in text:
            continue
        new_text, found = clean_text(text)
        if not found:
            continue
        changed_files += 1
        totals.update(found)
        if args.apply:
            path.write_text(new_text, encoding="utf-8")

    print(f"{'Rewrote' if args.apply else 'Would rewrite'} {changed_files} files")
    print(f"dots removed: {sum(totals.values())}")
    print(f"distinct word forms: {len(totals)}\n")
    for word, count in totals.most_common():
        print(f"  {count:6d}  {word}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
