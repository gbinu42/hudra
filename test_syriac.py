#!/usr/bin/env python3
"""Unit checks for scripts/fix_syriac_dots.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
from fix_syriac_dots import fix_dots


def test_examples():
    assert fix_dots("ܘܣܲܒܼܪܵܐ") == "ܘܣܲܒ݂ܪܵܐ"
    assert fix_dots("ܬܿ") == "ܬ݁"
    assert fix_dots("ܟܼ") == "ܟ݂"
    assert fix_dots("ܣܲܒܼܪܵܟܼ") == "ܣܲܒ݂ܪܵܟ݂"
    assert fix_dots("ܘܢܸܬܿܬܿܪܝܼ") == "ܘܢܸܬ݁ܬ݁ܪܝܼ"


def test_vowels_preserved():
    assert fix_dots("ܚܘܼܕܪܵܐ") == "ܚܘܼܕܪܵܐ"
    assert fix_dots("ܡܲܙܡܘܿܪܵܐ") == "ܡܲܙܡܘܿܪܵܐ"
    assert fix_dots("ܩܲܕܝܼܫܵܐ") == "ܩܲܕܝܼܫܵܐ"
    assert fix_dots("ܫܲܡܼܠܝܼ") == "ܫܲܡܼܠܝܼ"


def test_never_strips_unknown():
    assert "\u0330" in fix_dots("ܡ\u0330")
    assert fix_dots("ܒ݂") == "ܒ݂"
    assert fix_dots("ܬ݁") == "ܬ݁"


def test_linea_occultans_below():
    # U+0331 combining macron below is removed, not rewritten as U+0747.
    assert fix_dots("\u071a\u0331\u0722\u0732\u0722") == "\u071a\u0722\u0732\u0722"
    assert fix_dots("\u0717\u0331\u0718\u0735\u0710") == "\u0717\u0718\u0735\u0710"
    assert "\u0748" not in fix_dots("\u071a\u0331\u0722\u0732\u0722")
    assert "\u0747" not in fix_dots("\u071a\u0331\u0722\u0732\u0722")


def test_stacked_below_vowel():
    # Hbasa under /ā/ → combining dot below; zlama under /ā/ → diaeresis below.
    assert fix_dots("\u0717\u0304\u0718\u073c\u0735\u0718") == "\u0717\u0304\u0718\u0323\u0735\u0718"
    assert fix_dots("\u0717\u0718\u0738\u0735\u072c\u0742") == "\u0717\u0718\u0324\u0735\u072c\u0742"
    assert fix_dots("\u0717\u0718\u0738\u0735\u0718") == "\u0717\u0718\u0324\u0735\u0718"
    assert fix_dots("\u0729\u073c\u0735\u0721") == "\u0729\u0323\u0735\u0721"
    # Yodh is a mater: ܝܼܵ spans two syllables and is left alone.
    assert fix_dots("\u0722\u0712\u0742\u071d\u073c\u0735\u0710") == "\u0722\u0712\u0742\u071d\u073c\u0735\u0710"


def test_serto_vowels():
    assert fix_dots("\u0728\u073d\u0718\u072a") == "\u0728\u0718\u073c\u072a"
    assert fix_dots("\u072a\u073a\u072b\u0739\u0717") == "\u072a\u0739\u072b\u0739\u0717"
    assert fix_dots("\u0712\u071a\u0736\u0721\u072c\u0735\u0710") == "\u0712\u071a\u0738\u0721\u072c\u0735\u0710"
    # A waw that already carries a vowel absorbs the Serto mark.
    assert fix_dots("\u072a\u073d\u0718\u073f\u072a") == "\u072a\u0718\u073f\u072a"


def test_soft_pe():
    # Blanket soft-pe → breve is off; pe keeps rukkakha.
    assert fix_dots("ܦܼ") == "ܦ݂"
    assert fix_dots("ܦ݂") == "ܦ݂"
    # The listed lexemes take the breve where their pe closes a syllable.
    assert fix_dots("ܢܲܦ݂ܫܵܐ") == "ܢܲܦ̮ܫܵܐ"
    assert fix_dots("ܠܢܲܦ݂ܫܟ݂ܘܿܢ") == "ܠܢܲܦ̮ܫܟ݂ܘܿܢ"
    assert fix_dots("ܬܲܟ݂ܫܲܦ݂ܬܵܐ") == "ܬܲܟ݂ܫܲܦ̮ܬܵܐ"
    assert fix_dots("ܛܘܼܦ݂ܣܵܐ") == "ܛܘܼܦ̮ܣܵܐ"
    assert fix_dots("ܣܲܦ݂ܣܹܪܵܐ") == "ܣܲܦ̮ܣܹܪܵܐ"
    # A prefix puts the pe of ܦܬܚ in the same closing position.
    assert fix_dots("ܬܸܦ݂ܬܲܚ") == "ܬܸܦ̮ܬܲܚ"
    # Resh is spelled both ways in the corpus; the skeleton matches either.
    # Marks come back in the letter-syame-vowel order the rest of the pass uses.
    # Dotless rish + syame becomes ordinary resh + syame.
    assert fix_dots("\u0718\u0723\u0732\u0726\u0742\u0723\u0739\u0716\u0739\u0308\u0710") == (
        "\u0718\u0723\u0732\u0726\u032e\u0723\u0739\u072a\u0308\u0739\u0710"
    )
    # A vocalised pe inside a listed lexeme still takes the breve — the plural
    # of ܬܟܫܦܬܐ moves the vowel onto the pe and keeps it.
    assert fix_dots("ܒܬܲܟ݂ܫ̈ܦ݂ܵܬܲܢ") == "ܒܬܲܟ݂ܫ̈ܦ̮ܵܬܲܢ"
    # Word-final pe keeps rukkakha.
    assert fix_dots("ܡܓܲܕܦ݂") == "ܡܓܲܕܦ݂"
    # Lexemes outside the list are untouched wherever their pe sits.
    assert fix_dots("ܢܵܦ݂ܸܠ") == "ܢܵܦ݂ܸܠ"
    assert fix_dots("ܕܗܵܦ݂ܹܟ݂") == "ܕܗܵܦ݂ܹܟ݂"
    # An unmarked pe is never given a mark.
    assert fix_dots("ܢܲܦܫܵܐ") == "ܢܲܦܫܵܐ"


def test_soft_wins_over_hard():
    assert fix_dots("ܒܼܿ") == "ܒ݂"
    assert fix_dots("ܒ݂݁") == "ܒ݂"


def test_mark_order():
    # Qushshaya before vowel after remap from rwaha
    assert fix_dots("ܬܹܿ") == "ܬܹ݁"
    assert fix_dots("ܒܼܲ") == "ܒ݂ܲ"
    # Letter — syame — vowel
    assert fix_dots("ܒܲ̈") == "ܒ̈ܲ"
    assert fix_dots("ܪܲ̈") == "ܪ̈ܲ"
    assert fix_dots("ܪ̈ܲ") == "ܪ̈ܲ"


def test_syame_order():
    assert fix_dots("ܕܦܲܓ݂ܪ̈ܲܝܢ") == "ܕܦܲܓ݂ܪ̈ܲܝܢ"
    assert fix_dots("ܕܦܲܓ݂ܪܲ̈ܝܢ") == "ܕܦܲܓ݂ܪ̈ܲܝܢ"
    assert fix_dots("ܪ̈ܲܚܡܹܐ") == "ܪ̈ܲܚܡܹܐ"
    assert fix_dots("ܡܲܙܡܘܿܪܹ̈ܐ") == "ܡܲܙܡܘܿܪܹ̈ܐ"
    assert fix_dots("ܦܲܓ݂ܪܪ̈ܲܝܢ") == "ܦܲܓ݂ܪ̈ܲܝܢ"
    assert fix_dots("ܦܲܓ݂ܪܲܝܢ") == "ܦܲܓ݂ܪ̈ܲܝܢ"
    assert fix_dots("ܪܲ̈") == "ܪ̈ܲ"
    assert fix_dots("ܪ̈ܲ") == "ܪ̈ܲ"
    assert fix_dots("ܡܚܲܪܪܹ̈ܐ") == "ܡܚܲܪܪܹ̈ܐ"
    assert fix_dots("ܖ̈") == "ܪ̈"
    assert fix_dots("ܦܲܓ݂ܖ̈ܲܝܢ") == "ܦܲܓ݂ܪ̈ܲܝܢ"
    assert fix_dots("ܦܲܓ݂ܖܪ̈ܲܝܢ") == "ܦܲܓ݂ܪ̈ܲܝܢ"
    assert fix_dots("ܪ̈ܲܚܡܹܐ") == "ܪ̈ܲܚܡܹܐ"
    assert fix_dots("ܖ̈ܲܚܡܹܐ") == "ܪ̈ܲܚܡܹܐ"
    assert fix_dots("ܡܵܘܩܲܖ") == "ܡܵܘܩܲܪ"


def test_chaldean_min():
    from fix_syriac_dots import fix_chaldean_min

    assert fix_chaldean_min("ܡܢ ܒܝܼܫܵܐ") == "ܡ̣ܢ ܒܝܼܫܵܐ"
    assert fix_chaldean_min("ܘܡܢ ܥܵܠܲܡ") == "ܘܡ̣ܢ ܥܵܠܲܡ"
    assert fix_chaldean_min("ܕܡܢ ܩܕ݂ܝܼܡ") == "ܕܡ̣ܢ ܩܕ݂ܝܼܡ"
    assert fix_chaldean_min("ܡ݂ܢ ܫܡܲܝܵܐ") == "ܡ̣ܢ ܫܡܲܝܵܐ"
    assert fix_chaldean_min("ܠܡܢ ܣܵܓ݂ܕܝܼܬ݁ܘܿܢ") == "ܠܡܲܢ ܣܵܓ݂ܕܝܼܬ݁ܘܿܢ"
    assert fix_chaldean_min("ܒܡܢ ܚܲܟ݁ܝܼܡ") == "ܒܡܲܢ ܚܲܟ݁ܝܼܡ"
    # already pointed — leave alone
    assert fix_chaldean_min("ܡܲܢ ܕܨܵܒܹܐ") == "ܡܲܢ ܕܨܵܒܹܐ"
    assert fix_chaldean_min("ܡ̇ܢ ܕ") == "ܡ̇ܢ ܕ"
    assert fix_chaldean_min("ܡܵܢ ܐܝܼܬ݂") == "ܡܵܢ ܐܝܼܬ݂"
    assert fix_chaldean_min("ܡܸܢ ܒܝܼܫܵܐ") == "ܡ̣ܢ ܒܝܼܫܵܐ"
    assert fix_chaldean_min("ܡܸܢܝ") == "ܡܸܢܝ"
    assert fix_chaldean_min("ܡܸܢܹܗ") == "ܡܸܢܹܗ"
    # not a particle (continues as a word)
    assert fix_chaldean_min("ܡܢܘܼ") == "ܡܢܘܼ"
    # idempotent
    assert fix_chaldean_min("ܡ̣ܢ ܒܝܼܫܵܐ") == "ܡ̣ܢ ܒܝܼܫܵܐ"


if __name__ == "__main__":
    test_examples()
    test_vowels_preserved()
    test_never_strips_unknown()
    test_linea_occultans_below()
    test_stacked_below_vowel()
    test_serto_vowels()
    test_soft_pe()
    test_soft_wins_over_hard()
    test_mark_order()
    test_syame_order()
    test_chaldean_min()
    print("ok")
