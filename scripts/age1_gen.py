#!/usr/bin/env python3
"""
Level-aware Age-1 computable generators. Each returns (question, answer, wrongs,
explanation); the registry wraps them with mcq to build options and the
INDEPENDENT solver (testers.solve_maths) re-derives the answer.

Levels here are FOUNDATION only (1-2, single-step). Multi-step 11+ levels (3-5)
are not claimed until built and verified (spec section 6 / parent STEP 1f).

Topic homes (checked by the registry's stem patterns and the audit test):
  g_mental_single -> MA-B01 (mental +,-,x,/ ; a single two-operand operation —
                     NOT a x b +- c, which is order of operations = MA-B05)
  g_round         -> MA-A05 (round to nearest 10 at L1, nearest 100 at L2)
  g_div_fact      -> MA-B04 (division facts from the times tables)
"""
from __future__ import annotations

MINUS = "−"   # − matches the project's maths typography
TIMES = "×"   # ×
DIV = "÷"     # ÷


def g_mental_single(rng, level=1):
    op = rng.choice(["+", MINUS, TIMES, DIV])
    if op == "+":
        (a, b) = (rng.randint(10, 49), rng.randint(10, 49)) if level == 1 \
            else (rng.randint(100, 499), rng.randint(100, 499))
        ans = a + b
        wrongs = [a + b + 10, abs(a - b), ans + 1, ans - 10]
        expl = f"Add: {a} + {b} = {ans}."
    elif op == MINUS:
        if level == 1:
            a = rng.randint(20, 99); b = rng.randint(5, a - 1)
        else:
            a = rng.randint(200, 900); b = rng.randint(50, a - 1)
        ans = a - b
        wrongs = [a + b, ans + 1, ans + 10, ans - 1]
        expl = f"Take away: {a} {MINUS} {b} = {ans}."
    elif op == TIMES:
        (a, b) = (rng.randint(2, 9), rng.randint(2, 9)) if level == 1 \
            else (rng.randint(2, 12), rng.randint(6, 12))
        ans = a * b
        wrongs = [a * b + a, a * b - b, a + b, a * b + b]
        expl = f"Multiply: {a} {TIMES} {b} = {ans}."
    else:  # division fact
        if level == 1:
            b = rng.randint(2, 9); q = rng.randint(2, 9)
        else:
            b = rng.randint(3, 12); q = rng.randint(6, 12)
        a = b * q; ans = q
        wrongs = [q + 1, q - 1, a - b, q + 2]
        expl = f"Divide: {b} {TIMES} {ans} = {a}, so {a} {DIV} {b} = {ans}."
    return f"Work out {a} {op} {b}", ans, [w for w in wrongs if w > 0], expl


def g_round(rng, level=1):
    base = 10 if level == 1 else 100
    n = rng.randint(base + 1, 99 * base // 10 + base)   # a few digits above base
    ans = (n + base // 2) // base * base                # round half up (school rule)
    expl = (f"Look at the {'ones' if base == 10 else 'tens'} digit of {n}; "
            f"{n} rounds to {ans} (nearest {base}).")
    wrongs = [ans + base, ans - base, (n // base) * base, n]
    return f"Round {n} to the nearest {base}.", ans, [w for w in wrongs if w > 0], expl


def g_div_fact(rng, level=1):
    if level == 1:
        b = rng.randint(2, 9); q = rng.randint(2, 9)
    else:
        b = rng.randint(3, 12); q = rng.randint(6, 12)
    a = b * q
    expl = f"{b} {TIMES} {q} = {a}, so {a} {DIV} {b} = {q}."
    wrongs = [q + 1, q - 1, a - b, q + 2]
    return f"Work out {a} {DIV} {b}", q, [w for w in wrongs if w > 0], expl
