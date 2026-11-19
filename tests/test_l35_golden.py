"""Golden known-answer tests for Level 3–5 maths, using canonical 11+ question
PATTERNS (not copied past-paper text) whose answers are known by hand. Both
independent methods must agree with the hand answer."""
from fractions import Fraction

import maths_l35 as L


def _assert(type_name, stem, expected):
    _, solve, check, _ = L.TYPES[type_name]
    exp = Fraction(expected)
    assert solve(stem) == exp, f"{stem!r}: forward solver != {expected}"
    assert check(stem, exp), f"{stem!r}: cross-check failed"
    assert not check(stem, exp + 1), f"{stem!r}: cross-check too weak"


def test_golden_bodmas():
    _assert("bodmas", "Work out 7 × 8 − 15.", 41)              # ×  before −
    _assert("bodmas", "Work out 9 × 6 + 12 ÷ 4.", 57)          # ÷ before +
    _assert("bodmas", "Work out (4 + 5) × 3 − 8 ÷ 2.", 23)     # brackets first


def test_golden_money_change():
    _assert("money_change",
            "Priya buys 6 pencils at £0.45 each and pays with a £5.00 note. How much change should Priya get?",
            Fraction("2.30"))
    _assert("money_change",
            "Sam buys 4 apples at £0.75 each and pays with a £10.00 note. How much change should Sam get?",
            Fraction("7.00"))


def test_golden_fraction_then():
    _assert("fraction_then", "Work out 3/4 of 48, then add 9.", 45)
    _assert("fraction_then", "Work out 2/3 of 60, then subtract 12.", 28)


def test_golden_percent_multi():
    _assert("percent_multi",
            "A £60 coat is reduced by 25% in a sale, then a further £5 is taken off. What is the final price?",
            Fraction("40.00"))
    _assert("percent_multi",
            "A £80 coat is reduced by 10% in a sale, then a further £8 is taken off. What is the final price?",
            Fraction("64.00"))


def test_golden_estimate():
    _assert("estimate", "Estimate 312 + 589 by rounding each number to the nearest 100.", 900)
    _assert("estimate", "Estimate 48 × 21 by rounding each number to the nearest 10.", 1000)
    _assert("estimate", "Estimate (180 + 220) × 3 by rounding 180 and 220 to the nearest 100.", 1200)


def test_golden_division_worded():
    _assert("division_worded",
            "Priya shares 24 apples equally between 6 friends. How many does each friend get?", 4)
    _assert("division_worded",
            "Sam puts 29 cards into bags of 5. How many are left over?", 4)


def test_golden_two_step_inverse():
    _assert("two_step_inverse", "What number goes in the box? 7 × ? + 5 = 40", 5)
    _assert("two_step_inverse", "What number goes in the box? 6 × ? − 4 = 20", 4)


def test_golden_compare_calc():
    _assert("compare_calc", "Which is larger: 7 × 8 or 55? Give the larger value.", 56)
    _assert("compare_calc", "Which is larger: 6 × 6 or 5 × 9? Give the larger value.", 45)


def test_golden_lcm_hcf():
    _assert("lcm_hcf", "What is the lowest common multiple of 4 and 6?", 12)
    _assert("lcm_hcf", "What is the highest common factor of 12 and 18?", 6)


def test_golden_work_backwards():
    # 1/3 used -> 2/3 left; 1/4 of that used -> 3/4 * 2/3 = 1/2 left; 36 remain -> start 72
    _assert("work_backwards",
            "A game has some coins. First 1/3 of the coins are used, then 1/4 of what is left. "
            "Now 36 coins remain. How many coins were there at the start?",
            72)
