#!/usr/bin/env python3
"""
NVR 3D question generators (original abstract shapes), with code verification.

Two types:
  * CUBE NETS  — "Which cube folds from this net?"  (general fold simulator, so
    any valid net layout works). The net is the OUTSIDE of the cube (flaps fold
    away from the viewer). Answer = a real view of the folded cube; distractors
    are its mirror images (the classic trap) and views that put opposite faces
    side by side. Exactly one option is a real view of the folded cube.
  * CUBE ROTATION — "Which is the same cube, rotated?" (full 24-rotation model).
    Options use only the three faces visible in the reference, so the question
    is solvable from the picture; distractors are mirror images.

The fold/rotation logic is computed, not recalled, so answers are provably correct.
Honest limit: symbols are treated as orientation-free (the model does not track
which way a symbol is turned on its face).
"""
import random
from itertools import permutations
from collections import deque
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent.parent / "nvr_proof"
MARK = ["o", "s", "D", "P", "*", "X"]            # 6 distinct abstract symbols
OPP = [frozenset((0, 1)), frozenset((2, 3)), frozenset((4, 5))]   # opposite face-ids

# ---- cube orientation as {position: face_id}; identity below ----
IDENT = {"U": 0, "D": 1, "N": 2, "S": 3, "E": 4, "W": 5}


def roll(o, d):
    if d == "N":
        return {"N": o["U"], "D": o["N"], "S": o["D"], "U": o["S"], "E": o["E"], "W": o["W"]}
    if d == "S":
        return {"S": o["U"], "D": o["S"], "N": o["D"], "U": o["N"], "E": o["E"], "W": o["W"]}
    if d == "E":
        return {"E": o["U"], "D": o["E"], "W": o["D"], "U": o["W"], "N": o["N"], "S": o["S"]}
    if d == "W":
        return {"W": o["U"], "D": o["W"], "E": o["D"], "U": o["E"], "N": o["N"], "S": o["S"]}


# ---------- CUBE NETS ----------
def fold_face_ids(cells):
    """Roll a cube over the net; return {cell: face_id} or None if not a valid net."""
    start = cells[0]
    cellset = set(cells)
    ids, orient = {start: IDENT["D"]}, {start: dict(IDENT)}
    seen, q = {start}, deque([start])
    dmap = {(-1, 0): "N", (1, 0): "S", (0, 1): "E", (0, -1): "W"}
    while q:
        r, c = q.popleft()
        for (dr, dc), d in dmap.items():
            nb = (r + dr, c + dc)
            if nb in cellset and nb not in seen:
                o = roll(orient[(r, c)], d)
                orient[nb] = o
                ids[nb] = o["D"]
                seen.add(nb); q.append(nb)
        if len(seen) == len(cells):
            pass
    if len(seen) != 6 or len(set(ids.values())) != 6:
        return None
    return ids


def opposite_sym_pairs(cells, symbols):
    ids = fold_face_ids(cells)
    id2sym = {ids[c]: symbols[i] for i, c in enumerate(cells)}
    return [frozenset((id2sym[a], id2sym[b])) for p in OPP for a, b in [tuple(p)]]


def valid_triple(trip, pairs):
    return not any(frozenset((trip[i], trip[j])) in pairs
                   for i in range(3) for j in range(i + 1, 3))


# fold_face_ids() rolls a cube over the net, which is the same as folding the
# flaps UP around a cube sitting on the paper (printed side inside). The
# standard 11+ convention is that the net shows the OUTSIDE (flaps fold away
# from the viewer), which is that cube reflected top<->bottom: so the face id
# that the roll calls "D" (the starting cell) becomes the TOP face.
ID2NORMAL_OUTSIDE = {IDENT["D"]: (0, 0, 1), IDENT["U"]: (0, 0, -1),
                     IDENT["N"]: (0, 1, 0), IDENT["S"]: (0, -1, 0),
                     IDENT["E"]: (1, 0, 0), IDENT["W"]: (-1, 0, 0)}


def net_assignment(cells, symbols):
    """{outward normal: symbol} for the cube folded from this net (net = outside)."""
    ids = fold_face_ids(cells)
    return {ID2NORMAL_OUTSIDE[ids[c]]: symbols[i] for i, c in enumerate(cells)}


def make_net_question(cells, seed):
    rng = random.Random(seed)
    syms = MARK[:]; rng.shuffle(syms)
    valid = views_of(net_assignment(cells, syms))
    pairs = set(opposite_sym_pairs(cells, syms))
    correct = rng.choice(sorted(valid))
    opts, seen = [correct], {correct}
    # one mirror-image trap (same three faces, impossible order) ...
    mirrors = sorted({(t, r, l) for (t, l, r) in valid} - valid)
    m = rng.choice(mirrors); opts.append(m); seen.add(m)
    # ... then a mix of more mirrors and opposite-faces-adjacent impossibilities
    while len(opts) < 4:
        if rng.random() < 0.5:
            cand = rng.choice(mirrors)
        else:
            p = rng.choice(sorted(pairs, key=sorted))
            third = rng.choice([x for x in syms if x not in p])
            cand = tuple(rng.sample([*sorted(p), third], 3))
        if cand not in valid and cand not in seen:
            seen.add(cand); opts.append(cand)
    rng.shuffle(opts)
    idx = opts.index(correct)
    assert [i for i, o in enumerate(opts) if o in valid] == [idx], "NET verify fail"
    return syms, opts, idx


# ---------- CUBE ROTATION (true 3D geometry) ----------
# Faces are axis normals. The iso view looks from (1,1,1) with z up: the face
# whose rotated normal is +z is drawn on TOP, +x on the LEFT, +y on the RIGHT
# (right-hand vector = forward x up = (-1,1,0), i.e. towards +y). iso_cube()
# draws (top, left, right) in that order. (Earlier versions swapped left/right,
# which drew every cube as its mirror image.)
NORMALS = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
I3 = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
RZ = ((0, -1, 0), (1, 0, 0), (0, 0, 1))      # +90° about z
RX = ((1, 0, 0), (0, 0, -1), (0, 1, 0))      # +90° about x


def matmul(A, B):
    return tuple(tuple(sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)) for i in range(3))


def apply(R, n):
    return tuple(sum(R[i][k] * n[k] for k in range(3)) for i in range(3))


def rotations_24():
    seen, q = {I3}, [I3]
    while q:
        M = q.pop()
        for G in (RZ, RX):
            N = matmul(G, M)
            if N not in seen:
                seen.add(N); q.append(N)
    return list(seen)


ROT24 = rotations_24()
assert len(ROT24) == 24, f"expected 24 rotations, got {len(ROT24)}"


def view(assign, R):
    """Return (top, left, right) symbols = faces landing at +z, +x, +y."""
    t = l = r = None
    for n, sym in assign.items():
        rn = apply(R, n)
        if rn == (0, 0, 1):
            t = sym
        elif rn == (1, 0, 0):
            l = sym
        elif rn == (0, 1, 0):
            r = sym
    return (t, l, r)


def views_of(assign):
    return {view(assign, R) for R in ROT24}


def make_rotation_question_full(seed):
    """Reference view + 4 options that use ONLY the three faces shown in the
    reference, so every option can be judged from the picture alone. The answer
    is a genuine rotation; the distractors are mirror images (impossible)."""
    rng = random.Random(seed)
    syms = MARK[:]; rng.shuffle(syms)
    assign = dict(zip(NORMALS, syms))
    valid = views_of(assign)
    assert len(valid) == 24, "chirality/model error: 24 rotations must give 24 distinct views"
    ref = rng.choice(sorted(valid))
    perms = set(permutations(ref))
    correct = rng.choice(sorted((perms & valid) - {ref}))
    mirrors = sorted(perms - valid)                       # exactly 3
    opts = [correct] + mirrors
    rng.shuffle(opts)
    idx = opts.index(correct)
    assert [i for i, o in enumerate(opts) if o in valid] == [idx], "ROT verify fail"
    return assign, ref, opts, idx


def make_rotation_question(seed):
    _, ref, opts, idx = make_rotation_question_full(seed)
    return ref, opts, idx


# ---------- drawing ----------
def iso_cube(ax, top, left, right, cx=0.0, cy=0.0, s=1.0):
    a, b = s * 0.866, s * 0.5
    faces = [([(cx, cy + s), (cx + a, cy + s + b), (cx, cy + s + 2 * b), (cx - a, cy + s + b)], "#eef2ff"),
             ([(cx, cy), (cx - a, cy + b), (cx - a, cy + s + b), (cx, cy + s)], "#dbe3ff"),
             ([(cx, cy), (cx + a, cy + b), (cx + a, cy + s + b), (cx, cy + s)], "#c7d2fe")]
    for poly, fc in faces:
        ax.add_patch(plt.Polygon(poly, closed=True, ec="black", fc=fc, lw=1.5))
    ax.scatter([cx], [cy + s + b], marker=top, s=240, c="black", zorder=5)
    ax.scatter([cx - a / 2], [cy + (s + b) / 2], marker=left, s=240, c="black", zorder=5)
    ax.scatter([cx + a / 2], [cy + (s + b) / 2], marker=right, s=240, c="black", zorder=5)
    ax.set_xlim(-1.15, 1.15); ax.set_ylim(-0.15, 2.25); ax.set_aspect("equal"); ax.axis("off")


def draw_net(ax, cells, syms):
    rs = [c[0] for c in cells]; cs = [c[1] for c in cells]
    for (r, c), sym in zip(cells, syms):
        ax.add_patch(plt.Rectangle((c, -r), 1, 1, ec="black", fc="#f8fafc", lw=1.5))
        ax.scatter([c + 0.5], [-r + 0.5], marker=sym, s=300, c="black", zorder=5)
    ax.set_xlim(min(cs) - 0.3, max(cs) + 1.3); ax.set_ylim(-max(rs) - 0.3, -min(rs) + 1.3)
    ax.set_aspect("equal"); ax.axis("off")


def render(title, opts, idx, path, net_cells=None, net_syms=None, ref_cube=None):
    fig = plt.figure(figsize=(9, 6.2))
    fig.text(0.5, 0.95, title, ha="center", fontsize=14, fontweight="bold")
    if net_cells is not None:
        axn = fig.add_axes([0.3, 0.52, 0.4, 0.38]); draw_net(axn, net_cells, net_syms)
        fig.text(0.5, 0.9, "the net", ha="center", fontsize=10, style="italic")
    elif ref_cube is not None:
        axr = fig.add_axes([0.42, 0.5, 0.16, 0.34]); iso_cube(axr, *ref_cube)
        fig.text(0.5, 0.89, "reference cube", ha="center", fontsize=10, style="italic")
    for i, opt in enumerate(opts):
        ax = fig.add_axes([0.04 + i * 0.245, 0.06, 0.2, 0.4])
        iso_cube(ax, opt[0], opt[1], opt[2])
        ax.set_title(chr(65 + i), fontsize=13, fontweight="bold")
    fig.savefig(path, dpi=110); plt.close(fig)
    return chr(65 + idx)


NETS = {
    "cross":     [(1, 1), (0, 1), (2, 1), (1, 0), (1, 2), (1, 3)],
    "staircase": [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2), (2, 3)],
    "ell":       [(0, 0), (1, 0), (1, 1), (1, 2), (1, 3), (2, 3)],
    "tee":       [(0, 2), (1, 0), (1, 1), (1, 2), (1, 3), (2, 2)],
    "bad_3x2":   [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)],  # NOT a cube net
}

def self_test():
    """Prove the rotation model distinguishes a cube from its mirror."""
    assert len(ROT24) == 24
    bad = 0
    for seed in range(200):
        a = MARK[:]; random.Random(seed).shuffle(a)
        assign = dict(zip(NORMALS, a))
        V = views_of(assign)
        if len(V) != 24:
            bad += 1
        # mirror (swap left/right) of every valid view must be INVALID (chiral)
        if any((t, r, l) in V for (t, l, r) in V):
            bad += 1
    return bad


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    fails = self_test()
    print(f"Rotation self-test over 200 random cubes: {'PASS' if fails == 0 else f'FAIL ({fails})'}"
          "  (each cube gives 24 distinct views; no mirror view is ever accepted)")
    print("Net validity check (fold simulator):")
    for name, cells in NETS.items():
        print(f"  {name:10s}: {'valid cube net' if fold_face_ids(cells) else 'NOT a cube net'}")
    key = {}
    for n, (name, seed) in enumerate([("cross", 7), ("staircase", 15), ("ell", 29)], 1):
        syms, opts, idx = make_net_question(NETS[name], seed)
        key[f"net_q{n} ({name})"] = render("Which cube folds from the net?", opts, idx,
                                           OUT / f"net_q{n}.png", NETS[name], syms)
    for n, seed in enumerate([101, 202], 1):
        ref, opts, idx = make_rotation_question(seed)
        key[f"rot_q{n}"] = render("Which option is the reference cube, rotated?", opts, idx,
                                  OUT / f"rot_q{n}.png", ref_cube=ref)
    print("Verified answer key:", key)
