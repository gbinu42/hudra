#!/usr/bin/env python3
"""
Normalize mis-encoded Syriac consonant dots in the prayer/psalm corpus.

East Syriac Madnhaya — common corpus confusions:
  1. U+073C HBASA-ESASA DOTTED on BGDKPT → U+0742 RUKKAKHA
     (on other letters U+073C is the legitimate /i/ vowel — keep)
  2. U+073F RWAHA on BGDKPT → U+0741 QUSHSHAYA
     (on waw U+073F is the legitimate /o/ vowel — keep).
     On other non-waw letters the same vowel dot stands in for a square
     / dot above, written as U+0307 (not qushshaya). A BGDKPT that already
     carries a vowel and follows zqapha is the CaCeC participle reading
     point, so that rwaha also becomes U+0307 rather than qushshaya.

Generic combining dots → Syriac marks when the base letter fits:
  3. U+0323 COMBINING DOT BELOW on BGDKPT → U+0742 RUKKAKHA
  4. U+0307 COMBINING DOT ABOVE on BGDKPT → U+0741 QUSHSHAYA.
     Overreach on the active participle is undone by 4b below.
  4b. Active-participle reading point: in the CaCeC participle the dot over
     the middle radical is a grammatical point, not qushshaya, and the radical
     is post-vocalic (soft). It is detected as a BGDKPT letter that carries a
     vowel of its own and follows a letter pointed with zqapha, and is written
     as U+0307. Gemination and hard positions have no preceding zqapha, so
     they keep qushshaya. The shape also fits a post-vocalic BGDKPT in a
     non-participle (ܥܒ݂ܵܕܹܿܝܗ̇), where the dot is more likely a mis-encoded
     syame; U+0307 is still the safe outcome there, since the letter is soft
     either way.
  5. U+0324 COMBINING DIAERESIS BELOW on ܬ → U+0740 FEMININE DOT
  5b. U+0331 COMBINING MACRON BELOW is removed.
     In this corpus the underline is noise (not a silent-letter mṭalqānā).
     U+0304 / U+0654 still become U+0747 via the bilingual-peshitta wrapper;
     U+0748 SYRIAC OBLIQUE LINE BELOW (mhaggyānā) is never produced here.

Soft pe (East Syriac convention) — narrowed to specific lexemes:
  6. (off) Blanket U+0742 on ܦ → U+032E COMBINING BREVE BELOW.
     Which of the two a soft pe takes depends on where it sits. Counting every
     marked pe in the hudra prayers: a pe that closes a syllable — no vowel of
     its own, a consonant behind it — is written with the breve 72,438 times
     and with rukkakha never; a pe carrying its own vowel (ܢܵܦ݂ܸܠ) or standing
     word-final (ܢܩܸܦ݂) keeps rukkakha. A blanket rule ignores that split, so
     it stays off.
  6b. The lexemes in BREVE_PE_LEXEMES take the breve: ܢܦ݂ܫ → ܢܦ̮ܫ, in every
     inflection and with any proclitic (ܢܲܦ̮ܫܹܗ, ܒܢܲܦ̮ܫܗܘܿܢ, ܠܢܲܦ̮ܫܟ݂ܘܿܢ),
     except where the pe is word-final. Within a listed lexeme the breve is
     kept even on a vocalised pe, since the corpus writes ܬܲܟܼܫ̈ܦ̮ܵܬܲܢ that way
     1,066 times. Only an existing rukkakha is rewritten; an unmarked pe is
     never given a mark the source did not write.

Mark order is normalized to letter–syame–vowel (e.g. ܪ̈ܲ).

Dotless rish (U+0716 ܖ) is a keyboard stand-in for resh with syame.
  It becomes U+072A ܪ, keeping syame. A dummy ܖ immediately before a
  real ܪ (ܦܲܓ݂ܖܪ̈) is dropped so the existing ܦܲܓ݂ܪܪ̈ collapse can fire.

Hbasa typed as rukkakha (U+073C on BGDKPT) is a keyboard stand-in for
  U+0742. A targeted --hbasa-only pass rewrites ܟܼ → ܟ݂ in place and
  does not reorder other marks. Hbasa on waw/yodh stays as /u/ / /i/.

Rwaha typed as qushshaya (U+073F on BGDKPT) is a keyboard stand-in for
  U+0741. A targeted --rwaha-only pass rewrites ܒܿ → ܒ݁ in place
  (ܒܬܸܫܒܿܘܿܚܬܵܐ → ܒܬܸܫܒ݁ܘܿܚܬܵܐ) and does not reorder other marks.
  Rwaha on waw stays as /o/. The same pass maps a non-waw rwaha that is
  not qushshaya to U+0307, and a stacked hbasa under /a/ or /ā/ on a
  non-BGDKPT letter to U+0323 (the lower-dot counterpart; yodh exempt).

Stacked vowels — a letter cannot carry two of them:
  7. A below vowel under a real /a/ or /ā/ (U+0732, U+0735) is a
     mis-encoded lower reading mark. Which mark depends on the vowel:
       U+073C HBASA → U+0323 COMBINING DOT BELOW (ܗ̄ܘܼܵܘ → ܗ̄ܘ̣ܵܘ)
       U+0738 / U+0739 ZLAMA → U+0324 COMBINING DIAERESIS BELOW
         (ܗܘܸܵܬ݂ → ܗܘ̤ܵܬ݂). NFC stores the marks as ܘ̣ܵ / ܘ̤ܵ.
     Yodh is exempt: ܝܼܵ is a genuine mater plus the following vowel
     (ܢܒ݂ܝܼܵܐ, ܐܹܠܝܼܵܐ), not a stacked pair.

Serto vowel signs left in a Madnhaya text:
  7b. U+0736 RBASA ABOVE → U+0738 DOTTED ZLAMA HORIZONTAL and
     U+073A HBASA ABOVE → U+0739 DOTTED ZLAMA ANGULAR, in place.
     U+073D ESASA ABOVE marks /u/ on the consonant before the waw; it moves
     onto the waw as U+073C (ܨܽܘܪ → ܨܘܼܪ). A waw that already carries
     a vowel keeps it and the Serto mark is absorbed, not duplicated.

"From" particle ܡ̣ܢ (applied when the text tradition uses this pointing):
  8. Bare particle ܡܢ / wrong ܡ݂ܢ, ܡܼܢ, ܡܢ݂ → ܡ̣ܢ (U+0323 DOT BELOW).
     Any one-dot-below shape counts, on either letter: the point belongs
     between them, so it lands on the mim or the nun depending on the source.
     Zlama form ܡܸܢ → ܡ̣ܢ, standalone particle only.
     Mirror case for "who": ܡ݁ܢ / ܡܢ݁ → ܡ̇ܢ (U+0307 DOT ABOVE), where
     qushshaya was typed for the supralinear point.
     Proclitics ܘ / ܕ kept: ܘܡ̣ܢ, ܕܡ̣ܢ.
     Only the standalone particle is pointed: ܡܢ inside a word
     (ܡܢܵܐ, ܡܢܵܬ݂ܵܐ, ܥܲܡܢ) is left alone, so the word boundary has to
     treat vowel points and other combining marks as word-internal.
     Do NOT touch already-pointed ܡܲܢ / ܡ̇ܢ / ܡܵܢ / ܡܼܢ,
     ܡܸܢ inside other roots (ܗܲܝܡܸܢ), or suffixed ܡܸܢܝ / ܡܸܢܹܗ / ܡܸܢܗܘܿܢ.
     Interrogative/relative "who" with ܠ or ܒ: ܠܡܢ → ܠܡܲܢ, ܒܡܢ → ܒܡܲܢ.
     A targeted --min-only pass rewrites only an already-marked ܡ݂ܢ / ܡܢ݂
     (rukkakha, hbasa, or breve standing in for the sublinear point) to ܡ̣ܢ.
     It does not point a bare ܡܢ.

Never delete diacritics: if no remapping rule applies, the mark is kept.
When soft + hard end up on the same letter, keep soft and drop qushshaya.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

BGDKPT = set("ܒܓܕܟܦܬ")
TAW = "ܬ"
YUDH = "ܝ"
WAW = "ܘ"
PE = "ܦ"
RESH = "\u072a"
DOTLESS_RISH = "\u0716"  # ܖ — keyboard stand-in for resh / resh-syame

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
ZQAPHA = "\u0735"  # /ā/ — first vowel of the CaCeC active participle
ZLAMA_HORIZONTAL = "\u0738"  # ܸ — Assyrian pointing on ܡܸܢ "from"
ZLAMA_ANGULAR = "\u0739"  # ܹ

MACRON_BELOW = "\u0331"  # generic underline — dropped, not promoted to ݇

# Serto vowel signs, sometimes left in an otherwise Madnhaya text.
RBASA_ABOVE = "\u0736"
HBASA_ABOVE = "\u073a"
ESASA_ABOVE = "\u073d"

# A real /a/ or /ā/; a below vowel stacked under one of these is a reading mark.
MAIN_ABOVE_VOWELS = {PTAHA, ZQAPHA}
# How that mark is written depends on which below vowel was misused for it.
STACKED_BELOW_TO_MARK = {
    HBASA: DOT_BELOW,  # ܗ̄ܘܼܵܘ → ܗ̄ܘ̣ܵܘ
    ZLAMA_HORIZONTAL: DIAERESIS_BELOW,  # ܗܘܸܵܬ݂ → ܗܘ̤ܵܬ݂
    ZLAMA_ANGULAR: DIAERESIS_BELOW,
}
BELOW_VOWELS = set(STACKED_BELOW_TO_MARK)

# Combining marks (generic + Syriac), used to skip pointing inside a word.
_MARKS = r"\u0300-\u036F\u0730-\u074A"
# Word-internal characters; used as a lookaround boundary for the mn particle.
# Combining marks belong here too: with letters alone, a neighbouring vowel
# point hides the rest of the word and ܡܢ matches inside it (ܡܢܵܐ, ܥܲܡܢ).
_MN_WORD_CHAR = r"\u0300-\u036F\u0710-\u072F\u0730-\u074A\u074D-\u074F"
# One-dot-below shapes wrongly used for the sublinear point of ܡ̣ܢ "from";
# the reference lists both ܡ݂ܢ (rukkakha) and ܡܼܢ (hbasa) as errors.
_MN_SOFT = f"[{RUKKAKHA}{BREVE_BELOW}{HBASA}]"
# The one-dot-above shape wrongly used for the supralinear point of ܡ̇ܢ "who".
_MN_HARD = f"[{QUSHSHAYA}]"
# Either kind of stray mark, for the proclitic "who" forms.
_MN_WRONG = f"[{RUKKAKHA}{BREVE_BELOW}{HBASA}{QUSHSHAYA}]"

# Consonant modifiers (excluding syame) that should precede vowel points.
CONSONANT_MODS = {RUKKAKHA, QUSHSHAYA, FEMININE, BREVE_BELOW}
VOWELS = {chr(c) for c in range(0x0730, 0x0740)}


def _remap_mark(base: str, mark: str) -> str | None:
    """Map a single combining mark. Return None to drop it."""
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
    if mark == MACRON_BELOW:
        return None
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


def fix_dotless_rish(text: str) -> str:
    """ܖ̈ → ܪ̈. A dummy ܖ immediately before ܪ is dropped (ܦܲܓ݂ܖܪ̈)."""
    if not text or DOTLESS_RISH not in text:
        return text
    result: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] != DOTLESS_RISH:
            result.append(text[i])
            i += 1
            continue
        marks: list[str] = []
        i += 1
        while i < n and unicodedata.category(text[i]).startswith("M"):
            marks.append(text[i])
            i += 1
        if SYAME not in marks and i < n and text[i] == RESH:
            continue
        result.append(RESH)
        result.extend(marks)
    return "".join(result)


def fix_hbasa_rukkakha(text: str) -> str:
    """ܟܼ → ܟ݂ on BGDKPT. Hbasa on other letters stays as /i/ or /u/."""
    if not text or HBASA not in text:
        return text
    result: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        result.append(ch)
        i += 1
        if ch not in BGDKPT:
            continue
        marks: list[str] = []
        while i < n and unicodedata.category(text[i]).startswith("M"):
            marks.append(text[i])
            i += 1
        if HBASA not in marks:
            result.extend(marks)
            continue
        # Replace in place; do not reorder. Soft wins if both marks sit
        # on the same letter (ܒܼܿ → ܒ݂). Collapse a duplicate rukkakha.
        new_marks: list[str] = []
        seen_rukk = False
        for m in marks:
            if m == HBASA:
                m = RUKKAKHA
            if m == QUSHSHAYA:
                continue
            if m == RUKKAKHA:
                if seen_rukk:
                    continue
                seen_rukk = True
            new_marks.append(m)
        result.extend(new_marks)
    return "".join(result)


def _rewrite_rwaha_marks(
    base: str, marks: list[str], prev_marks: list[str]
) -> list[str]:
    """Replace a stand-in rwaha; keep original mark order."""
    other_vowel = any(m in VOWELS and m != RWAHA for m in marks)
    has_soft = RUKKAKHA in marks or BREVE_BELOW in marks
    participle = (
        base in BGDKPT and other_vowel and ZQAPHA in prev_marks
    )
    new_marks: list[str] = []
    seen_qush = False
    seen_dot_above = False
    for m in marks:
        if m == RWAHA:
            if base == WAW:
                new_marks.append(m)
                continue
            if base in BGDKPT and not participle:
                m = QUSHSHAYA
            else:
                m = DOT_ABOVE
        if m == QUSHSHAYA:
            if has_soft or seen_qush:
                continue
            seen_qush = True
        elif m == DOT_ABOVE:
            if seen_dot_above:
                continue
            seen_dot_above = True
        new_marks.append(m)
    return new_marks


def fix_rwaha_qushshaya(text: str) -> str:
    """ܒܿ → ܒ݁ on BGDKPT. Rwaha on waw stays as /o/.

    A vowel-dot used as a square/dot above on a non-waw letter that cannot
    take qushshaya (or on a CaCeC participle middle radical) becomes U+0307.
    Marks are rewritten in place; they are not reordered.
    """
    if not text or RWAHA not in text:
        return text
    result: list[str] = []
    i = 0
    n = len(text)
    prev_marks: list[str] = []
    while i < n:
        ch = text[i]
        result.append(ch)
        i += 1
        if not ("\u0710" <= ch <= "\u072f"):
            if not unicodedata.category(ch).startswith("M"):
                prev_marks = []
            continue
        marks: list[str] = []
        while i < n and unicodedata.category(text[i]).startswith("M"):
            marks.append(text[i])
            i += 1
        if RWAHA in marks:
            marks = _rewrite_rwaha_marks(ch, marks, prev_marks)
        result.extend(marks)
        prev_marks = marks
    return "".join(result)


def fix_stacked_hbasa_dot_below(text: str) -> str:
    """Hbasa under /a/ or /ā/ on a non-BGDKPT letter → combining dot below.

    Bare hbasa stays as /i/ or /u/. Yodh is exempt (ܝܼܵ is a mater).
    BGDKPT is left to the rukkakha pass. Marks are not reordered.
    """
    if not text or HBASA not in text:
        return text
    result: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        result.append(ch)
        i += 1
        if not ("\u0710" <= ch <= "\u072f"):
            continue
        marks: list[str] = []
        while i < n and unicodedata.category(text[i]).startswith("M"):
            marks.append(text[i])
            i += 1
        stacked = (
            HBASA in marks
            and ch != YUDH
            and ch not in BGDKPT
            and any(m in MAIN_ABOVE_VOWELS for m in marks)
        )
        if not stacked:
            result.extend(marks)
            continue
        new_marks: list[str] = []
        seen_dot = False
        for m in marks:
            if m == HBASA:
                m = DOT_BELOW
            if m == DOT_BELOW:
                if seen_dot:
                    continue
                seen_dot = True
            new_marks.append(m)
        result.extend(new_marks)
    return "".join(result)


def fix_dots(text: str) -> str:
    if not text:
        return text

    text = fix_dotless_rish(text)

    # Ahead of the per-letter pass, so converted vowels are ordered with the
    # rest and can be seen by the stacked-vowel rule.
    text = fix_serto_vowels(text)

    result: list[str] = []
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

            result.append(base)
            result.extend(_order_marks(_finalize_marks(base, marks)))
        else:
            # Orphan combining mark (no base in stream) — keep as-is.
            result.append(char)
            i += 1

    out = "".join(result)
    # Plural "our bodies": ܦܲܓ݂ܪ̈ܲܝܢ (syame then vowel).
    out = out.replace("ܦܲܓ݂ܪܪ̈", "ܦܲܓ݂ܪ̈")
    out = out.replace("ܦܲܓ݂ܪܲ̈", "ܦܲܓ݂ܪ̈ܲ")
    out = out.replace("ܦܲܓ݂ܪܲܝܢ", "ܦܲܓ݂ܪ̈ܲܝܢ")
    out = fix_soft_pe_roots(out)
    out = fix_participle_points(out)
    return out


# Serto esasa marks the /u/ on the consonant before the waw; Madnhaya
# puts it on the waw itself (ܨܽܘܪ → ܨܘܼܪ). A waw that is already vocalised
# carries the Madnhaya reading, so the Serto mark is absorbed, not duplicated.
_ESASA_RE = re.compile(rf"{ESASA_ABOVE}([{_MARKS}]*){WAW}([{_MARKS}]*)")

# Serto vowels with a one-to-one Madnhaya counterpart on the same letter.
_SERTO_VOWELS = {RBASA_ABOVE: ZLAMA_HORIZONTAL, HBASA_ABOVE: ZLAMA_ANGULAR}


def fix_serto_vowels(text: str) -> str:
    """West Syriac vowel signs → their East Syriac counterparts."""
    if not text:
        return text
    for serto, madnhaya in _SERTO_VOWELS.items():
        text = text.replace(serto, madnhaya)
    if ESASA_ABOVE not in text:
        return text

    def sub(m: re.Match[str]) -> str:
        between, waw_marks = m.group(1), m.group(2)
        if any(c in VOWELS for c in waw_marks):
            return between + WAW + waw_marks
        return between + WAW + HBASA + waw_marks

    text = _ESASA_RE.sub(sub, text)
    # Anything left is already sitting on its own letter.
    return text.replace(ESASA_ABOVE, HBASA)


# Middle radical of a CaCeC active participle: BGDKPT carrying its own vowel,
# preceded by a letter pointed with zqapha (ܥܵܒܹ̇ܕ݂, ܣܵܦܹ̇ܩ, ܢܵܦܹ̇ܠ). The upper
# dot there is a reading point, so an inherited qushshaya is written back as a
# plain dot above. Hard/geminated forms (ܡܩܲܒܸ݁ܠ, ܣܲܓ݁ܝܼܐܵܐ) lack the zqapha.
_PARTICIPLE_POINT_RE = re.compile(
    rf"[\u0710-\u072F][{_MARKS}]*{ZQAPHA}[{_MARKS}]*"
    rf"[{''.join(sorted(BGDKPT))}][{_MARKS}]*"
)


def fix_participle_points(text: str) -> str:
    """CaCeC participle: dot over the middle radical is not qushshaya."""
    if not text or QUSHSHAYA not in text:
        return text

    def sub(m: re.Match[str]) -> str:
        cluster = m.group(0)
        # Marks of the BGDKPT letter only — everything after the last letter.
        split = max(
            i for i, ch in enumerate(cluster) if "\u0710" <= ch <= "\u072f"
        )
        head, marks = cluster[: split + 1], cluster[split + 1 :]
        if QUSHSHAYA not in marks or not any(m in VOWELS for m in marks):
            return cluster
        return head + marks.replace(QUSHSHAYA, DOT_ABOVE)

    return _PARTICIPLE_POINT_RE.sub(sub, text)


# Lexemes that spell soft pe with the breve rather than rukkakha, each given as
# the consonant skeleton around its pe. Matching on consonants alone covers every
# inflection and proclitic (ܢܲܦ̮ܫܹܗ, ܒܢܲܦ̮ܫܗܘܿܢ, ܠܢܲܦ̮ܫܟ݂ܘܿܢ), since only the marks
# between the letters vary. Attested with the breve in the hudra prayers, the
# Peshitta Gospels, or both.
BREVE_PE_LEXEMES = (
    "ܢܦܫ",  # soul, self
    "ܟܫܦ",  # ܬܟܫܦܬܐ, supplication
    "ܛܘܦܣ",  # ܛܘܦܣܐ type/figure, and its derivatives
    "ܦܬܚ",  # to open
    "ܦܓܥ",  # to meet
    "ܣܦܣܪ",  # sword
    "ܫܛܝܦܬ",  # torrential
    "ܢܦܛܪ",
    "ܢܦܬܠܝ",  # Naphtali
    "ܣܚܦ",  # to overthrow
    "ܪܦܫ",
    "ܙܦܬ",  # pitch
    "ܦܟܗ",  # to lose savour
    "ܬܦܪܝ",  # ܢܬܦܪܝܐ
)

_LETTERS = "\u0710-\u072f"
# The corpus spells resh both ways; a skeleton must match either.
_LETTER_CLASS = {RESH: f"[{RESH}{DOTLESS_RISH}]"}


def _breve_pe_re(skeleton: str) -> re.Pattern[str]:
    """Match the pe of one lexeme, capturing the marks it carries."""
    sep = f"[{_MARKS}]*"
    cut = skeleton.index(PE) + 1
    letters = [_LETTER_CLASS.get(c, c) for c in skeleton]
    head = sep.join(letters[:cut])
    tail = sep.join(letters[cut:])
    # Word-final pe keeps rukkakha (ܢܩܸܦ݂, ܡܓܲܕܦ݂), so something must follow.
    # Where the skeleton names the following letter, require it.
    follows = f"(?={tail})" if tail else f"(?=[{_LETTERS}])"
    return re.compile(f"({head})([{_MARKS}]*){follows}")


_BREVE_PE_RES = tuple(_breve_pe_re(s) for s in BREVE_PE_LEXEMES)


def fix_soft_pe_roots(text: str) -> str:
    """Soft pe takes the breve in these lexemes unless word-final: ܢܦ݂ܫ → ܢܦ̮ܫ."""
    if not text or PE not in text:
        return text
    for pattern in _BREVE_PE_RES:
        text = pattern.sub(
            lambda m: m.group(1) + m.group(2).replace(RUKKAKHA, BREVE_BELOW),
            text,
        )
    return text


def _finalize_marks(base: str, marks: list[str]) -> list[str]:
    new_marks = [m for m in (_remap_mark(base, m) for m in marks) if m]

    # A letter cannot carry two vowels: a below vowel stacked under a real
    # /a/ or /ā/ is a mis-encoded lower reading mark (ܗ̄ܘܼܵܘ → ̣,
    # ܗܘܸܵܬ݂ → ̤, ܩܼܵܡ → ̣). Yodh is exempt — there ܝܼܵ is a genuine
    # mater plus the following vowel (ܢܒ݂ܝܼܵܐ, ܐܹܠܝܼܵܐ).
    if base != YUDH and any(m in MAIN_ABOVE_VOWELS for m in new_marks):
        new_marks = [STACKED_BELOW_TO_MARK.get(m, m) for m in new_marks]

    # Soft pe → breve below is disabled; leave rukkakha on ܦ as ܦ݂.

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


# ܠܡܢ / ܒܡܢ (± prior ܘ/ܕ) → who with ptāḥā; bare/ܘ/ܕ ܡܢ → ܡ̣ܢ. A stray mark
# may sit on either letter (ܡ݂ܢ or ܡܢ݂), since it stands for a point that the
# script writes between them.
_WHO_MN_RE = re.compile(
    rf"(?<![{_MN_WORD_CHAR}])([ܘܕ]?[ܠܒ])ܡ{_MN_WRONG}?ܢ{_MN_WRONG}?"
    rf"(?![{_MN_WORD_CHAR}])"
)
# Standalone ܡ݁ܢ / ܡܢ݁ → ܡ̇ܢ: qushshaya standing in for the supralinear point.
_WHO_MN_DOT_RE = re.compile(
    rf"(?<![{_MN_WORD_CHAR}])([ܘܕ]?)ܡ(?:{_MN_HARD}ܢ|ܢ{_MN_HARD})"
    rf"(?![{_MN_WORD_CHAR}])"
)
_FROM_MN_RE = re.compile(
    rf"(?<![{_MN_WORD_CHAR}])([ܘܕ]?)ܡ{_MN_SOFT}?ܢ{_MN_SOFT}?(?![{_MN_WORD_CHAR}])"
)
# Targeted ܡ݂ܢ / ܡܢ݂ → ܡ̣ܢ: a below-dot stand-in is already present, so this
# does not invent pointing on a bare ܡܢ, nor rewrite ܠܡܢ / ܒܡܢ.
# Proclitic ܘ / ܕ may themselves carry marks (ܘܲܕ݂ܡ݂ܢ).
_FROM_MN_MARKED_RE = re.compile(
    rf"(?<![{_MN_WORD_CHAR}])((?:ܘ[{_MARKS}]*)?(?:ܕ[{_MARKS}]*)?)"
    rf"ܡ(?:{_MN_SOFT}ܢ|ܢ{_MN_SOFT})"
    rf"(?![{_MN_WORD_CHAR}])"
)
# Assyrian ܡܸܢ → ܡ̣ܢ. Standalone particle only: the lookbehind keeps ܗܲܝܡܸܢ
# out, and the lookahead keeps suffixed forms (ܡܸܢܝ, ܡܸܢܹܗ, ܡܸܢܗܘܿܢ) as they are.
_FROM_MN_ZLAMA_RE = re.compile(
    rf"(?<![{_MN_WORD_CHAR}])([ܘܕ]?)ܡ{ZLAMA_HORIZONTAL}ܢ(?![{_MN_WORD_CHAR}])"
)


def fix_chaldean_min(text: str) -> str:
    """Point the 'min' (from) particle; keep 'man' (who) distinct."""
    if not text or "ܡ" not in text:
        return text

    def who_sub(m: re.Match[str]) -> str:
        return m.group(1) + "ܡ" + PTAHA + "ܢ"

    def who_dot_sub(m: re.Match[str]) -> str:
        return m.group(1) + "ܡ" + DOT_ABOVE + "ܢ"

    def from_sub(m: re.Match[str]) -> str:
        return m.group(1) + "ܡ" + DOT_BELOW + "ܢ"

    # Who first so ܠܡܢ / ܒܡܢ are not turned into underdot "from".
    text = _WHO_MN_RE.sub(who_sub, text)
    text = _WHO_MN_DOT_RE.sub(who_dot_sub, text)
    text = _FROM_MN_ZLAMA_RE.sub(from_sub, text)
    text = _FROM_MN_RE.sub(from_sub, text)
    return text


def fix_min_rukkakha(text: str) -> str:
    """ܡ݂ܢ → ܡ̣ܢ. Only when a below-dot stand-in is already on mem or nun."""
    if not text or "ܡ" not in text:
        return text

    def from_sub(m: re.Match[str]) -> str:
        return m.group(1) + "ܡ" + DOT_BELOW + "ܢ"

    return _FROM_MN_MARKED_RE.sub(from_sub, text)


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


def _self_check() -> None:
    """Rule regressions taken from the corpus report."""
    assert fix_dots("ܘܣܲܒܼܪܵܐ") == "ܘܣܲܒ݂ܪܵܐ"
    assert fix_dots("ܬܿ") == "ܬ݁"
    assert fix_dots("ܟܼ") == "ܟ݂"
    assert fix_hbasa_rukkakha("ܠܵܟܼܘܼ") == "ܠܵܟ݂ܘܼ"
    assert fix_hbasa_rukkakha("ܚܘܼܕܪܵܐ") == "ܚܘܼܕܪܵܐ"  # /u/ on waw stays
    assert fix_hbasa_rukkakha("ܩܕܝܼܫܵܐ") == "ܩܕܝܼܫܵܐ"  # /i/ on yodh stays
    assert fix_hbasa_rukkakha("ܒܼ݁") == "ܒ݂"  # soft wins over real qushshaya
    assert fix_hbasa_rukkakha("ܟܼ̈") == "ܟ݂̈"  # do not reorder
    assert fix_rwaha_qushshaya("ܒܬܸܫܒܿܘܿܚܬܵܐ") == "ܒܬܸܫܒ݁ܘܿܚܬܵܐ"
    assert fix_rwaha_qushshaya("ܡܲܙܡܘܿܪܵܐ") == "ܡܲܙܡܘܿܪܵܐ"  # /o/ on waw stays
    assert fix_rwaha_qushshaya("ܬܿ") == "ܬ݁"
    assert fix_rwaha_qushshaya("ܬܹܿ") == "ܬܹ݁"  # do not reorder
    assert fix_rwaha_qushshaya("ܥܵܒܹܿܕ݂") == "ܥܵܒܹ̇ܕ݂"  # participle reading point
    assert fix_rwaha_qushshaya("ܒܵܛܹܿܠ") == "ܒܵܛܹ̇ܠ"  # non-BGDKPT square above
    assert fix_rwaha_qushshaya("ܨܠܵܘܵܬ݂̈ܵܗܿ") == "ܨܠܵܘܵܬ݂̈ܵܗ̇"
    assert fix_rwaha_qushshaya("ܒ݂ܿ") == "ܒ݂"  # soft wins
    assert fix_stacked_hbasa_dot_below("ܘܩܼܵܡ") == "ܘܩ̣ܵܡ"
    assert fix_stacked_hbasa_dot_below("ܗ̄ܘܼܵܘ") == "ܗ̄ܘ̣ܵܘ"
    assert fix_stacked_hbasa_dot_below("ܫܲܡܼܠܝܼ") == "ܫܲܡܼܠܝܼ"  # /i/ stays
    assert fix_stacked_hbasa_dot_below("ܚܘܼܕܪܵܐ") == "ܚܘܼܕܪܵܐ"
    assert fix_stacked_hbasa_dot_below("ܢܒ݂ܝܼܵܐ") == "ܢܒ݂ܝܼܵܐ"  # yodh mater
    assert fix_dots("ܦ݂") == "ܦ݂"  # soft pe keeps rukkakha (breve rule off)
    assert fix_dots("ܦܼ") == "ܦ݂"  # hbasa on pe → rukkakha, not breve
    assert fix_dots("ܘܢܵܦܼܸܠ") == "ܘܢܵܦ݂ܸܠ"
    # CaCeC participle: middle radical keeps a plain dot above, from either a
    # combining dot above or a rwaha in the source. Gemination and hard
    # positions have no preceding zqapha and keep qushshaya.
    assert fix_dots("\u0725\u0735\u0712\u0739\u073f\u0715\u0742") == (
        "\u0725\u0735\u0712\u0307\u0739\u0715\u0742"
    )
    assert fix_dots("\u0723\u0735\u0726\u0739\u073f\u0729") == (
        "\u0723\u0735\u0726\u0307\u0739\u0729"
    )
    assert fix_dots("\u0722\u0735\u0726\u0739\u073f\u0720") == (
        "\u0722\u0735\u0726\u0307\u0739\u0720"
    )
    assert fix_dots("\u0723\u0732\u0713\u073f\u071d\u073c\u0710\u0735\u0710") == (
        "\u0723\u0732\u0713\u0741\u071d\u073c\u0710\u0735\u0710"
    )
    assert fix_dots("\u0721\u0729\u0732\u0712\u0738\u073f\u0720") == (
        "\u0721\u0729\u0732\u0712\u0741\u0738\u0720"
    )
    assert fix_dots("ܥܵܒܹ̇ܕ݂") == "ܥܵܒܹ̇ܕ݂"
    assert fix_dots("ܨܵܒܹ̇ܝܢ") == "ܨܵܒܹ̇ܝܢ"
    # ܢܦܫ is the exception: breve below, every inflection and proclitic.
    assert fix_dots("ܢܲܦ݂ܫܵܐ") == "ܢܲܦ̮ܫܵܐ"
    assert fix_dots("ܠܢܲܦ݂ܫܟ݂ܘܿܢ") == "ܠܢܲܦ̮ܫܟ݂ܘܿܢ"
    assert fix_dots("ܒܢܲܦܼܫܗܘܿܢ") == "ܒܢܲܦ̮ܫܗܘܿܢ"
    assert fix_dots("ܢܲܦ̮ܫܹܗ") == "ܢܲܦ̮ܫܹܗ"  # already breve
    assert fix_dots("ܢܲܦ̈ܫܵܬ݂ܵܐ") == "ܢܲܦ̈ܫܵܬ݂ܵܐ"  # syame untouched
    assert fix_dots("ܚܘܼܕܪܵܐ") == "ܚܘܼܕܪܵܐ"  # hbasa on waw stays
    assert fix_dots("ܡܲܙܡܘܿܪܵܐ") == "ܡܲܙܡܘܿܪܵܐ"  # rwaha on waw stays
    assert fix_dots("ܕܦܲܓ݂ܪ̈ܲܝܢ") == "ܕܦܲܓ݂ܪ̈ܲܝܢ"
    assert fix_dots("ܦܲܓ݂ܪܪ̈ܲܝܗܘܿܢ") == "ܦܲܓ݂ܪ̈ܲܝܗܘܿܢ"
    assert fix_dots("ܪܲ̈") == "ܪ̈ܲ"
    assert fix_dots("ܖ̈") == "ܪ̈"
    assert fix_dots("ܦܲܓ݂ܖ̈ܲܝܢ") == "ܦܲܓ݂ܪ̈ܲܝܢ"
    assert fix_dots("ܦܲܓ݂ܖܪ̈ܲܝܢ") == "ܦܲܓ݂ܪ̈ܲܝܢ"
    assert fix_dots("ܖ̈ܲܚܡܹܐ") == "ܪ̈ܲܚܡܹܐ"
    # A below vowel stacked under a real /a/ or /ā/ is a lower reading dot.
    assert fix_dots("ܗ̄ܘܼܵܘ") == "ܗ̄ܘ̣ܵܘ"
    assert fix_dots("ܗ݇ܘܼܵܘ") == "ܗ݇ܘ̣ܵܘ"
    assert fix_dots("ܗ̄ܘܵܘ") == "ܗ̄ܘܵܘ"  # no below vowel
    assert fix_dots("ܗܘܸܵܬ݂") == "ܗܘ̤ܵܬ݂"  # "she was" — zlama → diaeresis below
    assert fix_dots("ܗܘܸܵܘ") == "ܗܘ̤ܵܘ"
    assert fix_dots("ܘܩܼܵܡ") == "ܘܩ̣ܵܡ"  # "and he arose"
    # Yodh is the mater exception: ܝܼܵ is two syllables, not a stacked pair.
    assert fix_dots("ܢܒ݂ܝܼܵܐ") == "ܢܒ݂ܝܼܵܐ"
    assert fix_dots("ܐܹܠܝܼܵܐ") == "ܐܹܠܝܼܵܐ"
    # Combining macron below is dropped (not rewritten as U+0747).
    assert fix_dots("ܚ̱ܢܲܢ") == "ܚܢܲܢ"
    assert fix_dots("ܐܲܢ̱ܬ݁ܬ݂ܵܐ") == "ܐܲܢܬ݁ܬ݂ܵܐ"
    # U+0748 is the mhaggyana, a different sign; it is never produced here.
    assert "݈" not in fix_dots("ܚ̱ܢܲܢ")
    assert "݇" not in fix_dots("ܚ̱ܢܲܢ")
    # Serto vowels → Madnhaya.
    assert fix_dots("ܨܽܘܪ") == "ܨܘܼܪ"  # esasa moves onto the waw
    assert fix_dots("ܒܲܚܪܽܘܿܪܵܐ") == (
        "ܒܲܚܪܘܿܪܵܐ"  # waw already vocalised
    )
    assert fix_dots("ܒܚܶܡܬܵܐ") == "ܒܚܸܡܬܵܐ"
    assert fix_dots("ܪܺܫܹܗ") == "ܪܹܫܹܗ"
    assert fix_chaldean_min("ܡܢ ܒܝܼܫܵܐ") == "ܡ̣ܢ ܒܝܼܫܵܐ"
    assert fix_chaldean_min("ܘܡܢ ܥܵܠܲܡ") == "ܘܡ̣ܢ ܥܵܠܲܡ"
    assert fix_chaldean_min("ܕܡܢ ܩܕ݂ܝܼܡ") == "ܕܡ̣ܢ ܩܕ݂ܝܼܡ"
    assert fix_chaldean_min("ܡ݂ܢ ܫܡܲܝܵܐ") == "ܡ̣ܢ ܫܡܲܝܵܐ"
    # Any one-dot-below shape, on either letter (the point belongs between).
    assert fix_chaldean_min("\u0721\u073c\u0722 \u0712\u071d\u073c\u072b\u0735\u0710") == (
        "\u0721\u0323\u0722 \u0712\u071d\u073c\u072b\u0735\u0710"
    )
    assert fix_chaldean_min("\u0721\u0722\u0742 \u071b\u0712") == "\u0721\u0323\u0722 \u071b\u0712"
    # Qushshaya typed for the supralinear point of "who".
    assert fix_chaldean_min("\u0721\u0741\u0722 \u0715") == "\u0721\u0307\u0722 \u0715"
    assert fix_chaldean_min("\u0721\u0722\u0741 \u0715") == "\u0721\u0307\u0722 \u0715"
    assert fix_chaldean_min("ܠܡܢ ܣܵܓ݂ܕܝܼܬ݁ܘܿܢ") == "ܠܡܲܢ ܣܵܓ݂ܕܝܼܬ݁ܘܿܢ"
    assert fix_chaldean_min("ܒܡܢ ܚܲܟ݁ܝܼܡ") == "ܒܡܲܢ ܚܲܟ݁ܝܼܡ"
    assert fix_chaldean_min("ܡܲܢ ܕܨܵܒܹܐ") == "ܡܲܢ ܕܨܵܒܹܐ"  # already who
    assert fix_chaldean_min("ܡ̇ܢ ܕ") == "ܡ̇ܢ ܕ"
    assert fix_chaldean_min("ܡܸܢ ܒܝܼܫܵܐ") == "ܡ̣ܢ ܒܝܼܫܵܐ"
    assert fix_chaldean_min("ܘܡܸܢ ܥܵܠܲܡ") == "ܘܡ̣ܢ ܥܵܠܲܡ"
    # Suffixed forms keep the Assyrian pointing; only the particle is changed.
    assert fix_chaldean_min("ܡܸܢܝ") == "ܡܸܢܝ"
    assert fix_chaldean_min("ܡܸܢܹܗ") == "ܡܸܢܹܗ"
    assert fix_chaldean_min("ܡܸܢܗܘܿܢ") == "ܡܸܢܗܘܿܢ"
    assert fix_chaldean_min("ܡܸܢܟ݂ܘܿܢ") == "ܡܸܢܟ݂ܘܿܢ"
    assert fix_chaldean_min("ܗܲܝܡܸܢ") == "ܗܲܝܡܸܢ"  # believe, not particle
    assert fix_chaldean_min("ܡܗܲܝܡܸܢ") == "ܡܗܲܝܡܸܢ"
    # Only the standalone particle: ܡܢ inside a pointed word stays bare.
    assert fix_chaldean_min("ܡܢܵܐ ܥܵܒܹܕ݂") == "ܡܢܵܐ ܥܵܒܹܕ݂"
    assert fix_chaldean_min("ܡܢܵܬ݂ܵܐ") == "ܡܢܵܬ݂ܵܐ"
    assert fix_chaldean_min("ܥܲܡܢ") == "ܥܲܡܢ"
    assert fix_chaldean_min("ܡܢܗܘܿܢ") == "ܡܢܗܘܿܢ"
    assert fix_chaldean_min("ܡ̣ܢ ܟܠ") == "ܡ̣ܢ ܟܠ"  # idempotent
    assert fix_min_rukkakha("ܡ݂ܢ ܫܡܲܝܵܐ") == "ܡ̣ܢ ܫܡܲܝܵܐ"
    assert fix_min_rukkakha("ܘܡ݂ܢ ܥܵܠܲܡ") == "ܘܡ̣ܢ ܥܵܠܲܡ"
    assert fix_min_rukkakha("ܕܡ݂ܢ ܩܕ݂ܝܼܡ") == "ܕܡ̣ܢ ܩܕ݂ܝܼܡ"
    assert fix_min_rukkakha("ܘܲܕ݂ܡ݂ܢ ܥܵܠܲܡ") == "ܘܲܕ݂ܡ̣ܢ ܥܵܠܲܡ"
    assert fix_min_rukkakha("ܡܢ݂ ܫܡܲܝܵܐ") == "ܡ̣ܢ ܫܡܲܝܵܐ"
    assert fix_min_rukkakha("ܡܢ ܒܝܼܫܵܐ") == "ܡܢ ܒܝܼܫܵܐ"  # do not invent a point
    assert fix_min_rukkakha("ܠܡ݂ܢ") == "ܠܡ݂ܢ"  # not the "from" particle
    assert fix_min_rukkakha("ܣܵܡ݂ ܥܲܠ") == "ܣܵܡ݂ ܥܲܠ"  # rukkakha on other mem
    assert fix_min_rukkakha("ܡ̣ܢ ܟܠ") == "ܡ̣ܢ ܟܠ"


def _apply_to_corpus(ROOT: Path) -> None:
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


def _apply_rish_only(ROOT: Path) -> None:
    """Rewrite ܖ → ܪ in corpus files without touching other diacritics."""
    seen: set[Path] = set()
    changed = 0
    remaining = 0
    for path in _corpus_json_files(ROOT):
        path = path.resolve()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        raw = path.read_text(encoding="utf-8")
        new = fix_dotless_rish(raw)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            changed += 1
        remaining += new.count(DOTLESS_RISH)
    print(f"Rewrote dotless rish in {changed} files; {remaining} U+0716 left.")


def _corpus_json_files(ROOT: Path) -> list[Path]:
    files: list[Path] = []
    for rel in (
        "data/prayers",
        "data/psalms",
        "web/data",
        "web/public/data/prayers",
        "web/public/data/psalms",
        "web/public/data",
    ):
        d = ROOT / rel
        if d.is_dir():
            files.extend(d.glob("*.json"))
        elif d.is_file() and d.suffix == ".json":
            files.append(d)
    for name in ("index.json", "psalms_index.json", "catalog.json"):
        files.append(ROOT / "data" / name)
    return files


def _hbasa_on_bgdkpt_left(text: str) -> int:
    """How many U+073C still sit on a BGDKPT cluster."""
    n = 0
    i = 0
    length = len(text)
    while i < length:
        ch = text[i]
        i += 1
        if ch not in BGDKPT:
            continue
        while i < length and unicodedata.category(text[i]).startswith("M"):
            if text[i] == HBASA:
                n += 1
            i += 1
    return n


def _apply_hbasa_only(ROOT: Path) -> None:
    """Rewrite ܼ on BGDKPT → ݂ without touching other diacritics."""
    seen: set[Path] = set()
    changed = 0
    remaining = 0
    for path in _corpus_json_files(ROOT):
        path = path.resolve()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        raw = path.read_text(encoding="utf-8")
        new = fix_hbasa_rukkakha(raw)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            changed += 1
        remaining += _hbasa_on_bgdkpt_left(new)
    print(
        f"Rewrote hbasa-as-rukkakha in {changed} files; "
        f"{remaining} U+073C still on BGDKPT."
    )


def _rwaha_on_bgdkpt_left(text: str) -> int:
    """How many U+073F still sit on a BGDKPT cluster."""
    n = 0
    i = 0
    length = len(text)
    while i < length:
        ch = text[i]
        i += 1
        if ch not in BGDKPT:
            continue
        while i < length and unicodedata.category(text[i]).startswith("M"):
            if text[i] == RWAHA:
                n += 1
            i += 1
    return n


def _apply_rwaha_only(ROOT: Path) -> None:
    """Rewrite vowel-dot stand-ins for square dots without reordering."""
    seen: set[Path] = set()
    changed = 0
    remaining = 0
    for path in _corpus_json_files(ROOT):
        path = path.resolve()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        raw = path.read_text(encoding="utf-8")
        new = fix_stacked_hbasa_dot_below(fix_rwaha_qushshaya(raw))
        if new != raw:
            path.write_text(new, encoding="utf-8")
            changed += 1
        remaining += _rwaha_on_bgdkpt_left(new)
    print(
        f"Rewrote rwaha-as-qushshaya (and stacked hbasa) in {changed} files; "
        f"{remaining} U+073F still on BGDKPT."
    )


def _apply_min_only(ROOT: Path) -> None:
    """Rewrite ܡ݂ܢ → ܡ̣ܢ without touching bare ܡܢ or other diacritics."""
    seen: set[Path] = set()
    changed = 0
    remaining = 0
    for path in _corpus_json_files(ROOT):
        path = path.resolve()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        raw = path.read_text(encoding="utf-8")
        new = fix_min_rukkakha(raw)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            changed += 1
        remaining += len(_FROM_MN_MARKED_RE.findall(new))
    print(
        f"Rewrote ܡ݂ܢ → ܡ̣ܢ in {changed} files; "
        f"{remaining} marked-from particles still using rukkakha/hbasa."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Normalize Syriac diacritics. Runs the rule self-check by default; "
            "rewriting the corpus requires --apply."
        )
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="rewrite the prayer/psalm corpus in place",
    )
    parser.add_argument(
        "--rish-only",
        action="store_true",
        help="with --apply, rewrite only ܖ → ܪ (leave other marks alone)",
    )
    parser.add_argument(
        "--hbasa-only",
        action="store_true",
        help="with --apply, rewrite only ܼ on BGDKPT → ݂ (leave other marks alone)",
    )
    parser.add_argument(
        "--rwaha-only",
        action="store_true",
        help=(
            "with --apply, rewrite ܿ on BGDKPT → ݁, other non-waw ܿ → ̇, "
            "and stacked ܼ under /a/ /ā/ on non-BGDKPT → ̣"
        ),
    )
    parser.add_argument(
        "--min-only",
        action="store_true",
        help="with --apply, rewrite only ܡ݂ܢ / ܡܢ݂ → ܡ̣ܢ (leave bare ܡܢ alone)",
    )
    parser.add_argument(
        "--self-check",
        action="store_true",
        help="only run the rule regressions (default when --apply is absent)",
    )
    args = parser.parse_args()

    _self_check()
    if not args.apply:
        print("Self-check passed. Re-run with --apply to rewrite the corpus.")
        raise SystemExit(0)

    root = Path(__file__).resolve().parents[1]
    if args.rish_only:
        _apply_rish_only(root)
    elif args.hbasa_only:
        _apply_hbasa_only(root)
    elif args.rwaha_only:
        _apply_rwaha_only(root)
    elif args.min_only:
        _apply_min_only(root)
    else:
        _apply_to_corpus(root)
