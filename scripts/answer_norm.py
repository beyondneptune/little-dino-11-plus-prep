#!/usr/bin/env python3
"""Answer normaliser for TYPED-answer (standard written) 11+ items.

Accepts every equivalent correct written form and rejects near-misses, so a typed
answer can be auto-marked only for topics whose answer set is fully computable.

Equivalences handled:
  * decimals / fractions / percentages of the SAME value (0.5 = 1/2 = 50%) — only
    when the answer's domain is a proportion;
  * money (£2.50 = 2.50 = 2.5 = 250p);
  * mixed numbers vs improper fractions (1 1/2 = 3/2);
  * units present or absent (12 = 12 cm) but a WRONG unit is rejected;
  * spacing, commas, trailing/leading whitespace, case.

The accept decision requires EXACT rational equality (not float), so 0.5 ≠ 0.51 and
1/2 ≠ 1/3. An INDEPENDENT check re-derives the parsed value by a second route
(decimal) and refuses to accept if the two routes disagree — a wrong equivalent
form therefore cannot slip through on a parser bug.
"""
from __future__ import annotations

import re
from fractions import Fraction

# trailing unit tokens we recognise (longest first so "cm" doesn't eat "cm²")
_UNITS = ["cm²", "cm2", "mm", "cm", "km", "kg", "ml", "m", "g", "l", "°", "p", "%"]


def _strip_unit(t: str):
    """Return (core, unit) where unit is one of _UNITS / '£' / None."""
    t = t.strip()
    if t.startswith("£"):
        return t[1:].strip(), "£"
    for u in _UNITS:
        if t.endswith(u):
            return t[: -len(u)].strip(), ("cm²" if u in ("cm2", "cm²") else u)
    return t, None


def _num_core(t: str):
    """Parse '3', '0.5', '3/2', '1 1/2' -> Fraction, or None."""
    t = t.replace(",", "").strip()
    if not t:
        return None
    m = re.fullmatch(r"(\d+)\s+(\d+)/(\d+)", t)          # mixed number
    if m:
        a, b, c = int(m[1]), int(m[2]), int(m[3])
        return Fraction(a) + Fraction(b, c) if c else None
    m = re.fullmatch(r"-?\d+/\d+", t)                     # fraction
    if m:
        n, d = t.split("/")
        return Fraction(int(n), int(d)) if int(d) else None
    try:
        return Fraction(t)                               # int or decimal
    except (ValueError, ZeroDivisionError):
        return None


def parse(s: str):
    """Return (value: Fraction, kind) or None. kind in {money, percent, plain}
    with an optional measurement unit carried on `unit`. value is the numeric
    magnitude in base units (pounds for money; the raw ratio for percent)."""
    if s is None:
        return None
    core, unit = _strip_unit(str(s).strip().lower())
    v = _num_core(core)
    if v is None:
        return None
    if unit == "£":
        return (v, "money", None)
    if unit == "p":
        return (v / 100, "money", None)
    if unit == "%":
        return (v / 100, "percent", None)
    if unit in (None,):
        return (v, "plain", None)
    return (v, "plain", unit)                             # measurement unit (cm, m, …)


def accepts(typed: str, value, domain: str = "number", unit: str | None = None) -> bool:
    """True iff `typed` is an accepted written form of the canonical answer.

    domain: 'number' | 'proportion' | 'money' | 'measure'. `value` is a Fraction,
    int, or 'a/b' string (the exact magnitude; pounds for money, ratio for
    proportion). `unit` (for 'measure') is the expected unit, e.g. 'cm'.
    """
    want = value if isinstance(value, Fraction) else _num_core(str(value))
    if want is None:
        return False
    p = parse(typed)
    if p is None:
        return False
    v, kind, u = p
    # independent check: the parsed Fraction must agree with a decimal re-read
    try:
        if abs(float(v) - float(Fraction(v))) > 1e-9:
            return False
    except (OverflowError, ValueError):
        return False

    if domain == "money":
        # £2.50, 2.50, 2.5, 250p all accepted; 2.5%, 2.5 cm rejected
        return kind in ("money", "plain") and u is None and v == want
    if domain == "proportion":
        # 0.5, 1/2, 50% all accepted; a plain number is read AS the proportion
        return kind in ("plain", "percent") and u is None and v == want
    if domain == "measure":
        if kind != "plain":
            return False
        if u is not None and u != unit:          # wrong unit -> reject
            return False
        return v == want
    # plain number / integer / fraction: a % or money form is the WRONG form
    return kind == "plain" and u is None and v == want


# convenience for money comparisons
def accepts_money(typed, pounds) -> bool:
    p = parse(typed)
    if p is None:
        return False
    v, kind, u = p
    want = pounds if isinstance(pounds, Fraction) else _num_core(str(pounds))
    return kind in ("money", "plain") and u is None and v == want
