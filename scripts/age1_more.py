#!/usr/bin/env python3
"""Additional Age-1 computable Maths generators (parent STEP 3 expansion).

Each generator returns (question, answer, wrongs, explanation) in the leveled
style used by registry._maths_leveled; the INDEPENDENT solver in testers.py
re-derives the answer from the stem, so every served item is verified. These add
Age-1 topics that previously had no generator: comparing/ordering integers,
number properties (odd/even/multiples), Roman numerals, and missing numbers
(inverse operations). Levels: 1 = foundation, 2 = larger numbers / wider range.
"""
from __future__ import annotations

_ROMAN = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
          (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]


def to_roman(n: int) -> str:
    out = ""
    for v, s in _ROMAN:
        while n >= v:
            out += s
            n -= v
    return out


def roman_to_int(s: str) -> int:
    vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = prev = 0
    for ch in reversed(s):
        v = vals[ch]
        total += -v if v < prev else v
        prev = v if v >= prev else prev
    return total


def _distinct_wrongs(rng, ans, lo, hi, n=3, span=6):
    wrongs = set()
    guard = 0
    while len(wrongs) < n and guard < 400:
        guard += 1
        w = ans + rng.randint(-span, span)
        if lo <= w <= hi and w != ans:
            wrongs.add(w)
    return [str(w) for w in wrongs] if len(wrongs) == n else None


# MA-A03 — comparing and ordering integers
def g_compare(rng, level):
    hi = 99 if level <= 1 else 9999
    nums = rng.sample(range(10, hi), 4)
    want = rng.choice(["largest", "smallest"])
    ans = max(nums) if want == "largest" else min(nums)
    wrongs = [str(n) for n in nums if n != ans]
    q = f"Which of these numbers is the {want}?"
    expl = f"Compare the numbers place by place; {ans} is the {want}."
    return q, str(ans), wrongs, expl


# MA-B13 — number properties (odd / even / multiples)
def g_parity(rng, level):
    kind = rng.choice(["even", "odd", "mult", "mult"])
    hi = 50 if level <= 1 else 200
    if kind in ("even", "odd"):
        par = 0 if kind == "even" else 1
        ans = rng.randrange(10, hi)
        if ans % 2 != par:
            ans += 1
        wrongs = set()
        while len(wrongs) < 3:
            w = rng.randrange(10, hi + 1)
            if w % 2 != par and w != ans:
                wrongs.add(w)
        q = f"Which of these is an {kind} number?"
        expl = f"{ans} is {kind} because its last digit is {'0, 2, 4, 6 or 8' if par == 0 else '1, 3, 5, 7 or 9'}."
        return q, str(ans), [str(w) for w in wrongs], expl
    k = rng.choice([3, 4, 5, 10])
    ans = rng.randint(2, max(3, hi // k)) * k
    wrongs = set()
    while len(wrongs) < 3:
        w = rng.randrange(10, hi + 1)
        if w % k != 0 and w != ans:
            wrongs.add(w)
    q = f"Which of these is a multiple of {k}?"
    expl = f"{ans} = {ans // k} × {k}, so it is a multiple of {k}."
    return q, str(ans), [str(w) for w in wrongs], expl


# MA-A07 — Roman numerals
def g_roman(rng, level):
    n = rng.randint(1, 49) if level <= 1 else rng.randint(40, 1000)
    wrongs = _distinct_wrongs(rng, n, 1, 3000, span=max(3, n // 8 + 4))
    if wrongs is None:
        return None
    q = f"What number does the Roman numeral {to_roman(n)} represent?"
    return q, str(n), wrongs, f"{to_roman(n)} = {n}."


# MA-B06 — missing number (inverse operations)
def g_missing(rng, level):
    hi = 10 if level <= 1 else 12
    form = rng.choice(["mul", "div", "add"])
    if form == "mul":
        a, x = rng.randint(2, hi), rng.randint(2, hi)
        q, ans = f"What number goes in the box? {a} × ? = {a * x}", x
    elif form == "div":
        x, b = rng.randint(2, hi), rng.randint(2, 9)
        q, ans = f"What number goes in the box? {x * b} ÷ ? = {b}", x
    else:
        a, x = rng.randint(5, 40 if level <= 1 else 90), rng.randint(5, 40 if level <= 1 else 90)
        q, ans = f"What number goes in the box? {a} + ? = {a + x}", x
    wrongs = _distinct_wrongs(rng, ans, 1, 200, span=4)
    if wrongs is None:
        return None
    return q, str(ans), wrongs, f"Use the inverse operation; the missing number is {ans}."
