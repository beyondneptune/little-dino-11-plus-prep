#!/usr/bin/env python3
"""
Lesson verification (parent STEP 1e): re-compute every worked example in a lesson
with the INDEPENDENT solver, so a wrong example fails the build. Also report the
reading level.

Checkable claims in a lesson:
  * arithmetic:  "a op b = c"            (op in + - x /)  -> solver re-derives
  * rounding:    "Round n to the nearest b" ... "-> **result**"  -> solver re-derives
"""
import re

import testers as T
from reading_level import fk_grade

_EQ = re.compile(r"(\d+)\s*([+\-−×÷])\s*(\d+)\s*=\s*\*{0,2}(\d+)\*{0,2}")
_ROUND = re.compile(r"Round (\d+) to the nearest (\d+)")
_ARROW = re.compile(r"→\s*\*\*(\d+)\*\*")


def check_examples(text: str) -> list[str]:
    """Return a list of worked-example claims the solver disagrees with."""
    issues = []
    for m in _EQ.finditer(text):
        a, op, b, c = m.group(1), m.group(2), m.group(3), int(m.group(4))
        exp = T.solve_maths(f"Work out {a} {op} {b}")
        if exp is None or exp != c:
            issues.append(f"'{a} {op} {b} = {c}' but solver gives {exp}")
    # pair each rounding statement with the next arrow-result, in reading order
    events = sorted(
        [(m.start(), "R", m.groups()) for m in _ROUND.finditer(text)]
        + [(m.start(), "A", m.groups()) for m in _ARROW.finditer(text)])
    pending = None
    for _, kind, g in events:
        if kind == "R":
            pending = g
        elif pending:
            n, base = pending
            exp = T.solve_maths(f"Round {n} to the nearest {base}.")
            if exp is None or exp != int(g[0]):
                issues.append(f"'Round {n} to nearest {base}' states {g[0]} "
                              f"but solver gives {exp}")
            pending = None
    return issues


def check_lesson(text: str, reading_ceiling: float = 6.0) -> list[str]:
    issues = check_examples(text)
    grade = fk_grade(text)
    if grade > reading_ceiling:
        issues.append(f"reading grade {grade:.1f} > ceiling {reading_ceiling}")
    return issues
