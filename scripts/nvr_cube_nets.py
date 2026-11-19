#!/usr/bin/env python3
"""
Proof-of-concept NVR 3D generator: "Which cube can be folded from this net?"

All content is original (abstract symbols on cube faces). Each question is
generated AND verified in code: a cube can never show two OPPOSITE faces at the
same corner, so the correct option is the only one whose three visible faces are
pairwise non-opposite. The code asserts exactly one option is valid.

NOTE (honest limitation): this enforces the opposite-face rule rigorously but
does NOT test rotational orientation / chirality of the symbols.
"""
import random
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent.parent / "nvr_proof"
MARKERS = ["o", "s", "D", "P", "*", "X"]          # 6 distinct abstract symbols
# cross net:   T / L F R Bk / Bo   -> opposite pairs F-Bk, T-Bo, L-R
NET_GRID = {"T": (1, 2), "L": (0, 1), "F": (1, 1), "R": (2, 1), "Bk": (3, 1), "Bo": (1, 0)}


def opposite_pairs(m):
    return [(m["F"], m["Bk"]), (m["T"], m["Bo"]), (m["L"], m["R"])]


def valid_triple(triple, pairs):
    pset = {frozenset(p) for p in pairs}
    return not any(frozenset((triple[i], triple[j])) in pset
                   for i in range(3) for j in range(i + 1, 3))


def build(seed):
    rng = random.Random(seed)
    syms = MARKERS[:]; rng.shuffle(syms)
    mapping = dict(zip(["F", "Bk", "T", "Bo", "L", "R"], syms))
    pairs = opposite_pairs(mapping)
    correct = tuple(rng.choice(list(p)) for p in pairs)          # one from each pair
    distractors = []
    seen = {frozenset(correct)}
    while len(distractors) < 3:
        p = rng.choice(pairs)
        third = rng.choice([s for s in syms if s not in p])
        trip = tuple(rng.sample([p[0], p[1], third], 3))
        if not valid_triple(trip, pairs) and frozenset(trip) not in seen:
            seen.add(frozenset(trip)); distractors.append(trip)
    options = [correct] + distractors
    rng.shuffle(options)
    idx = options.index(correct)
    # ---- verify: exactly one option obeys the cube rule ----
    valids = [i for i, o in enumerate(options) if valid_triple(o, pairs)]
    assert valids == [idx], f"VERIFY FAIL seed={seed}: valid={valids} correct={idx}"
    return mapping, options, idx


# ---------- drawing ----------
def iso_cube(ax, cx, cy, s, top, left, right):
    a, b = s * 0.866, s * 0.5
    top_f = [(cx, cy + s), (cx + a, cy + s + b), (cx, cy + s + 2 * b), (cx - a, cy + s + b)]
    right_f = [(cx, cy), (cx + a, cy + b), (cx + a, cy + s + b), (cx, cy + s)]
    left_f = [(cx, cy), (cx - a, cy + b), (cx - a, cy + s + b), (cx, cy + s)]
    for poly, fc in [(top_f, "#eef2ff"), (left_f, "#dbe3ff"), (right_f, "#c7d2fe")]:
        ax.add_patch(plt.Polygon(poly, closed=True, ec="black", fc=fc, lw=1.5))
    ax.scatter([cx], [cy + s + b], marker=top, s=260, c="black", zorder=5)
    ax.scatter([cx - a / 2], [cy + (s + b) / 2], marker=left, s=260, c="black", zorder=5)
    ax.scatter([cx + a / 2], [cy + (s + b) / 2], marker=right, s=260, c="black", zorder=5)


def draw_net(ax, m):
    for face, (col, row) in NET_GRID.items():
        ax.add_patch(plt.Rectangle((col, row), 1, 1, ec="black", fc="#f8fafc", lw=1.5))
        ax.scatter([col + 0.5], [row + 0.5], marker=m[face], s=320, c="black", zorder=5)
    ax.set_xlim(-0.3, 4.3); ax.set_ylim(-0.3, 3.3); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("The net", fontsize=11)


def render(seed, path):
    mapping, options, idx = build(seed)
    fig = plt.figure(figsize=(9, 6))
    axn = fig.add_axes([0.05, 0.55, 0.9, 0.4]); draw_net(axn, mapping)
    for i, opt in enumerate(options):
        ax = fig.add_axes([0.03 + i * 0.245, 0.06, 0.22, 0.42])
        iso_cube(ax, 1.0, 0.2, 1.0, opt[0], opt[1], opt[2])
        ax.set_xlim(-1.3, 1.6); ax.set_ylim(-0.1, 2.3); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(f"{chr(65 + i)}", fontsize=13, fontweight="bold")
    fig.suptitle("Which cube can be folded from the net?", fontsize=13, y=0.99)
    fig.savefig(path, dpi=110); plt.close(fig)
    return chr(65 + idx)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    answers = {}
    for n, seed in enumerate([11, 23, 42], 1):
        ans = render(seed, OUT / f"cube_net_q{n}.png")
        answers[f"Q{n}"] = ans
    print("Generated 3 questions in", OUT)
    print("Verified answer key (code-checked unique):", answers)
