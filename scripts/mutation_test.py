#!/usr/bin/env python3
"""
Mutation testing of the generator AND solver CODE (parent STEP 1d).

The planted-bug corpus (planted_corpus.py) scoring 100% proves little on its own,
because the same author wrote the generator and the solver. This harness injects
bugs into the actual code and measures whether the OTHER half catches them:

  * generator bugs (off-by-one key, wrong rounding, duplicate options, wrong key)
    should be caught by the INDEPENDENT solver -> the item is rejected;
  * solver/checker bugs (off-by-one, blind spot, always-accept) should be caught
    because genuine items stop verifying, or a known-wrong item starts verifying.

It also includes the HONEST blind spot: a bug present in BOTH the generator and
the solver (the same rounding tie-break convention) is NOT caught — two agreeing
halves can be wrong together. That is reported, not hidden.
"""
from __future__ import annotations

import contextlib
import copy
import random
from datetime import date
from pathlib import Path

import age1_gen as A1
import maths_gen as M
import testers as T
import verify_computable as VC

ROOT = Path(__file__).resolve().parent.parent


def _items(gen, n, level=1, seed=7):
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        q, ans, wrongs, expl = gen(rng, level)
        try:
            opts, idx = M.mcq(ans, wrongs, rng)
        except ValueError:
            continue
        out.append({"question": q, "options": opts, "answer": chr(65 + idx),
                    "_check": {"kind": "maths"}})
    return out


@contextlib.contextmanager
def _patch(obj, name, fn):
    old = getattr(obj, name)
    setattr(obj, name, fn)
    try:
        yield
    finally:
        setattr(obj, name, old)


# ---- generator bugs (always wrong) — the solver must reject them -------------
def _gen_bug(wrap, n=100, level=1):
    items = _items(wrap, n, level)
    rejected = sum(1 for it in items if not VC.verify("maths", it).ok)
    return rejected / len(items)


def _off_by_one(gen):
    return lambda rng, level=1: (lambda r: (r[0], r[1] + 1, r[2], r[3]))(gen(rng, level))


def _round_wrong(rng, level=1):
    q, ans, wrongs, expl = A1.g_round(rng, level)
    return q, ans + (10 if level == 1 else 100), wrongs, expl   # wrong rounding


def _dup_option_caught(n=100):
    bad = 0
    for it in _items(A1.g_mental_single, n):
        it = copy.deepcopy(it)
        it["options"][1] = it["options"][0]          # duplicate option
        if not VC.verify("maths", it).ok:
            bad += 1
    return bad / n


def _wrong_label_caught(n=100):
    bad = 0
    for it in _items(A1.g_div_fact, n):
        it = copy.deepcopy(it)
        a = ord(it["answer"]) - 65
        it["answer"] = chr(65 + (a + 1) % len(it["options"]))   # flip the key
        if not VC.verify("maths", it).ok:
            bad += 1
    return bad / n


# ---- solver/checker bugs — genuine items must stop verifying / wrong accepted
def _solver_bug_caught(patch_obj, patch_name, fn):
    genuine = _items(A1.g_mental_single, 60) + _items(A1.g_round, 40)
    probe = _items(A1.g_div_fact, 1)[0]
    bad = copy.deepcopy(probe)
    a = ord(bad["answer"]) - 65
    bad["answer"] = chr(65 + (a + 1) % len(bad["options"]))      # a known-wrong item
    with _patch(patch_obj, patch_name, fn):
        genuine_rejected = sum(1 for it in genuine if not VC.verify("maths", it).ok)
        wrong_accepted = VC.verify("maths", bad).ok
    return genuine_rejected > 0 or wrong_accepted


# ---- the honest blind spot: a bug in BOTH halves (shared rounding convention)
def _shared_bug_caught():
    # "Round 25 to the nearest 10": correct (round half up) = 30. A half-DOWN
    # convention gives 20. Put 20 as the key AND make the solver round half down.
    def solve_halfdown(q):
        import re
        from fractions import Fraction
        m = re.fullmatch(r"Round (\d+) to the nearest (\d+)\.", q)
        if m:
            n, base = int(m[1]), int(m[2])
            return Fraction((n + base // 2 - 1) // base * base)   # ties go down
        return T.__wrapped_solve(q) if hasattr(T, "__wrapped_solve") else None
    item = {"question": "Round 25 to the nearest 10.",
            "options": ["20", "30", "10", "25"], "answer": "A",  # keyed to 20 (wrong)
            "_check": {"kind": "maths"}}
    with _patch(T, "solve_maths", solve_halfdown):
        accepted = VC.verify("maths", item).ok
    return not accepted   # caught only if the verifier rejects the shared-wrong item


def measure():
    results = []
    results.append(("generator: off-by-one key (mental)", "generator",
                    _gen_bug(_off_by_one(A1.g_mental_single))))
    results.append(("generator: off-by-one key (division)", "generator",
                    _gen_bug(_off_by_one(A1.g_div_fact))))
    results.append(("generator: wrong rounding", "generator", _gen_bug(_round_wrong)))
    results.append(("generator: duplicate option", "generator", _dup_option_caught()))
    results.append(("generator: wrong answer label", "generator", _wrong_label_caught()))
    results.append(("solver: off-by-one", "solver",
                    1.0 if _solver_bug_caught(T, "solve_maths",
                    lambda q, _o=T.solve_maths: (_o(q) + 1 if _o(q) is not None else None)) else 0.0))
    results.append(("solver: returns nothing", "solver",
                    1.0 if _solver_bug_caught(T, "solve_maths", lambda q: None) else 0.0))
    results.append(("checker: always accepts", "checker",
                    1.0 if _solver_bug_caught(T, "check_maths_item", lambda it: (True, "")) else 0.0))
    results.append(("SHARED generator+solver: round-half-down", "blind-spot",
                    1.0 if _shared_bug_caught() else 0.0))
    return results


def report(results):
    lines = [f"# Mutation testing — generator & solver code ({date.today()})", "",
             "Each row injects a bug into the real code and checks whether the OTHER",
             "half catches it. 1.00 = caught. The last row is the HONEST blind spot:",
             "a bug shared by both halves is not caught.", "",
             "| Mutation | Where | Caught |", "|---|---|---|"]
    for name, where, rate in results:
        lines.append(f"| {name} | {where} | {rate:.2f} |")
    shared = next(r for n, w, r in results if w == "blind-spot")
    lines += ["", "## What this CANNOT catch (honest)",
              "- A bug present in BOTH the generator and the solver (same rounding",
              f"  tie-break convention above: caught = {shared:.2f}). Two agreeing halves",
              "  can be wrong together. Mitigation: pin conventions explicitly, and where",
              "  cheap add a third independent reference (e.g. a different rounding impl).",
              "- Whether a question is well-pitched, interesting, or at the right level —",
              "  that is a human/pedagogical judgement, not a correctness check.",
              "- Ambiguity in language items (handled by the separate language pipeline)."]
    out = "\n".join(lines) + "\n"
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / f"mutation_{date.today()}.md").write_text(out)
    return out


if __name__ == "__main__":
    print(report(measure()))
