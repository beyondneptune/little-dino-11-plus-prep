#!/usr/bin/env python3
"""Dual-method verifier for the Level 3–5 maths generators (scripts/maths_l35.py).

An item is accepted ONLY if, independently of the generator:
  1. the FORWARD solver re-derives the marked answer from the stem, AND
  2. a DIFFERENT-METHOD cross-check (reverse calculation or a second solver with
     different logic) also passes, AND
  3. the options are 4 distinct values and the marked option is the unique match.

Two agreeing-by-construction solvers could share a bug; requiring a second,
structurally different method makes a silent wrong key far less likely. Used by
build_l35.py (bank build) and tests/test_*_l35 (metamorphic + mutation + golden).
"""
from __future__ import annotations

import random
from fractions import Fraction

import maths_l35 as L


def verify(type_name, it) -> tuple[bool, str]:
    gen, solve, check, _ = L.TYPES[type_name]
    stem, ans = it["question"], Fraction(it["answer"])
    opts = it["options"]
    if len(opts) != 4 or len({o.strip() for o in opts}) != 4:
        return False, "options not 4 distinct"
    # marked option must render the answer, and be the unique numeric match
    matches = [i for i, o in enumerate(opts) if L.num(o) == ans]
    if matches != [it["answer_index"]]:
        return False, f"marked {it['answer_index']} but numeric matches {matches}"
    a = solve(stem)                                   # method A: forward solver
    if a is None:
        return False, "forward solver could not parse"
    if Fraction(a) != ans:
        return False, f"forward solver got {a}, marked {ans}"
    if not check(stem, ans):                          # method B: different method
        return False, "cross-check (different method) failed"
    # the different method must also REJECT a deliberately wrong answer
    if check(stem, ans + 1):
        return False, "cross-check accepts a wrong answer (too weak)"
    return True, "ok"


def build(type_name, level, target=60, seed=0):
    gen, solve, check, levels = L.TYPES[type_name]
    assert level in levels, f"{type_name} has no level {level}"
    rng = random.Random((hash((type_name, level)) ^ seed) & 0xFFFFFFFF)
    out, seen, scanned = [], set(), 0
    while len(out) < target and scanned < target * 120:
        scanned += 1
        it = gen(rng, level)
        if it is None:
            continue
        ok, _ = verify(type_name, it)
        if not ok:
            continue
        if it["question"] in seen:
            continue
        seen.add(it["question"])
        out.append(it)
    return out


if __name__ == "__main__":
    for name, (_, _, _, levels) in L.TYPES.items():
        for lv in levels:
            bank = build(name, lv, target=40)
            print(f"{name:16} L{lv}: {len(bank):3} verified")
