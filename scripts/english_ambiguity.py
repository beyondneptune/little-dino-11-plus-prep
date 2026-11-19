#!/usr/bin/env python3
"""Ambiguity harness (parent Checkpoint 6, Addendum B). The structural harness
(english_measure.py) shows the checker catches wrong keys and duplicate answers
100%. That is NOT evidence the items are sound. This harness plants the flaws the
structural one can't see — a SECOND genuinely-correct answer, an acceptable
alternative, or a "wrong" spelling option that is actually a valid variant — and
reports the catch rate SEPARATELY. Language stays unserved until THIS bar is met.
"""
from __future__ import annotations

import copy
from collections import Counter

import testers as T
import vocab
import vr_gen as V

N = 200

# a small curated list of genuine spelling VARIANTS (both acceptable English) —
# used to plant a "the wrong option is actually valid" flaw for spelling items.
VALID_VARIANTS = {
    "colour": "color", "realise": "realize", "organise": "organize",
    "favourite": "favorite", "travelling": "traveling", "grey": "gray",
    "practise": "practice", "judgement": "judgment", "cosy": "cozy",
}
VARIANTS = {**VALID_VARIANTS, **{v: k for k, v in VALID_VARIANTS.items()}}


def _gen_vr(kind, n):
    out, seed = [], 0
    while len(out) < n and seed < n * 60:
        seed += 1
        for it in V.generate(40, seed):
            if it.get("_check", {}).get("kind") == kind:
                out.append(it)
    return out[:n]


def _ans_idx(it):
    return ord(it["answer"]) - 65


# ---- ambiguity planters -----------------------------------------------------
_POOL = sorted({w for pair in vocab.SYN for w in pair}
               | {w for ws in vocab.CATS.values() for w in ws})


def plant_second_synonym(it):
    """Replace a distractor with ANOTHER word that is a true synonym of the clue
    (per the word list) — now two options are correct. A sound checker rejects."""
    if it["_check"]["kind"] != "word_analogy" or it["_check"]["rel"] != "syn":
        return None
    clue = it["_check"]["pair"][0]
    ans = it["options"][_ans_idx(it)]
    for w in _POOL:
        if w not in it["options"] and w != ans and vocab.same_meaning(w, clue):
            f = copy.deepcopy(it)
            f["options"][(_ans_idx(f) + 1) % 4] = w
            return f
    return None


def plant_second_odd(it):
    """Make a SECOND word that is also 'odd' for its own reason -> ambiguous."""
    if it["_check"]["kind"] != "odd_word":
        return None
    cats_of = lambda w: {n for n, ws in vocab.CATS.items() if w in ws}
    used = set()
    for o in it["options"]:
        used |= cats_of(o)
    for name, ws in vocab.CATS.items():
        if name not in used and ws:
            f = copy.deepcopy(it)
            f["options"][(_ans_idx(f) + 1) % 4] = sorted(ws)[0]
            return f
    return None


def plant_valid_variant_spelling(it):
    """For a spelling item, replace a 'wrong' option with a VALID spelling variant
    of the correct word (e.g. colour/color) -> two acceptable options."""
    if it["_check"]["kind"] != "spelling":
        return None
    ans = it["options"][_ans_idx(it)].lower()
    if ans not in VARIANTS:
        return None
    f = copy.deepcopy(it)
    f["options"][(_ans_idx(f) + 1) % 4] = VARIANTS[ans]
    return f


AMBIG = {
    "word_analogy": [("second_correct_synonym", plant_second_synonym)],
    "odd_word": [("second_odd_one", plant_second_odd)],
    "spelling": [("valid_variant", plant_valid_variant_spelling)],
}


def measure():
    rows = []
    for kind, planters in AMBIG.items():
        items = _gen_vr(kind, N) if kind in ("word_analogy", "odd_word") else _gen_english(kind, N)
        for fname, planter in planters:
            flawed = [planter(it) for it in items]
            flawed = [x for x in flawed if x is not None]
            if not flawed:
                rows.append((kind, fname, 0, None, "no planted items (word list too small to build this flaw)"))
                continue
            check = T.check_vr_item if kind in ("word_analogy", "odd_word") else T.check_english_item
            caught = sum(1 for x in flawed if not check(x))
            rows.append((kind, fname, len(flawed), 100.0 * caught / len(flawed), ""))
    return rows


def _gen_english(kind, n):
    import english_gen as E
    out, seed = [], 0
    while len(out) < n and seed < n * 80:
        seed += 1
        for it in E.generate(40, seed):
            if it.get("_check", {}).get("kind") == kind:
                out.append(it)
    return out[:n]


def report(rows):
    lines = ["# English / VR — AMBIGUITY catch rates (separate from structural)", "",
             "Structural flaws (wrong key, duplicate answer) are caught 100% — that is NOT "
             "evidence the items are sound. These are the harder, realistic flaws: a genuine "
             "second correct answer, or a 'wrong' option that is actually valid. **Language stays "
             "unserved until these also clear the 99% bar with the evidence recorded.**", "",
             "| Type | Ambiguity flaw | Planted | Catch rate | Note |",
             "|---|---|---|---|---|"]
    for kind, fname, n, rate, note in rows:
        r = "n/a" if rate is None else f"{rate:.1f}%"
        lines.append(f"| {kind} | {fname} | {n} | {r} | {note} |")
    lines += ["", "## Reading",
              "- Where the word list KNOWS the alternative, the checker's uniqueness logic catches "
              "it. Where it does NOT (a real synonym/variant outside the curated list), the item "
              "passes undetected — so the true limit is **word-list completeness**, not the checker.",
              "- This is why language is not served: a 100% structural score hides an incomplete "
              "lexicon. The fix is bigger, sense-tagged, hand-audited word lists + a confusable/variant "
              "blocklist, then re-run this harness."]
    from pathlib import Path
    out = Path(__file__).resolve().parent.parent / "reports" / "english_ambiguity.md"
    out.write_text("\n".join(lines) + "\n")
    return out


if __name__ == "__main__":
    rows = measure()
    for kind, fname, n, rate, note in rows:
        print(f"{kind:14} {fname:22} planted={n:4} catch={'n/a' if rate is None else f'{rate:.0f}%'} {note}")
    print("written:", report(rows))
