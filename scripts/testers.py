#!/usr/bin/env python3
"""
Independent testers for the four generators.

Each tester re-checks a question WITHOUT reusing the generator's own answer
logic, and FAILS anything it does not recognise (unknown = not verified).

- Maths  : reads the question TEXT, solves it from scratch, and requires exactly
           one option equal in value to its answer — the one marked correct.
- VR     : re-derives rule-based answers; for word types, checks that no
           distractor is also a valid answer (same meaning / same category).
- NVR    : folds the net with separate 3D geometry (not the generator's roll
           simulator) and judges each option with a determinant orientation
           test, so mirror images are caught.
- English: checks the key plus the known ways a second answer could also be
           right. This is a strong filter, not a proof.
"""
import re
import string
from fractions import Fraction
from math import isqrt

import vocab

AL = string.ascii_uppercase


# ======================================================================
# MATHS — solve from the question text
# ======================================================================
def _num(s):
    """Parse an option like '£4.35', '72 cm²', '3/4', '45°' -> Fraction (or None)."""
    t = s.strip().replace("£", "").replace(",", "")
    t = re.sub(r"\s*(cm²|cm|°)$", "", t)
    try:
        return Fraction(t)
    except (ValueError, ZeroDivisionError):
        return None


def _is_prime(n):
    return n > 1 and all(n % k for k in range(2, isqrt(n) + 1))


def solve_maths(q):
    """Return the expected answer as a Fraction, or None if the template is unknown."""
    m = re.fullmatch(r"Work out (\d+) × (\d+) ([+−]) (\d+)", q)
    if m:
        a, b, op, c = int(m[1]), int(m[2]), m[3], int(m[4])
        return Fraction(a * b + c if op == "+" else a * b - c)
    # single two-operand operation (MA-B01 mental; MA-B04 division facts):
    m = re.fullmatch(r"Work out (\d+) ([+\-−×÷]) (\d+)", q)
    if m:
        a, op, b = int(m[1]), m[2], int(m[3])
        if op == "+":
            return Fraction(a + b)
        if op in ("-", "−"):
            return Fraction(a - b)
        if op == "×":
            return Fraction(a * b)
        if op == "÷":
            return Fraction(a, b) if b else None
    m = re.fullmatch(r"Use long multiplication to work out (\d+) × (\d+)\.", q)
    if m:
        return Fraction(int(m[1]) * int(m[2]))
    m = re.fullmatch(r"Work out (\d+) ÷ (\d+)\.", q)
    if m:
        return Fraction(int(m[1]), int(m[2]))
    m = re.fullmatch(r"What is (\d+)/(\d+) of (\d+)\?", q)
    if m:
        return Fraction(int(m[1]), int(m[2])) * int(m[3])
    m = re.fullmatch(r"Work out (\d+)/(\d+) \+ (\d+)/(\d+)\. Give your answer in its simplest form\.", q)
    if m:
        return Fraction(int(m[1]), int(m[2])) + Fraction(int(m[3]), int(m[4]))
    m = re.fullmatch(r"Find (\d+)% of (\d+)\.", q)
    if m:
        return Fraction(int(m[1]) * int(m[2]), 100)
    m = re.fullmatch(r"A £(\d+) item is reduced by (\d+)% in a sale\. What is the new price\?", q)
    if m:
        return Fraction(int(m[1]) * (100 - int(m[2])), 100)
    m = re.fullmatch(r"£(\d+) is shared in the ratio (\d+):(\d+)\. What is the larger share\?", q)
    if m:
        t, a, b = int(m[1]), int(m[2]), int(m[3])
        return Fraction(t * max(a, b), a + b)
    m = re.fullmatch(r"A rectangle is (\d+) cm by (\d+) cm\. What is its (area|perimeter)\?", q)
    if m:
        w, h = int(m[1]), int(m[2])
        return Fraction(w * h if m[3] == "area" else 2 * (w + h))
    m = re.fullmatch(r"Two angles in a triangle are (\d+)° and (\d+)°\. What is the third angle\?", q)
    if m:
        return Fraction(180 - int(m[1]) - int(m[2]))
    m = re.fullmatch(r"What is the next term: ([\d, ]+), …\?", q)
    if m:
        seq = [int(x) for x in m[1].split(",")]
        diffs = {seq[i + 1] - seq[i] for i in range(len(seq) - 1)}
        return Fraction(seq[-1] + diffs.pop()) if len(diffs) == 1 else None
    m = re.fullmatch(r"Find the mean of: ([\d, ]+)\.", q)
    if m:
        vals = [int(x) for x in m[1].split(",")]
        return Fraction(sum(vals), len(vals))
    m = re.fullmatch(r"Round (\d+) to the nearest (\d+)\.", q)
    if m:
        n, base = int(m[1]), int(m[2])
        return Fraction((n + base // 2) // base * base)        # round half up
    m = re.fullmatch(r"A book costs £(\d+\.\d\d)\. You pay with a £(\d+) note\. How much change\?", q)
    if m:
        return Fraction(m[2]) - Fraction(m[1])
    m = re.fullmatch(r"Convert (\d+(?:\.\d+)?) metres into centimetres\.", q)
    if m:
        return Fraction(m[1]) * 100
    m = re.fullmatch(r"What number does the Roman numeral ([IVXLCDM]+) represent\?", q)
    if m:
        return Fraction(_roman_to_int(m[1]))
    m = re.fullmatch(r"What number goes in the box\? (\d+) ([+×÷]) \? = (\d+)", q)
    if m:
        a, op, b = int(m[1]), m[2], int(m[3])
        if op == "×":
            return Fraction(b, a) if a else None
        if op == "÷":
            return Fraction(a, b) if b else None
        if op == "+":
            return Fraction(b - a)
    return None


def _roman_to_int(s):
    vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = prev = 0
    for ch in reversed(s):
        v = vals[ch]
        total += -v if v < prev else v
        prev = v if v >= prev else prev
    return total


def check_maths_item(it):
    """Return (ok, reason)."""
    opts = it["options"]
    if len({o.strip() for o in opts}) != 4:
        return False, "options are not 4 visibly different values"
    try:
        marked = ord(it["answer"]) - 65
        assert 0 <= marked < 4
    except Exception:
        return False, "bad answer letter"
    q = it["question"]
    if q == "Which of these is a prime number?":
        primes = [i for i, o in enumerate(opts) if o.strip().isdigit() and _is_prime(int(o))]
        return (primes == [marked], "prime check")
    # "choose the option with property P" items: the options ARE the candidates,
    # so the independent solver recomputes which option(s) satisfy P (must be one).
    m = re.fullmatch(r"Which of these numbers is the (largest|smallest)\?", q)
    if m:
        vals = [_num(o) for o in opts]
        if any(v is None for v in vals):
            return False, "non-numeric options"
        want = max(vals) if m[1] == "largest" else min(vals)
        return ([i for i, v in enumerate(vals) if v == want] == [marked], "compare")
    m = re.fullmatch(r"Which of these is an (even|odd) number\?", q)
    if m:
        par = 0 if m[1] == "even" else 1
        idxs = [i for i, o in enumerate(opts) if o.strip().lstrip("-").isdigit() and int(o) % 2 == par]
        return (idxs == [marked], "parity")
    m = re.fullmatch(r"Which of these is a multiple of (\d+)\?", q)
    if m:
        k = int(m[1])
        idxs = [i for i, o in enumerate(opts) if o.strip().isdigit() and int(o) % k == 0]
        return (idxs == [marked], "multiple")
    exp = solve_maths(q)
    if exp is None:
        return False, "unknown question template (cannot verify)"
    if exp < 0:
        return False, f"answer {exp} is negative (impossible question)"
    matches = [i for i, o in enumerate(opts) if _num(o) == exp]
    if matches != [marked]:
        return False, f"expected {exp}; options matching = {matches}, marked = {marked}"
    if "simplest form" in q:
        f = _num(opts[marked])
        if f is not None and "/" in opts[marked]:
            n, d = opts[marked].split("/")
            if Fraction(int(n), int(d)).denominator != int(d):
                return False, "answer not in simplest form"
    return True, "ok"


def test_maths(items):
    return sum(check_maths_item(it)[0] for it in items), len(items)


# ======================================================================
# VR
# ======================================================================
def _p(c):
    return AL.index(c)


def check_vr_item(it):
    c = it["_check"]; opts = it["options"]
    if len(set(opts)) != 4:
        return False
    got = opts[ord(it["answer"]) - 65]; k = c["kind"]
    if k == "letter_series":
        s = c["seq"]; step = (_p(s[1]) - _p(s[0])) % 26
        return all((_p(s[i + 1]) - _p(s[i])) % 26 == step for i in range(len(s) - 1)) \
            and AL[(_p(s[-1]) + step) % 26] == got
    if k == "number_series":
        s = c["seq"]; step = s[1] - s[0]
        return all(s[i + 1] - s[i] == step for i in range(len(s) - 1)) and str(s[-1] + step) == got
    if k == "letters_for_numbers":
        # parse the question text, not the stored map
        m = re.fullmatch(r"If (.+), work out ([A-Z]) ([+−]) ([A-Z])\.", it["question"])
        if not m:
            return False
        amap = {kv.split("=")[0]: int(kv.split("=")[1]) for kv in m[1].split(", ")}
        if set(amap) & set("ABCD"):
            return False                       # letters would clash with answer labels
        v = amap[m[2]] + amap[m[4]] if m[3] == "+" else amap[m[2]] - amap[m[4]]
        return str(v) == got and sum(o == str(v) for o in opts) == 1
    if k == "letter_code":
        w1, c1, sm = c["w1"], c["c1"], c["sample"]
        sh = {(_p(c1[i]) - _p(w1[i])) % 26 for i in range(len(w1))}
        if len(sh) != 1:
            return False
        s = next(iter(sh))
        return "".join(AL[(_p(ch) + s) % 26] for ch in sm) == got
    if k == "odd_word":
        cats_of = lambda w: {name for name, ws in vocab.CATS.items() if w in ws}
        groups = [cats_of(o) for o in opts]
        if any(len(g) != 1 for g in groups):
            return False                       # a word in 0 or 2+ categories is ambiguous
        flat = [next(iter(g)) for g in groups]
        counts = {x: flat.count(x) for x in flat}
        odd = [o for o, cat in zip(opts, flat) if counts[cat] == 1]
        return len(counts) == 2 and odd == [got]
    if k == "word_analogy":
        c1, d1 = c["pair"]
        if c["rel"] == "syn":
            right = [o for o in opts if o != c1 and vocab.same_meaning(o, c1)]
        else:
            right = [o for o in opts if vocab.opposite_of(c1, o)]
        return right == [got]
    return False


def test_vr(items):
    return sum(check_vr_item(it) for it in items), len(items)


# ======================================================================
# NVR — separate 3D folding + orientation test
# ======================================================================
def _neg(v):
    return tuple(-x for x in v)


def fold_net_outside(cells, syms):
    """Fold a net (net = outside of cube, flaps fold away from the viewer).

    Independent of the generator: tracks, for each cell, its outward normal and
    the 3D direction that each net direction (N/E/S/W) points to on that face.
    Moving onto a neighbour in net direction d: the neighbour's normal is the
    old direction d; travelling further in d now heads along -old_normal.
    """
    d2 = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}
    opp = {"N": "S", "S": "N", "E": "W", "W": "E"}
    start = cells[0]
    frame = {start: ((0, 0, 1), {"N": (0, 1, 0), "S": (0, -1, 0), "E": (1, 0, 0), "W": (-1, 0, 0)})}
    todo = [start]
    while todo:
        cur = todo.pop()
        n, dirs = frame[cur]
        for d, (dr, dc) in d2.items():
            nb = (cur[0] + dr, cur[1] + dc)
            if nb in cells and nb not in frame:
                nd = dict(dirs)
                nd[d] = _neg(n)
                nd[opp[d]] = n
                frame[nb] = (dirs[d], nd)
                todo.append(nb)
    normals = {frame[c][0]: syms[i] for i, c in enumerate(cells) if c in frame}
    return normals if len(normals) == 6 else None


def _det(a, b, c):
    return (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0]))


def is_real_view(view, normal_of):
    """(top, left, right) is a real view iff the three faces meet at one corner
    and appear in the right-handed order: det(left, right, top) = +1."""
    t, l, r = (normal_of[s] for s in view)
    dots = [sum(x * y for x, y in zip(u, v)) for u, v in ((t, l), (t, r), (l, r))]
    return all(d == 0 for d in dots) and _det(l, r, t) == 1


def check_nvr_item(it):
    c = it["_check"]
    if c["kind"] == "cube_net":
        assign = fold_net_outside(list(c["cells"]), c["syms"])
    else:
        assign = c["assign"]
    if assign is None:
        return False
    normal_of = {s: n for n, s in assign.items()}
    real = [i for i, o in enumerate(c["opts"]) if is_real_view(o, normal_of)]
    if c["kind"] == "cube_rotation":
        ref = tuple(c.get("ref", ()))
        if not ref or not is_real_view(ref, normal_of):
            return False
        # solvable from the picture: options may only show faces seen in the reference
        if any(set(o) != set(ref) for o in c["opts"]):
            return False
    return real == [c["idx"]] and len(set(map(tuple, c["opts"]))) == 4


def test_nvr(items):
    return sum(check_nvr_item(it) for it in items), len(items)


# ======================================================================
# ENGLISH — key + ambiguity checks
# ======================================================================
def check_english_item(it):
    c = it["_check"]; opts = it["options"]
    if len(set(opts)) != 4:
        return False
    got = opts[ord(it["answer"]) - 65]
    key = c.get("correct", c.get("ans"))
    if got != key:
        return False
    others = [o for o in opts if o != got]
    k = c["kind"]
    if k == "spelling":
        # a misspelling must not equal / be a known real word in our banks
        known = set(vocab._CL) | {w for p in vocab.ANT for w in p} | \
                {w for ws in vocab.CATS.values() for w in ws} | {"defiantly", "surprize", "lightening"}
        return not any(o in known for o in others)
    if k == "synonym":
        return not any(vocab.same_meaning(o, c["w"]) for o in others)
    if k == "antonym":
        return not any(vocab.opposite_of(c["w"], o) for o in others)
    if k == "grammar_agree":
        good = {c["pv"] if c["plural"] else c["sv"]}
        # any bare present-tense or past-tense verb form would also be grammatical
        return not any(o in good or o.endswith("ed") for o in others)
    if k in ("grammar", "cloze"):
        return True                     # authored items: key + distinct only
    return False


def test_english(items):
    return sum(check_english_item(it) for it in items), len(items)
