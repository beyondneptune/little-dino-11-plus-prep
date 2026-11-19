#!/usr/bin/env python3
"""
Planted-bug corpus + catch-rate measurement (brief 5c; AUTONOMOUS_PROMPT 5a/5c).

For each subject and each applicable flaw, plant the flaw into many genuine items
and measure what fraction the verifier REJECTS (the catch rate). Also measure the
false-reject rate on un-mutated items (must be 0). A catch rate below its
threshold means the verifier is not trustworthy for that flaw.

This measures the DETERMINISTIC verifiers (testers.py) we have today. Language-
judgement flaws that need the not-yet-built blind-solve/adversarial pipeline
(e.g. a synonym distractor on comprehension, off-level reading, factual errors)
are listed as PENDING; their types stay `not_served` until that pipeline exists
and is measured (DECISIONS).
"""
from __future__ import annotations

import copy
from collections import Counter
from datetime import date
from pathlib import Path

import english_gen as E
import train_all as TA
import verify_computable as VC
import vocab

ROOT = Path(__file__).resolve().parent.parent
ALL_WORDS = sorted({w for grp in vocab._CL.values() for w in grp})
ED_WORDS = ["walked", "jumped", "played", "asked", "wanted", "looked", "carried", "opened"]


# ---------------- flaws (return a mutated copy, or None if N/A) -------------
def flip_key(it):
    opts = VC._options(it)
    if len(opts) < 2:
        return None
    it = copy.deepcopy(it)
    i = ord(it["answer"]) - 65
    it["answer"] = chr(65 + (i + 1) % len(opts))
    if it.get("_check", {}).get("kind") in (None,) or "idx" in it.get("_check", {}):
        # NVR keeps its answer in _check['idx']; leave idx, only the letter moved,
        # which is exactly the "served key disagrees with solver" flaw.
        pass
    return it


def duplicate_option(it):
    if not it.get("options") or len(it["options"]) < 2:
        return None
    it = copy.deepcopy(it)
    a = ord(it["answer"]) - 65
    j = (a + 1) % len(it["options"])
    it["options"][j] = it["options"][a]            # two options now equal the key
    return it


def synonym_distractor(it):
    if it.get("_check", {}).get("kind") != "synonym":
        return None
    w = it["_check"]["w"]
    opts = it["options"]
    key = opts[ord(it["answer"]) - 65]
    for cand in ALL_WORDS:
        if cand not in opts and cand != key and vocab.same_meaning(cand, w):
            it = copy.deepcopy(it)
            a = ord(it["answer"]) - 65
            j = next(k for k in range(len(it["options"])) if k != a)
            it["options"][j] = cand                # a second valid synonym of w
            return it
    return None


def realword_for_misspelling(it):
    if it.get("_check", {}).get("kind") != "spelling":
        return None
    opts = it["options"]
    a = ord(it["answer"]) - 65
    for cand in ALL_WORDS:
        if cand not in opts:
            it = copy.deepcopy(it)
            j = next(k for k in range(len(it["options"])) if k != a)
            it["options"][j] = cand                # a real word among the misspellings
            return it
    return None


def extra_ed_grammar(it):
    if it.get("_check", {}).get("kind") != "grammar_agree":
        return None
    opts = it["options"]
    a = ord(it["answer"]) - 65
    for cand in ED_WORDS:
        if cand not in opts:
            it = copy.deepcopy(it)
            j = next(k for k in range(len(it["options"])) if k != a)
            it["options"][j] = cand                # a second grammatical (past-tense) form
            return it
    return None


GENERIC = [("wrong_key", flip_key), ("duplicate_option", duplicate_option)]
ENGLISH_SPECIFIC = [("synonym_distractor", synonym_distractor),
                    ("realword_misspelling", realword_for_misspelling),
                    ("ambiguous_grammar", extra_ed_grammar)]

# catch-rate thresholds (DECISIONS): deterministic verifiers must catch 100%.
THRESHOLD = 1.0


def _pool(subject, target):
    items, seed = [], 1
    gen = {"maths": TA.gen_maths, "vr": TA.gen_vr,
           "english": TA.gen_english, "nvr": TA.gen_nvr}[subject]
    while len(items) < target:
        items += gen(60 if subject != "nvr" else 30, seed)
        seed += 1
    return items


def measure(target=250):
    results = {}
    # false-reject (control): genuine items must verify
    for subject in ("maths", "vr", "nvr", "english"):
        pool = _pool(subject, target)
        bad = sum(0 if VC.verify(subject, it).ok else 1 for it in pool[:target])
        results[(subject, "control_false_reject")] = {"n": target, "caught": bad,
                                                       "rate": bad / target}
    # planted flaws — keep generating fresh items until `target` flaws are planted
    # (rare types like grammar-agreement need a bigger pool), with a hard cap.
    gens = {"maths": TA.gen_maths, "vr": TA.gen_vr,
            "english": TA.gen_english, "nvr": TA.gen_nvr}
    plans = [(s, name, fn) for s in ("maths", "vr", "nvr", "english") for name, fn in GENERIC]
    plans += [("english", name, fn) for name, fn in ENGLISH_SPECIFIC]
    for subject, name, fn in plans:
        gen = gens[subject]
        planted = caught = 0
        seed = 1000
        while planted < target and seed < 1000 + 4000:
            for it in gen(60 if subject != "nvr" else 30, seed):
                m = fn(it)
                if m is None:
                    continue
                planted += 1
                if not VC.verify(subject, m).ok:
                    caught += 1
                if planted >= target:
                    break
            seed += 1
        if planted:
            results[(subject, name)] = {"n": planted, "caught": caught,
                                        "rate": caught / planted}
    return results


def report(results):
    lines = [f"# Catch rates — planted-bug corpus ({date.today()})", "",
             "Deterministic verifiers (testers.py). Catch rate = fraction of planted",
             "flawed items REJECTED. Control = genuine items wrongly rejected (want 0).",
             "Threshold for these deterministic checks = 100%.", "",
             "| Subject | Flaw | planted | caught | catch rate |",
             "|---|---|---|---|---|"]
    for (subject, name), r in sorted(results.items()):
        lines.append(f"| {subject} | {name} | {r['n']} | {r['caught']} | "
                     f"{100*r['rate']:.1f}% |")
    lines += ["", "## Pending (need the blind-solve/adversarial language pipeline)",
              "- two-defensible-answer on comprehension/cloze, off-level reading, factual",
              "  errors on authored passages. Those R types stay `not_served` until the",
              "  pipeline is built and its catch rate is measured here."]
    out = "\n".join(lines) + "\n"
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / f"catch_rates_{date.today()}.md").write_text(out)
    return out


if __name__ == "__main__":
    res = measure()
    print(report(res))
