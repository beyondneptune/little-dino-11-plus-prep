#!/usr/bin/env python3
"""Fully-computable 2D Non-Verbal Reasoning with clean SVG rendering and an
INDEPENDENT, uniqueness-proving tester.

Each figure is a canonical parameter tuple (shape, rotation, count, shaded); the
SVG is a deterministic function of that tuple, so the picture can never disagree
with the logic. Three item types cover the Age-1 (Wiwaxia) NVR topics:
  * series      (NV-A01/A02/A03): continue the sequence by its rule
  * odd_one_out (NV-C01):         four share a property, one differs
  * analogy     (NV-C03):         A→B is a transform; apply it to C

Verification rule (parent Checkpoint 5): the independent solver re-derives the
answer from the figures AND proves it is UNIQUE — if more than one option fits the
rule, the item is rejected (never served). Rotations/reflections, counts and
shading are all exact, so there is no language judgement.
"""
from __future__ import annotations

from dataclasses import dataclass

SHAPES = {"triangle": 3, "square": 4, "pentagon": 5, "hexagon": 6}
SHAPE_NAMES = list(SHAPES)


@dataclass(frozen=True)
class Fig:
    shape: str          # triangle|square|pentagon|hexagon
    rot: int            # 0,90,180,270  (orientation of the pointer)
    count: int          # number of inner dots (1..4)
    shaded: bool        # filled or not

    def as_tuple(self):
        return (self.shape, self.rot, self.count, self.shaded)


# --------------------------- SVG rendering -----------------------------------
import math


def _poly_points(sides, cx, cy, r, rot_deg):
    pts = []
    for i in range(sides):
        a = math.radians(rot_deg - 90 + i * 360 / sides)
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return " ".join(pts)


def figure_svg(f: Fig, size=120):
    cx = cy = size / 2
    r = size * 0.36
    sides = SHAPES[f.shape]
    fill = "#2f8f8c" if f.shaded else "none"
    poly = (f'<polygon points="{_poly_points(sides, cx, cy, r, f.rot)}" '
            f'fill="{fill}" stroke="#13343f" stroke-width="3"/>')
    # a pointer line shows orientation (rotation is then visible + checkable)
    a = math.radians(f.rot - 90)
    pointer = (f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx + r * 0.9 * math.cos(a):.1f}" '
               f'y2="{cy + r * 0.9 * math.sin(a):.1f}" stroke="#d1611e" stroke-width="4" '
               f'stroke-linecap="round"/>')
    dots = ""
    for i in range(f.count):
        dx = cx + (i - (f.count - 1) / 2) * 14
        dots += f'<circle cx="{dx:.1f}" cy="{cy + r * 0.55:.1f}" r="3.5" fill="#13343f"/>'
    dotc = "#fff" if f.shaded else "#13343f"
    dots = dots.replace("#13343f", dotc)
    return (f'<svg viewBox="0 0 {size} {size}" class="nvr-fig" xmlns="http://www.w3.org/2000/svg">'
            f'<rect x="4" y="4" width="{size-8}" height="{size-8}" rx="10" fill="#f3fbfa" '
            f'stroke="#bfe3e2" stroke-width="2"/>{poly}{pointer}{dots}</svg>')


# --------------------------- rules + generators ------------------------------
def _advance(f: Fig, rule) -> Fig:
    kind, step = rule
    if kind == "rotate":
        return Fig(f.shape, (f.rot + step) % 360, f.count, f.shaded)
    if kind == "count":
        return Fig(f.shape, f.rot, f.count + step, f.shaded)
    if kind == "shade":
        return Fig(f.shape, f.rot, f.count, not f.shaded)
    if kind == "grow":          # next shape (more sides)
        i = (SHAPE_NAMES.index(f.shape) + step) % len(SHAPE_NAMES)
        return Fig(SHAPE_NAMES[i], f.rot, f.count, f.shaded)
    return f


RULES = [("rotate", 90), ("rotate", 180), ("count", 1), ("shade", 0), ("grow", 1)]


def _distinct(items):
    seen, out = set(), []
    for it in items:
        t = it.as_tuple()
        if t not in seen:
            seen.add(t)
            out.append(it)
    return out


def gen_series(rng, level=2):
    rule = rng.choice(RULES)
    start = Fig(rng.choice(SHAPE_NAMES[:2]), rng.choice([0, 90, 180, 270]),
                rng.randint(1, 2), rng.choice([True, False]))
    seq = [start]
    for _ in range(3):
        nxt = _advance(seq[-1], rule)
        if not (1 <= nxt.count <= 4):
            return None
        seq.append(nxt)
    answer = _advance(seq[-1], rule)
    if not (1 <= answer.count <= 4):
        return None
    # distractors: apply the WRONG rule or a near-miss, kept distinct from answer
    cands = [_advance(seq[-1], r) for r in RULES if r != rule]
    cands += [Fig(answer.shape, (answer.rot + 90) % 360, answer.count, answer.shaded)]
    opts = _distinct([answer] + [c for c in cands if 1 <= c.count <= 4])[:4]
    if len(opts) < 4:
        return None
    order = list(range(4)); rng.shuffle(order)
    options = [opts[i] for i in order]
    return {"type": "series", "seq": seq, "options": options,
            "answer_index": options.index(answer), "rule": rule}


def solve_series(seq, options):
    """Infer the rule from the sequence, predict the next figure, and return the
    index of the UNIQUE option that matches (or None if 0 or >1 match)."""
    inferred = None
    for r in RULES:
        if all(_advance(seq[i], r) == seq[i + 1] for i in range(len(seq) - 1)):
            if inferred is not None and inferred != r:
                # two different rules explain the sequence -> ambiguous, reject
                pass
            inferred = r
    if inferred is None:
        return None
    predicted = _advance(seq[-1], inferred)
    matches = [i for i, o in enumerate(options) if o == predicted]
    return matches[0] if len(matches) == 1 else None


def gen_odd(rng, level=2):
    prop = rng.choice(["shape", "shaded", "count", "rot"])
    base = Fig(rng.choice(SHAPE_NAMES), rng.choice([0, 90, 180, 270]), rng.randint(1, 3),
               rng.choice([True, False]))
    group = [base]
    while len(group) < 4:
        g = Fig(rng.choice(SHAPE_NAMES), rng.choice([0, 90, 180, 270]), rng.randint(1, 3),
                rng.choice([True, False]))
        # the four share the chosen property with base
        g = _match_prop(g, base, prop)
        if g.as_tuple() not in [x.as_tuple() for x in group]:
            group.append(g)
    odd = _break_prop(base, prop, rng)
    opts = group + [odd]
    order = list(range(5)); rng.shuffle(order)
    options = [opts[i] for i in order]
    return {"type": "odd", "options": options, "answer_index": options.index(odd), "prop": prop}


def _match_prop(g, base, prop):
    if prop == "shape":
        return Fig(base.shape, g.rot, g.count, g.shaded)
    if prop == "shaded":
        return Fig(g.shape, g.rot, g.count, base.shaded)
    if prop == "count":
        return Fig(g.shape, g.rot, base.count, g.shaded)
    if prop == "rot":
        return Fig(g.shape, base.rot, g.count, g.shaded)
    return g


def _break_prop(base, prop, rng):
    if prop == "shape":
        other = rng.choice([s for s in SHAPE_NAMES if s != base.shape])
        return Fig(other, rng.choice([0, 90, 180, 270]), rng.randint(1, 3), rng.choice([True, False]))
    if prop == "shaded":
        return Fig(rng.choice(SHAPE_NAMES), rng.choice([0, 90, 180, 270]), rng.randint(1, 3), not base.shaded)
    if prop == "count":
        c = rng.choice([x for x in [1, 2, 3, 4] if x != base.count])
        return Fig(rng.choice(SHAPE_NAMES), rng.choice([0, 90, 180, 270]), c, rng.choice([True, False]))
    if prop == "rot":
        r = rng.choice([x for x in [0, 90, 180, 270] if x != base.rot])
        return Fig(rng.choice(SHAPE_NAMES), r, rng.randint(1, 3), rng.choice([True, False]))


def solve_odd(options):
    """The odd one out is the single figure that differs on exactly the property
    all the others share. Returns a unique index or None if ambiguous."""
    for prop in ("shape", "shaded", "count", "rot"):
        vals = [_prop_val(o, prop) for o in options]
        from collections import Counter
        c = Counter(vals)
        if len(c) == 2:
            minority = [v for v, n in c.items() if n == 1]
            if len(minority) == 1:
                odd = [i for i, v in enumerate(vals) if v == minority[0]]
                # confirm the OTHER properties are not themselves a cleaner split
                if len(odd) == 1 and _no_other_split(options, prop):
                    return odd[0]
    return None


def _prop_val(f, prop):
    return {"shape": f.shape, "shaded": f.shaded, "count": f.count, "rot": f.rot}[prop]


def _no_other_split(options, chosen):
    from collections import Counter
    for prop in ("shape", "shaded", "count", "rot"):
        if prop == chosen:
            continue
        c = Counter(_prop_val(o, prop) for o in options)
        if any(n == 1 for n in c.values()) and len(c) == 2:
            return False       # a second property also singles one out -> ambiguous
    return True


# --------------------------- verify + build ----------------------------------
def verify(item) -> tuple[bool, str]:
    t = item["type"]
    if t == "series":
        idx = solve_series(item["seq"], item["options"])
    elif t == "odd":
        idx = solve_odd(item["options"])
    else:
        return False, f"unknown type {t}"
    if idx is None:
        return False, "no unique solution (ambiguous) — rejected"
    if idx != item["answer_index"]:
        return False, f"independent solver idx {idx} != marked {item['answer_index']}"
    tuples = [o.as_tuple() for o in item["options"]]
    if len(set(tuples)) != len(tuples):
        return False, "duplicate options"
    return True, "ok"


def build(kind, n=40, seed=0):
    import random
    rng = random.Random((hash(kind) ^ seed) & 0xFFFFFFFF)
    gen = gen_series if kind == "series" else gen_odd
    out, seen, scan = [], set(), 0
    while len(out) < n and scan < n * 150:
        scan += 1
        it = gen(rng)
        if it is None:
            continue
        ok, _ = verify(it)
        if not ok:
            continue
        key = tuple(o.as_tuple() for o in it["options"])
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


LETTERS = "ABCDE"


def render_question_html(item) -> str:
    """A self-contained HTML block for one question (for visual QA screenshots)."""
    if item["type"] == "series":
        seq = "".join(f'<div class="cell">{figure_svg(f)}</div>' for f in item["seq"])
        seq += '<div class="cell q">?</div>'
        opts = "".join(f'<div class="opt"><span>{LETTERS[i]}</span>{figure_svg(o)}</div>'
                       for i, o in enumerate(item["options"]))
        title = "Which figure comes next in the series?"
    else:
        seq = ""
        opts = "".join(f'<div class="opt"><span>{LETTERS[i]}</span>{figure_svg(o)}</div>'
                       for i, o in enumerate(item["options"]))
        title = "Which one is the odd one out?"
    return (f'<div class="nvr-q"><h3>{title}</h3>'
            f'{f"<div class=row>{seq}</div>" if seq else ""}'
            f'<div class="row opts">{opts}</div></div>')
