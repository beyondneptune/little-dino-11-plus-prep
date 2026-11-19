#!/usr/bin/env python3
"""Multi-step 11+ Maths generators (Levels 3–5) with DUAL verification.

Each item type provides three deliberately-separate pieces of logic:
  * generate(rng, level) -> item          (builds the stem + options + answer)
  * solve(stem)          -> Fraction|None (FORWARD independent solver; parses the
                                           rendered stem, no shared code with gen)
  * crosscheck(stem, ans)-> bool          (a DIFFERENT method: reverse calculation
                                           or a second solver with different logic)

The verifier (scripts/verify2.py) accepts an item only if BOTH the forward solver
agrees AND the different-method cross-check passes — the mitigation for the shared
generator/solver blind spot. Distractors come from NAMED slips, so each wrong
option can be explained.

No past-paper text is reproduced; difficulty is calibrated in
content/levels/maths_levels.md.
"""
from __future__ import annotations

import math
import re
from fractions import Fraction


# ---- rendering + option helpers ---------------------------------------------
def money(x) -> str:
    return f"£{float(Fraction(x)):.2f}"


def plain(x) -> str:
    f = Fraction(x)
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def num(s: str):
    """Parse a rendered option back to a Fraction (money, fraction, int)."""
    t = s.strip().replace("£", "").replace(",", "")
    try:
        return Fraction(t)
    except (ValueError, ZeroDivisionError):
        return None


def mcq(ans, slips, render):
    """Build 4 distinct options from the answer + named slips.
    `slips` is a list of (value, reason); returns (options, answer_index, reasons)."""
    seen = {render(ans)}
    opts = [(render(ans), None)]
    for val, reason in slips:
        r = render(val)
        if r not in seen and val is not None and (isinstance(val, Fraction) or val == val):
            seen.add(r)
            opts.append((r, reason))
        if len(opts) == 4:
            break
    if len(opts) < 4:
        return None
    # deterministic-but-mixed order via the answer's hash is avoided; caller shuffles
    return opts


# =========================================================================
# ITEM TYPES
# Each: generate(rng, level) -> item | None ; solve(stem) ; crosscheck(stem, ans)
# =========================================================================

# ---- 1) two/three-step BODMAS (bare calculation) ----------------------------
def gen_bodmas(rng, level):
    a = rng.randint(3, 9 if level == 3 else 12)
    b = rng.randint(3, 9 if level == 3 else 12)
    c = rng.randint(2, 20 if level == 3 else 40)
    if level == 3:
        stem = f"Work out {a} × {b} − {c}."
        ans = a * b - c
        slips = [(a * (b - c), "subtracted before multiplying"),
                 (a * b + c, "added instead of subtracting"),
                 (a * b - c - 1, "made a small slip")]
    elif level == 4:
        d = rng.choice([2, 3, 4, 5])
        c = d * rng.randint(2, 8)                    # make c ÷ d exact
        stem = f"Work out {a} × {b} + {c} ÷ {d}."
        ans = a * b + Fraction(c, d)
        slips = [(Fraction((a * b + c), d), "divided the whole thing instead of just the last part"),
                 (a * b + c, "forgot to do the dividing"),
                 (a * b + Fraction(c, d) + 1, "made a small slip")]
    else:
        d = rng.choice([2, 3, 4, 5])
        c = d * rng.randint(2, 9)
        e = rng.randint(2, 9)
        stem = f"Work out ({a} + {b}) × {e} − {c} ÷ {d}."
        ans = (a + b) * e - Fraction(c, d)
        slips = [((a + b) * e - c, "forgot to divide the last part"),
                 (a + b * e - Fraction(c, d), "ignored the brackets"),
                 ((a + b) * e - Fraction(c, d) + 1, "made a small slip")]
    return _finish(stem, ans, slips, f"Work left to right using BODMAS: {stem[9:-1]} = {plain(ans)}.")


def solve_bodmas(stem):
    m = re.fullmatch(r"Work out (.+)\.", stem)
    if not m:
        return None
    expr = m.group(1).replace("×", "*").replace("÷", "/").replace("−", "-")
    if not re.fullmatch(r"[0-9+\-*/() ]+", expr):
        return None
    try:
        # method A: evaluate with Fraction arithmetic (Python precedence)
        return eval(expr, {"__builtins__": {}}, {})  # noqa: S307 - sanitised numeric only
    except Exception:
        return None


def _shunting_eval(expr):
    """Method B: explicit shunting-yard evaluation (different code path)."""
    toks = re.findall(r"\d+|[+\-*/()]", expr)
    prec = {"+": 1, "-": 1, "*": 2, "/": 2}
    out, ops = [], []
    def apply():
        b, a, op = out.pop(), out.pop(), ops.pop()
        out.append(a + b if op == "+" else a - b if op == "-" else a * b if op == "*" else Fraction(a, b))
    for t in toks:
        if t.isdigit():
            out.append(Fraction(int(t)))
        elif t == "(":
            ops.append(t)
        elif t == ")":
            while ops and ops[-1] != "(":
                apply()
            ops.pop()
        else:
            while ops and ops[-1] != "(" and prec[ops[-1]] >= prec[t]:
                apply()
            ops.append(t)
    while ops:
        apply()
    return out[0]


def check_bodmas(stem, ans):
    m = re.fullmatch(r"Work out (.+)\.", stem)
    if not m:
        return False
    expr = m.group(1).replace("×", "*").replace("÷", "/").replace("−", "-")
    try:
        return _shunting_eval(expr) == Fraction(ans)
    except Exception:
        return False


# ---- 2) money change (two-step word problem) --------------------------------
_NAMES = ["Priya", "Sam", "Mia", "Leo", "Ava", "Noah", "Zara", "Kai"]
_ITEMS = ["pencils", "stickers", "apples", "badges", "cards", "rulers"]


def gen_money(rng, level):
    name = rng.choice(_NAMES)
    item = rng.choice(_ITEMS)
    n = rng.randint(3, 6 if level == 3 else 9)
    pence = rng.randint(20, 95)
    price = Fraction(pence, 100)
    note = rng.choice([5, 10] if level == 3 else [10, 20])
    total = n * price
    if total >= note:
        return None
    ans = note - total
    stem = (f"{name} buys {n} {item} at {money(price)} each and pays with a {money(note)} note. "
            f"How much change should {name} get?")
    slips = [(total, "gave the cost, not the change"),
             (note - price, "paid for only one item"),
             (note - n * price - Fraction(10, 100), "made a 10p slip")]
    return _finish(stem, ans, slips,
                   f"{n} × {money(price)} = {money(total)}; {money(note)} − {money(total)} = {money(ans)}.")


def solve_money(stem):
    m = re.fullmatch(r".+ buys (\d+) \w+ at £(\d+\.\d\d) each and pays with a £(\d+\.\d\d) note\. "
                     r"How much change should \w+ get\?", stem)
    if not m:
        return None
    n = int(m.group(1))
    price = Fraction(m.group(2)).limit_denominator(100)
    note = Fraction(m.group(3)).limit_denominator(100)
    return note - n * price


def check_money(stem, ans):
    # method B: reverse — change + total paid for items must equal the note
    m = re.fullmatch(r".+ buys (\d+) \w+ at £(\d+\.\d\d) each and pays with a £(\d+\.\d\d) note\. .+", stem)
    if not m:
        return False
    n, price, note = int(m.group(1)), Fraction(m.group(2)), Fraction(m.group(3))
    return Fraction(ans) + n * price == note and Fraction(ans) >= 0


# ---- 3) fraction of an amount, then a second step ---------------------------
def gen_fraction_then(rng, level):
    den = rng.choice([2, 3, 4, 5] if level == 3 else [3, 4, 5, 6, 8])
    numr = rng.randint(1, den - 1)
    whole = den * rng.randint(4, 12)
    part = Fraction(numr, den) * whole
    add = rng.randint(3, 20)
    op = rng.choice(["add", "sub"]) if level >= 4 else "add"
    if op == "sub" and add > part:
        add = int(part) - 1
    ans = part + add if op == "add" else part - add
    word = "add" if op == "add" else "subtract"
    stem = f"Work out {numr}/{den} of {whole}, then {word} {add}."
    slips = [(Fraction(numr, den) * whole, "stopped after the fraction step"),
             (whole // den + add, "used one part instead of the right number of parts"),
             (ans + 1, "made a small slip")]
    return _finish(stem, ans, slips,
                   f"{numr}/{den} of {whole} = {plain(part)}; {plain(part)} {'+' if op == 'add' else '−'} {add} = {plain(ans)}.")


def solve_fraction_then(stem):
    m = re.fullmatch(r"Work out (\d+)/(\d+) of (\d+), then (add|subtract) (\d+)\.", stem)
    if not m:
        return None
    numr, den, whole, word, add = int(m[1]), int(m[2]), int(m[3]), m[4], int(m[5])
    part = Fraction(numr, den) * whole
    return part + add if word == "add" else part - add


def check_fraction_then(stem, ans):
    # method B: undo the second step, then multiply back up by the fraction's inverse
    m = re.fullmatch(r"Work out (\d+)/(\d+) of (\d+), then (add|subtract) (\d+)\.", stem)
    if not m:
        return False
    numr, den, whole, word, add = int(m[1]), int(m[2]), int(m[3]), m[4], int(m[5])
    part = Fraction(ans) - add if word == "add" else Fraction(ans) + add   # reverse step 2
    return part * den == numr * whole                                      # reverse step 1


# ---- 4) percentage reduction, then a further reduction ----------------------
def gen_percent_multi(rng, level):
    price = rng.randint(20, 80) if level == 4 else rng.randint(40, 200)
    pct = rng.choice([10, 20, 25, 50])
    after1 = Fraction(price) * (100 - pct) / 100
    extra = rng.choice([2, 3, 5]) if level == 4 else rng.choice([5, 8, 10])
    if extra >= after1:
        return None
    ans = after1 - extra
    stem = (f"A £{price} coat is reduced by {pct}% in a sale, then a further £{extra} is taken off. "
            f"What is the final price?")
    slips = [(after1, "forgot the extra £ off"),
             (Fraction(price) * pct / 100, "found the discount, not the price"),
             (Fraction(price) - extra, "forgot the percentage")]
    return _finish(stem, ans, slips,
                   f"{pct}% off £{price} → {money(after1)}; minus £{extra} → {money(ans)}.")


def solve_percent_multi(stem):
    m = re.fullmatch(r"A £(\d+) coat is reduced by (\d+)% in a sale, then a further £(\d+) is taken off\. "
                     r"What is the final price\?", stem)
    if not m:
        return None
    price, pct, extra = int(m[1]), int(m[2]), int(m[3])
    return Fraction(price) * (100 - pct) / 100 - extra


def check_percent_multi(stem, ans):
    # method B: reverse — add the £extra back, then undo the % to recover the price
    m = re.fullmatch(r"A £(\d+) coat is reduced by (\d+)% in a sale, then a further £(\d+) .+", stem)
    if not m:
        return False
    price, pct, extra = int(m[1]), int(m[2]), int(m[3])
    before_extra = Fraction(ans) + extra
    return before_extra * 100 == Fraction(price) * (100 - pct)


# ---- 5) work backwards (Level 5) --------------------------------------------
def gen_work_backwards(rng, level):
    d1 = rng.choice([2, 3, 4])
    d2 = rng.choice([2, 3, 4])
    # start S; spend 1/d1, then 1/d2 of the remainder; remainder R left
    keep = Fraction(d1 - 1, d1) * Fraction(d2 - 1, d2)
    unit = rng.randint(6, 20)
    start = unit * keep.denominator          # ensure integer start
    remainder = start * keep
    if remainder.denominator != 1 or remainder <= 0:
        return None
    ans = start
    stem = (f"A game has some coins. First {Fraction(1, d1)!s} of the coins are used, "
            f"then {Fraction(1, d2)!s} of what is left. "
            f"Now {int(remainder)} coins remain. How many coins were there at the start?")
    slips = [(int(remainder) * d1 * d2, "multiplied by both bottoms"),
             (int(remainder) + int(start - remainder) // 2, "only did part of the working"),
             (int(start) - 1, "made a small slip")]
    return _finish(stem, ans, slips,
                   f"Kept {keep!s} of the start; {int(remainder)} ÷ {keep!s} = {int(start)}.")


_FRAC_RE = r"(\d+)/(\d+)"


def solve_work_backwards(stem):
    m = re.fullmatch(rf"A game has some coins\. First {_FRAC_RE} of the coins are used, "
                     rf"then {_FRAC_RE} of what is left\. Now (\d+) coins remain\. .+", stem)
    if not m:
        return None
    d1, d2, rem = int(m[2]), int(m[4]), int(m[5])
    keep = Fraction(d1 - 1, d1) * Fraction(d2 - 1, d2)
    start = rem / keep
    return start if start.denominator == 1 else None


def check_work_backwards(stem, ans):
    # method B: simulate FORWARD from the proposed start and check the remainder
    m = re.fullmatch(rf"A game has some coins\. First {_FRAC_RE} of the coins are used, "
                     rf"then {_FRAC_RE} of what is left\. Now (\d+) coins remain\. .+", stem)
    if not m:
        return False
    d1, d2, rem = int(m[2]), int(m[4]), int(m[5])
    s = Fraction(ans)
    after1 = s - s / d1
    after2 = after1 - after1 / d2
    return after2 == rem


# ---- assembly ---------------------------------------------------------------
def _finish(stem, ans, slips, expl):
    import random as _r
    ans = Fraction(ans)
    render = money if "£" in stem else plain
    opts = mcq(ans, slips, render)
    if opts is None:
        return None
    _r.Random(hash(stem) & 0xFFFFFFFF).shuffle(opts)       # stable per-stem option order
    option_strs = [o[0] for o in opts]
    reasons = [o[1] for o in opts]
    return {"question": stem, "answer": ans, "options": option_strs,
            "answer_index": next(i for i, o in enumerate(opts) if o[1] is None),
            "explanation": expl,
            "distractor_explanations": reasons}


# ---- 6) estimate by rounding (MA-A05 L3-5) ----------------------------------
def _round_half_up(n, base):
    return (n + base // 2) // base * base


def gen_estimate(rng, level):
    if level == 3:
        a, b = rng.randint(120, 890), rng.randint(120, 890)
        op = rng.choice(["+", "−"])
        if op == "−" and b > a:
            a, b = b, a
        ra, rb = _round_half_up(a, 100), _round_half_up(b, 100)
        ans = ra + rb if op == "+" else ra - rb
        stem = f"Estimate {a} {op} {b} by rounding each number to the nearest 100."
        slips = [((a + b) if op == "+" else (a - b), "gave the exact answer, not the estimate"),
                 ((ra + rb + 100) if op == "+" else (ra - rb - 100), "rounded a number the wrong way"),
                 (ans + 100, "made a small slip")]
    elif level == 4:
        a, b = rng.randint(21, 89), rng.randint(21, 89)
        ra, rb = _round_half_up(a, 10), _round_half_up(b, 10)
        ans = ra * rb
        stem = f"Estimate {a} × {b} by rounding each number to the nearest 10."
        slips = [(a * b, "gave the exact answer, not the estimate"),
                 ((ra + 10) * rb, "rounded the first number the wrong way"),
                 (ans + 100, "made a small slip")]
    else:
        a, b, c = rng.randint(180, 820), rng.randint(180, 820), rng.randint(2, 9)
        ra, rb = _round_half_up(a, 100), _round_half_up(b, 100)
        ans = (ra + rb) * c
        stem = f"Estimate ({a} + {b}) × {c} by rounding {a} and {b} to the nearest 100."
        slips = [((a + b) * c, "gave the exact answer, not the estimate"),
                 (ra + rb * c, "ignored the brackets"),
                 (ans + 100, "made a small slip")]
    return _finish(stem, ans, slips, f"Round first, then calculate: the estimate is {plain(ans)}.")


def solve_estimate(stem):
    m = re.fullmatch(r"Estimate (\d+) ([+−]) (\d+) by rounding each number to the nearest 100\.", stem)
    if m:
        a, op, b = int(m[1]), m[2], int(m[3])
        ra, rb = _round_half_up(a, 100), _round_half_up(b, 100)
        return Fraction(ra + rb if op == "+" else ra - rb)
    m = re.fullmatch(r"Estimate (\d+) × (\d+) by rounding each number to the nearest 10\.", stem)
    if m:
        return Fraction(_round_half_up(int(m[1]), 10) * _round_half_up(int(m[2]), 10))
    m = re.fullmatch(r"Estimate \((\d+) \+ (\d+)\) × (\d+) by rounding \d+ and \d+ to the nearest 100\.", stem)
    if m:
        a, b, c = int(m[1]), int(m[2]), int(m[3])
        return Fraction((_round_half_up(a, 100) + _round_half_up(b, 100)) * c)
    return None


def check_estimate(stem, ans):
    def rnd(n, base):                          # method B: remainder-threshold rounding (different code)
        r = n % base
        return n - r if r < base / 2 else n - r + base
    m = re.fullmatch(r"Estimate (\d+) ([+−]) (\d+) by rounding each number to the nearest 100\.", stem)
    if m:
        a, op, b = int(m[1]), m[2], int(m[3])
        return Fraction(rnd(a, 100) + rnd(b, 100) if op == "+" else rnd(a, 100) - rnd(b, 100)) == Fraction(ans)
    m = re.fullmatch(r"Estimate (\d+) × (\d+) by rounding each number to the nearest 10\.", stem)
    if m:
        return Fraction(rnd(int(m[1]), 10) * rnd(int(m[2]), 10)) == Fraction(ans)
    m = re.fullmatch(r"Estimate \((\d+) \+ (\d+)\) × (\d+) by rounding \d+ and \d+ to the nearest 100\.", stem)
    if m:
        a, b, c = int(m[1]), int(m[2]), int(m[3])
        return Fraction((rnd(a, 100) + rnd(b, 100)) * c) == Fraction(ans)
    return False


# ---- 7) worded division (MA-B04 L3-5) ---------------------------------------
def gen_division_worded(rng, level):
    name, item = rng.choice(_NAMES), rng.choice(_ITEMS)
    if level == 3:
        g, each = rng.randint(3, 8), rng.randint(4, 12)
        n = g * each
        stem = f"{name} shares {n} {item} equally between {g} friends. How many does each friend get?"
        ans = each
        slips = [(n - g, "subtracted instead of dividing"), (each + 1, "made a small slip"),
                 (g, "gave the number of friends")]
    elif level == 4:
        g = rng.randint(3, 8)
        n = g * rng.randint(3, 9) + rng.randint(1, g - 1)
        stem = f"{name} puts {n} {item} into bags of {g}. How many are left over?"
        ans = n % g
        slips = [(n // g, "gave the number of full bags"), (g - (n % g), "took it away from the bag size"),
                 ((n % g) + 1, "made a small slip")]
    else:
        g, each = rng.randint(3, 6), rng.randint(6, 12)
        k = rng.randint(1, each - 2)
        n = g * each
        stem = (f"{name} shares {n} {item} equally between {g} friends, then each friend gives away "
                f"{k}. How many does each friend have left?")
        ans = each - k
        slips = [(each, "forgot the giving-away step"), (n // g - k - 1, "made a small slip"),
                 (n - g - k, "subtracted instead of dividing")]
    return _finish(stem, ans, slips, f"Divide, then finish the steps: the answer is {plain(ans)}.")


def solve_division_worded(stem):
    m = re.fullmatch(r".+ shares (\d+) \w+ equally between (\d+) friends\. How many does each friend get\?", stem)
    if m:
        return Fraction(int(m[1]), int(m[2]))
    m = re.fullmatch(r".+ puts (\d+) \w+ into bags of (\d+)\. How many are left over\?", stem)
    if m:
        return Fraction(int(m[1]) % int(m[2]))
    m = re.fullmatch(r".+ shares (\d+) \w+ equally between (\d+) friends, then each friend gives away (\d+)\. "
                     r"How many does each friend have left\?", stem)
    if m:
        return Fraction(int(m[1]), int(m[2])) - int(m[3])
    return None


def check_division_worded(stem, ans):
    # method B: reconstruct the total from the answer and check it matches
    m = re.fullmatch(r".+ shares (\d+) \w+ equally between (\d+) friends\. How many does each friend get\?", stem)
    if m:
        n, g = int(m[1]), int(m[2])
        return Fraction(ans) * g == n
    m = re.fullmatch(r".+ puts (\d+) \w+ into bags of (\d+)\. How many are left over\?", stem)
    if m:
        n, g = int(m[1]), int(m[2])
        return 0 <= ans < g and (n - ans) % g == 0
    m = re.fullmatch(r".+ shares (\d+) \w+ equally between (\d+) friends, then each friend gives away (\d+)\. .+", stem)
    if m:
        n, g, k = int(m[1]), int(m[2]), int(m[3])
        return (Fraction(ans) + k) * g == n
    return False


# ---- 8) two-step inverse / missing number (MA-B06 L3-4) ---------------------
def gen_two_step_inverse(rng, level):
    x = rng.randint(2, 9)
    a = rng.randint(2, 9)
    c = rng.randint(1, 20)
    if level == 3:
        b = a * x + c
        stem = f"What number goes in the box? {a} × ? + {c} = {b}"
    else:
        b = a * x - c if a * x > c else a * x + c
        if b == a * x + c:
            stem = f"What number goes in the box? {a} × ? + {c} = {b}"
        else:
            stem = f"What number goes in the box? {a} × ? − {c} = {b}"
    ans = x
    slips = [(x + 1, "made a small slip"),
             (max(1, x - 1), "made a small slip the other way"),
             (b // a, "forgot to take away before dividing"),
             (x + 2, "did a step out of order")]
    return _finish(stem, ans, slips, f"Undo each step with its inverse: the box is {plain(ans)}.")


def solve_two_step_inverse(stem):
    m = re.fullmatch(r"What number goes in the box\? (\d+) × \? ([+−]) (\d+) = (\d+)", stem)
    if m:
        a, op, c, b = int(m[1]), m[2], int(m[3]), int(m[4])
        rhs = (b - c) if op == "+" else (b + c)
        return Fraction(rhs, a) if a else None
    return None


def check_two_step_inverse(stem, ans):
    # method B: substitute the answer back into the original equation (forward)
    m = re.fullmatch(r"What number goes in the box\? (\d+) × \? ([+−]) (\d+) = (\d+)", stem)
    if m:
        a, op, c, b = int(m[1]), m[2], int(m[3]), int(m[4])
        lhs = a * Fraction(ans) + c if op == "+" else a * Fraction(ans) - c
        return lhs == b
    return False


# ---- 9) compare after calculating (MA-A03 L3-4) -----------------------------
def gen_compare_calc(rng, level):
    a, b = rng.randint(3, 12), rng.randint(3, 12)
    left = a * b
    if level == 3:
        c = left + rng.choice([-5, -3, -1, 1, 3, 5])
        if c <= 0 or c == left:
            return None
        stem = f"Which is larger: {a} × {b} or {c}? Give the larger value."
        right = c
    else:
        d, e = rng.randint(3, 12), rng.randint(3, 12)
        right = d * e
        if right == left:
            return None
        stem = f"Which is larger: {a} × {b} or {d} × {e}? Give the larger value."
    ans = max(left, right)
    slips = [(min(left, right), "gave the smaller value"), (left + right, "added them instead of comparing"),
             (ans + 1, "made a small slip")]
    return _finish(stem, ans, slips, f"Work out both, then pick the larger: {plain(ans)}.")


def solve_compare_calc(stem):
    m = re.fullmatch(r"Which is larger: (\d+) × (\d+) or (\d+)\? Give the larger value\.", stem)
    if m:
        return Fraction(max(int(m[1]) * int(m[2]), int(m[3])))
    m = re.fullmatch(r"Which is larger: (\d+) × (\d+) or (\d+) × (\d+)\? Give the larger value\.", stem)
    if m:
        return Fraction(max(int(m[1]) * int(m[2]), int(m[3]) * int(m[4])))
    return None


def check_compare_calc(stem, ans):
    # method B: the answer must equal one side AND be >= both sides (not a recompute of max)
    m = re.fullmatch(r"Which is larger: (\d+) × (\d+) or (\d+)\? .+", stem)
    if m:
        sides = {int(m[1]) * int(m[2]), int(m[3])}
    else:
        m = re.fullmatch(r"Which is larger: (\d+) × (\d+) or (\d+) × (\d+)\? .+", stem)
        if not m:
            return False
        sides = {int(m[1]) * int(m[2]), int(m[3]) * int(m[4])}
    v = Fraction(ans)
    return v in sides and all(v >= s for s in sides)


# ---- 10) lowest common multiple / highest common factor (MA-B13 L3-4) -------
def gen_lcm_hcf(rng, level):
    if level == 3:
        a, b = rng.randint(2, 8), rng.randint(2, 9)
        ans = a * b // math.gcd(a, b)
        stem = f"What is the lowest common multiple of {a} and {b}?"
        slips = [(a * b, "multiplied them without simplifying"), (ans + a, "made a small slip"),
                 (abs(a - b) or a + 1, "subtracted them")]
    else:
        k = rng.randint(2, 6)
        a, b = k * rng.randint(2, 6), k * rng.randint(2, 6)
        if a == b:
            return None
        ans = math.gcd(a, b)
        stem = f"What is the highest common factor of {a} and {b}?"
        slips = [(min(a, b), "gave the smaller number"), (ans + 1, "made a small slip"),
                 (a * b, "multiplied them")]
    return _finish(stem, ans, slips,
                   f"List the {'multiples' if level == 3 else 'factors'} of each and find the common one: {plain(ans)}.")


def solve_lcm_hcf(stem):
    m = re.fullmatch(r"What is the lowest common multiple of (\d+) and (\d+)\?", stem)
    if m:
        a, b = int(m[1]), int(m[2])
        return Fraction(a * b // math.gcd(a, b))
    m = re.fullmatch(r"What is the highest common factor of (\d+) and (\d+)\?", stem)
    if m:
        return Fraction(math.gcd(int(m[1]), int(m[2])))
    return None


def check_lcm_hcf(stem, ans):
    v = int(Fraction(ans))
    m = re.fullmatch(r"What is the lowest common multiple of (\d+) and (\d+)\?", stem)
    if m:                                  # method B: v divisible by both, and the SMALLEST such
        a, b = int(m[1]), int(m[2])
        return v > 0 and v % a == 0 and v % b == 0 and all(k % a or k % b for k in range(1, v))
    m = re.fullmatch(r"What is the highest common factor of (\d+) and (\d+)\?", stem)
    if m:                                  # method B: v divides both, and the LARGEST such
        a, b = int(m[1]), int(m[2])
        return v > 0 and a % v == 0 and b % v == 0 and all(a % k or b % k for k in range(v + 1, min(a, b) + 1))
    return False


TYPES = {
    "bodmas":          (gen_bodmas, solve_bodmas, check_bodmas, [3, 4, 5]),
    "compare_calc":    (gen_compare_calc, solve_compare_calc, check_compare_calc, [3, 4]),
    "lcm_hcf":         (gen_lcm_hcf, solve_lcm_hcf, check_lcm_hcf, [3, 4]),
    "money_change":    (gen_money, solve_money, check_money, [3, 4]),
    "fraction_then":   (gen_fraction_then, solve_fraction_then, check_fraction_then, [3, 4]),
    "percent_multi":   (gen_percent_multi, solve_percent_multi, check_percent_multi, [4, 5]),
    "work_backwards":  (gen_work_backwards, solve_work_backwards, check_work_backwards, [5]),
    "estimate":        (gen_estimate, solve_estimate, check_estimate, [3, 4, 5]),
    "division_worded": (gen_division_worded, solve_division_worded, check_division_worded, [3, 4, 5]),
    "two_step_inverse": (gen_two_step_inverse, solve_two_step_inverse, check_two_step_inverse, [3, 4]),
}
