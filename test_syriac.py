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
    assert "\u0331" in fix_dots("ܡ\u0331")
    assert fix_dots("ܒ݂") == "ܒ݂"
    assert fix_dots("ܬ݁") == "ܬ݁"


def test_soft_pe():
    assert fix_dots("ܦܼ") == "ܦ\u032e"
    assert fix_dots("ܦ݂") == "ܦ\u032e"


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


def test_dotless_rish():
    # Plural resh is ܪ̈ with syame before vowels (ܪ̈ܲ); ܖ → ܪ
    assert fix_dots("ܕܦܲܓ݂ܖ̈ܲܝܢ") == "ܕܦܲܓ݂ܪ̈ܲܝܢ"
    assert fix_dots("ܕܦܲܓ݂ܪ̈ܲܝܢ") == "ܕܦܲܓ݂ܪ̈ܲܝܢ"
    assert fix_dots("ܕܦܲܓ݂ܪܲ̈ܝܢ") == "ܕܦܲܓ݂ܪ̈ܲܝܢ"
    assert fix_dots("ܖ̈ܲܚܡܹܐ") == "ܪ̈ܲܚܡܹܐ"
    assert fix_dots("ܪ̈ܲܚܡܹܐ") == "ܪ̈ܲܚܡܹܐ"
    assert fix_dots("ܡܲܙܡܘܿܖܹ̈ܐ") == "ܡܲܙܡܘܿܪܹ̈ܐ"
    # merge clusters
    assert fix_dots("ܦܲܓ݂ܖܪ̈ܲܝܗܘܿܢ") == "ܦܲܓ݂ܪ̈ܲܝܗܘܿܢ"
    assert fix_dots("ܦܲܓ݂ܪܖ̈ܲܝܢ") == "ܦܲܓ݂ܪ̈ܲܝܢ"
    assert fix_dots("ܦܲܓ݂ܪܪ̈ܲܝܢ") == "ܦܲܓ݂ܪ̈ܲܝܢ"
    assert fix_dots("ܦܲܓ݂ܪܲܝܢ") == "ܦܲܓ݂ܪ̈ܲܝܢ"
    assert fix_dots("ܐܘܖܼܪܚܵܐ") == "ܐܘܪܼܚܵܐ"
    # bare / vowelled ܖ without syame → ܪ
    assert fix_dots("ܝܵܖܘܿܬܵܐ") == "ܝܵܪܘܿܬܵܐ"
    assert fix_dots("ܖܲܒܵܐ") == "ܪܲܒܵܐ"
    # vowel-before-syame → syame-before-vowel
    assert fix_dots("ܪܲ̈") == "ܪ̈ܲ"
    assert fix_dots("ܖܲ̈") == "ܪ̈ܲ"
    assert fix_dots("ܪ̈ܲ") == "ܪ̈ܲ"
    # legitimate double resh kept
    assert fix_dots("ܡܚܲܪܪܹ̈ܐ") == "ܡܚܲܪܪܹ̈ܐ"


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
    assert fix_chaldean_min("ܡܸܢ ܒܝܼܫܵܐ") == "ܡܸܢ ܒܝܼܫܵܐ"
    # not a particle (continues as a word)
    assert fix_chaldean_min("ܡܢܘܼ") == "ܡܢܘܼ"
    # idempotent
    assert fix_chaldean_min("ܡ̣ܢ ܒܝܼܫܵܐ") == "ܡ̣ܢ ܒܝܼܫܵܐ"


if __name__ == "__main__":
    test_examples()
    test_vowels_preserved()
    test_never_strips_unknown()
    test_soft_pe()
    test_soft_wins_over_hard()
    test_mark_order()
    test_dotless_rish()
    test_chaldean_min()
    print("ok")
