#!/usr/bin/env python3
"""Unit checks for scripts/fix_syriac_dots.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
from fix_syriac_dots import (
    fix_ayt_hbasa,
    fix_dot_above_qushshaya,
    fix_dots,
    fix_hbasa_above_dot,
    fix_hbasa_rukkakha,
    fix_macron_linea,
    fix_min_rukkakha,
    fix_min_zlama,
    fix_rwaha_qushshaya,
    fix_stacked_hbasa_dot_below,
)


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
    assert fix_dots("ܫܲܡ̣ܠܝܼ") == "ܫܲܡ̣ܠܝܼ"
    assert fix_dots("ܫܲܡܼܠܝܼ") == "ܫܲܡ̣ܠܝܼ"


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
    # Macron above on heh is linea occultans (U+0747), not kept as U+0304.
    assert fix_dots("\u0717\u0304\u0718\u073c\u0735\u0718") == "\u0717\u0747\u0718\u0323\u0735\u0718"
    assert fix_dots("\u0717\u0718\u0738\u0735\u072c\u0742") == "\u0717\u0718\u0324\u0735\u072c\u0742"
    assert fix_dots("\u0717\u0718\u0738\u0735\u0718") == "\u0717\u0718\u0324\u0735\u0718"
    assert fix_dots("\u0729\u073c\u0735\u0721") == "\u0729\u0323\u0735\u0721"
    # Yodh is a mater: ܝܼܵ spans two syllables and is left alone.
    assert fix_dots("\u0722\u0712\u0742\u071d\u073c\u0735\u0710") == "\u0722\u0712\u0742\u071d\u073c\u0735\u0710"


def test_serto_vowels():
    assert fix_dots("\u0728\u073d\u0718\u072a") == "\u0728\u0718\u073c\u072a"
    assert fix_dots("\u072a\u073a\u072b\u0739\u0717") == "\u072a\u0307\u072b\u0739\u0717"
    assert fix_dots("\u071d\u073a") == "\u071d\u0739"
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


def test_hbasa_rukkakha_only():
    # Targeted pass: ܼ on BGDKPT → ݂; other letters and mark order stay.
    assert fix_hbasa_rukkakha("ܠܵܟܼܘܼ") == "ܠܵܟ݂ܘܼ"
    assert fix_hbasa_rukkakha("ܣܲܒܼܪܵܟܼ") == "ܣܲܒ݂ܪܵܟ݂"
    assert fix_hbasa_rukkakha("ܚܘܼܕܪܵܐ") == "ܚܘܼܕܪܵܐ"
    assert fix_hbasa_rukkakha("ܩܕܝܼܫܵܐ") == "ܩܕܝܼܫܵܐ"
    assert fix_hbasa_rukkakha("ܫܲܡܼܠܝܼ") == "ܫܲܡܼܠܝܼ"
    assert fix_hbasa_rukkakha("ܒܼ݁") == "ܒ݂"
    assert fix_hbasa_rukkakha("ܒܼܿ") == "ܒ݂ܿ"  # rwaha is a different rule
    assert fix_hbasa_rukkakha("ܟܼ̈") == "ܟ݂̈"
    assert fix_hbasa_rukkakha("ܪ̈ܲ") == "ܪ̈ܲ"


def test_rwaha_qushshaya_only():
    # Targeted pass: ܿ on BGDKPT → ݁; /o/ on waw and mark order stay.
    assert fix_rwaha_qushshaya("ܒܬܸܫܒܿܘܿܚܬܵܐ") == "ܒܬܸܫܒ݁ܘܿܚܬܵܐ"
    assert fix_rwaha_qushshaya("ܡܫܲܒܿܚܝܼܢ") == "ܡܫܲܒ݁ܚܝܼܢ"
    assert fix_rwaha_qushshaya("ܡܲܙܡܘܿܪܵܐ") == "ܡܲܙܡܘܿܪܵܐ"
    assert fix_rwaha_qushshaya("ܬܿ") == "ܬ݁"
    assert fix_rwaha_qushshaya("ܬܹܿ") == "ܬܹ݁"
    assert fix_rwaha_qushshaya("ܥܵܒܹܿܕ݂") == "ܥܵܒܹ̇ܕ݂"
    assert fix_rwaha_qushshaya("ܒܵܛܹܿܠ") == "ܒܵܛܹ̇ܠ"
    assert fix_rwaha_qushshaya("ܨܠܵܘܵܬ݂̈ܵܗܿ") == "ܨܠܵܘܵܬ݂̈ܵܗ̇"
    assert fix_rwaha_qushshaya("ܒ݂ܿ") == "ܒ݂"
    assert fix_rwaha_qushshaya("ܣܲܓܿܝܼܐܵܐ") == "ܣܲܓ݁ܝܼܐܵܐ"


def test_dot_above_qushshaya_only():
    assert fix_dot_above_qushshaya("ܘܠܲܝܬ̇") == "ܘܠܲܝܬ݁"
    assert fix_dot_above_qushshaya("ܐܲܢ݇ܬ̇") == "ܐܲܢ݇ܬ݁"
    assert fix_dot_above_qushshaya("ܫܲܒ̇ܚܘܼܗܝ") == "ܫܲܒ݁ܚܘܼܗܝ"
    assert fix_dot_above_qushshaya("ܥܵܒܹ̇ܕ݂") == "ܥܵܒܹ̇ܕ݂"
    assert fix_dot_above_qushshaya("ܝܵܬܹ̇ܒ݂") == "ܝܵܬܹ̇ܒ݂"
    assert fix_dot_above_qushshaya("ܡ̇ܢ") == "ܡ̇ܢ"
    assert fix_dot_above_qushshaya("ܘܠܲܝܬ݁") == "ܘܠܲܝܬ݁"
    assert fix_dots("ܘܠܲܝܬ̇") == "ܘܠܲܝܬ݁"


def test_stacked_hbasa_dot_below_only():
    assert fix_stacked_hbasa_dot_below("ܘܩܼܵܡ") == "ܘܩ̣ܵܡ"
    assert fix_stacked_hbasa_dot_below("ܗ̄ܘܼܵܘ") == "ܗ̄ܘ̣ܵܘ"
    assert fix_stacked_hbasa_dot_below("ܫܲܡ̣ܠܝܼ") == "ܫܲܡ̣ܠܝܼ"
    assert fix_stacked_hbasa_dot_below("ܫܲܡܼܠܝܼ") == "ܫܲܡ̣ܠܝܼ"
    assert fix_stacked_hbasa_dot_below("ܛܲܥܼܢܹܗ") == "ܛܲܥ̣ܢܹܗ"
    assert fix_stacked_hbasa_dot_below("ܚܘܼܕܪܵܐ") == "ܚܘܼܕܪܵܐ"
    assert fix_stacked_hbasa_dot_below("ܢܒ݂ܝܼܵܐ") == "ܢܒ݂ܝܼܵܐ"
    assert fix_stacked_hbasa_dot_below("ܒܼܵ") == "ܒܼܵ"
    assert fix_stacked_hbasa_dot_below("ܘܲܥܪܲܩܼ") == "ܘܲܥܪܲܩ̣"
    assert fix_stacked_hbasa_dot_below("ܐܲܩܼܝܼܡ") == "ܐܲܩ̣ܝܼܡ"
    assert fix_stacked_hbasa_dot_below("ܫܒܲܩܼ݇ܢ") == "ܫܒܲܩ̣݇ܢ"
    assert fix_stacked_hbasa_dot_below("ܠܒܸܫܼ") == "ܠܒܸܫ̣"
    assert fix_dots("ܘܲܥܪܲܩܼ") == "ܘܲܥܪܲܩ̣"


def test_hbasa_above_dot_only():
    assert fix_hbasa_above_dot("ܒܺ") == "ܒ݁"
    assert fix_hbasa_above_dot("ܥܺ") == "ܥ̇"
    assert fix_hbasa_above_dot("ܝܺ") == "ܝܺ"
    assert fix_hbasa_above_dot("ܘܺ") == "ܘܺ"
    assert fix_hbasa_above_dot("ܢܲܺ") == "ܢܲ̇"
    assert fix_hbasa_above_dot("ܥܵܒܹܺܕ݂") == "ܥܵܒܹ̇ܕ݂"
    assert fix_dots("ܪܺܫܹܗ") == "ܪ̇ܫܹܗ"
    assert fix_dots("ܝܺ") == "ܝܹ"


def test_macron_linea_only():
    # Targeted pass: ̄ → ݇; macron below and other marks stay.
    assert fix_macron_linea("ܕܐܲܢ̄ܬ݁ܘܼ") == "ܕܐܲܢ݇ܬ݁ܘܼ"
    assert fix_macron_linea("ܐܸܬ݂ܩ̄ܒܲܪ") == "ܐܸܬ݂ܩ݇ܒܲܪ"
    assert fix_macron_linea("ܐ̄ܪ̈ܙܐ") == "ܐ݇ܪ̈ܙܐ"
    assert fix_macron_linea("ܕܐܲܢ݇ܬ݁ܘܼ") == "ܕܐܲܢ݇ܬ݁ܘܼ"
    assert fix_macron_linea("ܐ̄݇ܪ̈ܙܐ") == "ܐ݇ܪ̈ܙܐ"  # collapse duplicate
    assert fix_macron_linea("ܚ̱ܢܲܢ") == "ܚ̱ܢܲܢ"
    assert "݇" not in fix_macron_linea("ܚ̱ܢܲܢ")
    assert fix_dots("ܕܐܲܢ̄ܬ݁ܘܼ") == "ܕܐܲܢ݇ܬ݁ܘܼ"
    assert fix_dots("ܗ̄ܘܼܵܘ") == "ܗ݇ܘ̣ܵܘ"


def test_ayt_hbasa_only():
    # Targeted pass: drop ܼ on yodh only in ܲܝܼܬ; real /i/ stays.
    assert fix_ayt_hbasa("ܕܲܒ݂ܪܲܝܼܬ݁") == "ܕܲܒ݂ܪܲܝܬ݁"
    assert fix_ayt_hbasa("ܒܪܲܝܼܬ݁") == "ܒܪܲܝܬ݁"
    assert fix_ayt_hbasa("ܗܘܲܝܼܬ݁ܘܿܢ") == "ܗܘܲܝܬ݁ܘܿܢ"
    assert fix_ayt_hbasa("ܐܲܝܼܬ݁ܝܼ") == "ܐܲܝܬ݁ܝܼ"
    assert fix_ayt_hbasa("ܒܪܝܼܬ݂ܵܐ") == "ܒܪܝܼܬ݂ܵܐ"
    assert fix_ayt_hbasa("ܐܝܼܬ݂") == "ܐܝܼܬ݂"
    assert fix_ayt_hbasa("ܩܲܕܝܼܫܵܐ") == "ܩܲܕܝܼܫܵܐ"
    assert fix_ayt_hbasa("ܒܹܝܼܬ݂") == "ܒܹܝܼܬ݂"
    assert fix_ayt_hbasa("ܕܲܒ݂ܪܲܝܬ݁") == "ܕܲܒ݂ܪܲܝܬ݁"
    assert fix_dots("ܕܲܒ݂ܪܲܝܼܬ݁") == "ܕܲܒ݂ܪܲܝܬ݁"


def test_min_rukkakha_only():
    assert fix_min_rukkakha("ܡ݂ܢ ܫܡܲܝܵܐ") == "ܡ̣ܢ ܫܡܲܝܵܐ"
    assert fix_min_rukkakha("ܘܡ݂ܢ ܥܵܠܲܡ") == "ܘܡ̣ܢ ܥܵܠܲܡ"
    assert fix_min_rukkakha("ܕܡ݂ܢ ܩܕ݂ܝܼܡ") == "ܕܡ̣ܢ ܩܕ݂ܝܼܡ"
    assert fix_min_rukkakha("ܘܲܕ݂ܡ݂ܢ ܥܵܠܲܡ") == "ܘܲܕ݂ܡ̣ܢ ܥܵܠܲܡ"
    assert fix_min_rukkakha("ܡܢ݂ ܫܡܲܝܵܐ") == "ܡ̣ܢ ܫܡܲܝܵܐ"
    assert fix_min_rukkakha("ܡܢ ܒܝܼܫܵܐ") == "ܡܢ ܒܝܼܫܵܐ"
    assert fix_min_rukkakha("ܠܡ݂ܢ") == "ܠܡ݂ܢ"
    assert fix_min_rukkakha("ܣܵܡ݂ ܥܲܠ") == "ܣܵܡ݂ ܥܲܠ"
    assert fix_min_rukkakha("ܡ̣ܢ ܟܠ") == "ܡ̣ܢ ܟܠ"


def test_min_zlama_only():
    assert fix_min_zlama("ܡܸܢ ܒܝܼܫܵܐ") == "ܡ̣ܢ ܒܝܼܫܵܐ"
    assert fix_min_zlama("ܘܡܸܢ ܥܵܠܲܡ") == "ܘܡ̣ܢ ܥܵܠܲܡ"
    assert fix_min_zlama("ܕܡܸܢ ܩܕ݂ܝܼܡ") == "ܕܡ̣ܢ ܩܕ݂ܝܼܡ"
    assert fix_min_zlama("ܡܸܢܝ") == "ܡܸܢܝ"
    assert fix_min_zlama("ܡܸܢܹܗ") == "ܡܸܢܹܗ"
    assert fix_min_zlama("ܡܸܢܗܘܿܢ") == "ܡܸܢܗܘܿܢ"
    assert fix_min_zlama("ܗܲܝܡܸܢ") == "ܗܲܝܡܸܢ"
    assert fix_min_zlama("ܡܢ ܒܝܼܫܵܐ") == "ܡܢ ܒܝܼܫܵܐ"
    assert fix_min_zlama("ܡ̣ܢ ܟܠ") == "ܡ̣ܢ ܟܠ"


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
    test_hbasa_rukkakha_only()
    test_rwaha_qushshaya_only()
    test_dot_above_qushshaya_only()
    test_stacked_hbasa_dot_below_only()
    test_hbasa_above_dot_only()
    test_macron_linea_only()
    test_ayt_hbasa_only()
    test_min_rukkakha_only()
    test_min_zlama_only()
    print("ok")
