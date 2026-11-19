#!/usr/bin/env python3
"""
NVR question-bank generator (all original abstract shapes; answers code-verified).

Shape model: a regular polygon (3-8 sides), open/shaded, with ONE orientation
marker (a filled dot on one vertex) so rotation-type patterns are visible.

Transforms are single-attribute and NON-wrapping (except 'spin', which is a
genuine, visible rotation of the marker) so the answer always matches the rule
a human would read.

Types:
  2D  — analogy (A:B :: C:?), series (next in sequence), odd-one-out
  3D  — cube nets + cube rotation  (from nvr_3d.py)
Outputs PNGs under nvr_bank/<type>/ and a verified nvr_bank/answer_key.csv.
"""
import csv
import random
import sys
from math import cos, pi, sin
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nvr_3d as D                                         # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "nvr_bank"
FILLC = {"open": "white", "shaded": "#c7d2fe"}


# ---------------- shape model ----------------
def verts(n, r=1.0):
    return [(r * cos(pi / 2 + 2 * pi * k / n), r * sin(pi / 2 + 2 * pi * k / n)) for k in range(n)]


def draw_shape(ax, sh, r=1.0):
    vs = verts(sh["sides"], r)
    ax.add_patch(Polygon(vs, closed=True, fc=FILLC[sh["fill"]], ec="black", lw=2.2))
    mx, my = vs[sh["marker"] % sh["sides"]]
    ax.add_patch(Circle((mx, my), 0.17 * r, fc="black", ec="black", zorder=5))
    ax.set_xlim(-1.35 * r, 1.35 * r); ax.set_ylim(-1.35 * r, 1.35 * r)
    ax.set_aspect("equal"); ax.axis("off")


def rand_shape(rng, sides=None):
    n = sides or rng.choice([4, 5, 6])
    return {"sides": n, "fill": rng.choice(list(FILLC)), "marker": rng.randrange(n)}


def can(sh, t):
    return sh["sides"] < 8 if t == "add_side" else True


def apply_T(sh, t):
    s = dict(sh)
    if t == "spin":
        s["marker"] = (s["marker"] + 1) % s["sides"]
    elif t == "add_side":
        s["sides"] += 1                      # marker index stays valid (< old < new)
    elif t == "toggle_fill":
        s["fill"] = "shaded" if s["fill"] == "open" else "open"
    return s


TRANSFORMS = ["spin", "add_side", "toggle_fill"]


def _key(s):
    return (s["sides"], s["fill"], s["marker"] % s["sides"])


def _distractors(C, correct, t, rng):
    pool = [apply_T(C, t2) for t2 in TRANSFORMS if t2 != t and can(C, t2)]
    if can(correct, t):
        pool.append(apply_T(correct, t))                 # one step too far
    pool.append(apply_T(correct, "toggle_fill"))         # same but fill flipped
    sh = dict(correct); sh["marker"] = (sh["marker"] + 2) % sh["sides"]; pool.append(sh)
    out, seen = [], {_key(correct)}
    rng.shuffle(pool)
    for cand in pool:
        if _key(cand) not in seen:
            seen.add(_key(cand)); out.append(cand)
        if len(out) == 3:
            break
    return out


# ---------------- generators ----------------
def gen_analogy(rng):
    while True:
        t = rng.choice(TRANSFORMS)
        A, C = rand_shape(rng), rand_shape(rng)
        if not (can(A, t) and can(C, t)):
            continue
        B, correct = apply_T(A, t), apply_T(C, t)
        if _key(B) == _key(A):
            continue
        d = _distractors(C, correct, t, rng)
        if len(d) < 3:
            continue
        opts = [correct] + d
        rng.shuffle(opts); idx = opts.index(correct)
        assert sum(_key(o) == _key(correct) for o in opts) == 1
        return {"A": A, "B": B, "C": C}, opts, idx


def gen_series(rng):
    while True:
        t = rng.choice(["spin", "add_side"])
        if t == "add_side":
            S = rand_shape(rng, sides=rng.choice([3, 4])); S["marker"] = 0
        else:
            S = rand_shape(rng, sides=rng.choice([5, 6])); S["marker"] = 0
        seq = [S]
        for _ in range(3):
            seq.append(apply_T(seq[-1], t))
        correct = apply_T(seq[-1], t)
        keys = [_key(s) for s in seq] + [_key(correct)]
        if len(set(keys)) != 5:                         # all five must be distinct
            continue
        d = _distractors(seq[-1], correct, t, rng)
        if len(d) < 3:
            continue
        opts = [correct] + d
        rng.shuffle(opts); idx = opts.index(correct)
        assert sum(_key(o) == _key(correct) for o in opts) == 1
        return seq, opts, idx


def gen_odd(rng):
    attr = rng.choice(["sides", "fill"])
    base = rand_shape(rng); base["marker"] = 0
    odd = dict(base)
    if attr == "sides":
        odd["sides"] = rng.choice([s for s in [4, 5, 6, 7] if s != base["sides"]])
    else:
        odd["fill"] = "shaded" if base["fill"] == "open" else "open"
    shapes = [dict(base) for _ in range(4)] + [odd]
    rng.shuffle(shapes)
    idx = next(i for i, s in enumerate(shapes) if (s["sides"], s["fill"]) == (odd["sides"], odd["fill"]))
    assert sum((s["sides"], s["fill"]) != (base["sides"], base["fill"]) for s in shapes) == 1
    return shapes, idx


# ---------------- rendering ----------------
def _options_row(fig, opts):
    for i, o in enumerate(opts):
        ax = fig.add_axes([0.06 + i * 0.235, 0.06, 0.19, 0.32]); draw_shape(ax, o)
        ax.set_title(chr(65 + i), fontsize=13, fontweight="bold")


def render_analogy(data, opts, idx, path):
    fig = plt.figure(figsize=(9, 6))
    fig.text(0.5, 0.95, "A is to B as C is to … ?", ha="center", fontsize=14, fontweight="bold")
    cells = [("", data["A"]), ("→", None), ("", data["B"]), ("::", None),
             ("", data["C"]), ("→", None), ("?", None)]
    for i, (lab, sh) in enumerate(cells):
        ax = fig.add_axes([0.03 + i * 0.135, 0.52, 0.11, 0.3])
        draw_shape(ax, sh, 0.9) if sh else (ax.text(0.5, 0.5, lab, ha="center", va="center",
                                                    fontsize=20), ax.axis("off"))
    _options_row(fig, opts)
    fig.savefig(path, dpi=110); plt.close(fig); return chr(65 + idx)


def render_series(seq, opts, idx, path):
    fig = plt.figure(figsize=(9, 6))
    fig.text(0.5, 0.95, "What comes next?", ha="center", fontsize=14, fontweight="bold")
    for i, sh in enumerate(seq + [None]):
        ax = fig.add_axes([0.05 + i * 0.185, 0.52, 0.15, 0.32])
        draw_shape(ax, sh, 0.9) if sh else (ax.text(0.5, 0.5, "?", ha="center", va="center",
                                                    fontsize=24), ax.axis("off"))
    _options_row(fig, opts)
    fig.savefig(path, dpi=110); plt.close(fig); return chr(65 + idx)


def render_odd(shapes, idx, path):
    fig = plt.figure(figsize=(10, 3.6))
    fig.text(0.5, 0.9, "Which shape is the odd one out?", ha="center", fontsize=14, fontweight="bold")
    for i, sh in enumerate(shapes):
        ax = fig.add_axes([0.03 + i * 0.193, 0.12, 0.17, 0.6]); draw_shape(ax, sh)
        ax.set_title(chr(65 + i), fontsize=13, fontweight="bold")
    fig.savefig(path, dpi=110); plt.close(fig); return chr(65 + idx)


# ---------------- bank builder ----------------
def build(n2d=5, n3d=3):
    rng = random.Random(2024)
    rows = []

    def add(t, i, ans):
        rows.append({"type": t, "file": f"{t}/q{i:02d}.png", "answer": ans})

    for t, gen, ren in [("analogy", gen_analogy, render_analogy),
                        ("series", gen_series, render_series)]:
        (OUT / t).mkdir(parents=True, exist_ok=True)
        for i in range(1, n2d + 1):
            data, opts, idx = gen(rng)
            add(t, i, ren(data, opts, idx, OUT / t / f"q{i:02d}.png"))
    (OUT / "odd_one_out").mkdir(parents=True, exist_ok=True)
    for i in range(1, n2d + 1):
        shapes, idx = gen_odd(rng)
        add("odd_one_out", i, render_odd(shapes, idx, OUT / "odd_one_out" / f"q{i:02d}.png"))

    (OUT / "cube_net").mkdir(parents=True, exist_ok=True)
    names = list(D.NETS)
    for i in range(1, n3d + 1):
        nm = names[(i - 1) % 4]
        syms, opts, idx = D.make_net_question(D.NETS[nm], 1000 + i)
        add("cube_net", i, D.render("Which cube folds from the net?", opts, idx,
                                    OUT / "cube_net" / f"q{i:02d}.png", D.NETS[nm], syms))
    (OUT / "cube_rotation").mkdir(parents=True, exist_ok=True)
    for i in range(1, n3d + 1):
        ref, opts, idx = D.make_rotation_question(2000 + i)
        add("cube_rotation", i, D.render("Which option is the reference cube, rotated?", opts, idx,
                                         OUT / "cube_rotation" / f"q{i:02d}.png", ref_cube=ref))

    with (OUT / "answer_key.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["type", "file", "answer"]); w.writeheader(); w.writerows(rows)
    from collections import Counter
    print("Built NVR bank:", dict(Counter(r["type"] for r in rows)), "->", OUT)


if __name__ == "__main__":
    build(int(sys.argv[1]) if len(sys.argv) > 1 else 5,
          int(sys.argv[2]) if len(sys.argv) > 2 else 3)
