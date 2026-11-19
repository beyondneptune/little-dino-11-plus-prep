#!/usr/bin/env python3
"""
4 generators + 4 testers, run SIMULTANEOUSLY (one thread per subject), for
several rounds. Each round: generate questions and INDEPENDENTLY verify them.

- Maths : question text re-solved from scratch; exactly one option may match
- VR    : rule types re-derived; word types checked for a second valid answer
- NVR   : nets re-folded with separate 3D geometry; mirror images rejected
- English: key + ambiguity checks (strong filter, not proof)

A generator "passes training" for a round when its tester verifies 100% of its
output. This is parametric generation + verification, not ML fine-tuning.
"""
import random
import re
import string
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import maths_gen as M
import vr_gen as V
import english_gen as E
import nvr_3d as N

AL = string.ascii_uppercase
REAL_DIGITS = {1: 35, 2: 44, 3: 11, 4: 7}        # measured from real Maths papers


# ---------------- generators ----------------
def gen_maths(n, seed):
    rng = random.Random(seed); items = []
    for i in range(n):
        if i % 15 == 14:                                   # include prime questions too
            topic, q, opts, idx, expl = M.g_primes(rng)
        else:
            topic, q, ans, wrongs, expl = rng.choice(M.GENS)(rng)
            opts, idx = M.mcq(ans, wrongs, rng)
        items.append({"subject": "maths", "question": q, "options": opts,
                      "answer": chr(65 + idx), "_check": {"kind": "maths"}})
    return items


def gen_vr(n, seed):
    return V.generate(n, seed)


def gen_english(n, seed):
    return E.generate(n, seed)


def _rotation_item(seed):
    assign, ref, opts, idx = N.make_rotation_question_full(seed)
    return {"subject": "nvr", "type": "cube_rotation", "answer": chr(65 + idx),
            "_check": {"kind": "cube_rotation", "assign": assign, "ref": ref,
                       "opts": opts, "idx": idx}}


def gen_nvr(n, seed):
    rng = random.Random(seed); items = []
    names = [x for x in N.NETS if N.fold_face_ids(N.NETS[x])]
    for i in range(n):
        if i % 2 == 0:
            name = rng.choice(names)
            syms, opts, idx = N.make_net_question(N.NETS[name], seed * 97 + i)
            items.append({"subject": "nvr", "type": "cube_net", "answer": chr(65 + idx),
                          "_check": {"kind": "cube_net", "cells": N.NETS[name], "syms": syms,
                                     "opts": opts, "idx": idx}})
        else:
            items.append(_rotation_item(seed * 97 + i))
    return items


# ---------------- testers (independent) ----------------
# The testers live in testers.py and deliberately do NOT reuse the generators'
# answer logic: Maths is re-solved from the question text, NVR nets are folded
# with separate 3D geometry and judged with an orientation test.
from testers import test_maths, test_vr, test_nvr, test_english   # noqa: E402


def maths_profile_match(items):
    text = " ".join(it["question"] + " " + " ".join(it["options"]) for it in items)
    hist = {}
    for nnum in re.findall(r"\b\d[\d,]*\.?\d*\b", text):
        d = len(nnum.replace(",", "").replace(".", "").lstrip("0") or "0")
        hist[d] = hist.get(d, 0) + 1
    tot = sum(hist.values()) or 1
    diff = sum(abs(round(100 * hist.get(d, 0) / tot) - REAL_DIGITS[d]) for d in REAL_DIGITS)
    return max(0, 100 - diff)          # % closeness to real digit profile


PIPELINE = {
    "maths":   (gen_maths, test_maths),
    "vr":      (gen_vr, test_vr),
    "nvr":     (gen_nvr, test_nvr),
    "english": (gen_english, test_english),
}


def hardword_pct(items):
    words = re.findall(r"[A-Za-z]{2,}",
                       " ".join(it["question"] + " " + " ".join(it["options"]) for it in items))
    return round(100 * sum(len(w) >= 8 for w in words) / max(1, len(words)))


def run_subject(name, n, seed):
    gen, test = PIPELINE[name]
    items = gen(n, seed)
    ok, total = test(items)
    if name == "maths":
        extra = f"  | number-size match to real: {maths_profile_match(items)}%"
    elif name in ("vr", "english"):
        extra = f"  | vocab tier: {hardword_pct(items)}% long words (real ~11%)"
    else:
        extra = "  | (visual — not auto-profiled; types matched to real)"
    return name, ok, total, extra


def main(rounds=3, n=60):
    print(f"4 generators + 4 testers, SIMULTANEOUS, {rounds} rounds "
          f"({n}/subject, {n//2} for NVR):\n")
    for r in range(1, rounds + 1):
        with ThreadPoolExecutor(max_workers=4) as ex:
            futs = [ex.submit(run_subject, s, n if s != "nvr" else n // 2, r * 1000 + i)
                    for i, s in enumerate(PIPELINE)]
            res = {f.result()[0]: f.result() for f in futs}
        print(f"── round {r} ──")
        for s in ("maths", "vr", "nvr", "english"):
            _, ok, tot, extra = res[s]
            print(f"   {s:8s}: {ok}/{tot} verified{extra}")
    print("\n'verified' = tester independently confirmed the answer "
          "(English = key + ambiguity checks, not proof).")


if __name__ == "__main__":
    main()
