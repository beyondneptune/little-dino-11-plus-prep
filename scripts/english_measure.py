#!/usr/bin/env python3
"""English / Verbal-Reasoning MEASUREMENT harness (parent Checkpoint 5, measure
before building). For each item type we generate clean items, PLANT a known flaw
(wrong key, two correct answers, ambiguous wording, bad spelling, grammar error),
run the existing data-based checker, and report the **catch rate** (fraction of
flawed items the checker rejects) plus the **cost** (time) per verified item.

Nothing here is served. The point is to find, with numbers, which types the
current rule/word-list checker already guards to >= 99% and which need a stronger
(still data-based, no language-model judgement) generator before they could be.
"""
from __future__ import annotations

import copy
import time
from collections import defaultdict

import english_gen as E
import testers as T
import vr_gen as V

N = 200
THRESHOLD = 99.0

# item kind -> (subject, checker)
KINDS = {
    "synonym": ("english", T.check_english_item),
    "antonym": ("english", T.check_english_item),
    "grammar_agree": ("english", T.check_english_item),
    "spelling": ("english", T.check_english_item),
    "odd_word": ("vr", T.check_vr_item),
    "word_analogy": ("vr", T.check_vr_item),
    # computable VR included as a control (should catch ~everything)
    "letter_series": ("vr", T.check_vr_item),
    "number_series": ("vr", T.check_vr_item),
}


def _gen(kind, n):
    out, seed = [], 0
    src = E.generate if KINDS[kind][0] == "english" else V.generate
    while len(out) < n and seed < n * 60:
        seed += 1
        for it in src(40, seed):
            if it.get("_check", {}).get("kind") == kind:
                out.append(it)
                if len(out) >= n:
                    break
    return out


def _letter(it, idx):
    return chr(65 + idx)


def _ans_idx(it):
    return ord(it["answer"]) - 65


# ---- flaw planters: return a flawed copy, or None if not applicable ----------
def flaw_wrong_key(it):
    f = copy.deepcopy(it)
    f["answer"] = _letter(f, (_ans_idx(f) + 1) % 4)      # point at a wrong option
    return f


def flaw_two_correct(it):
    f = copy.deepcopy(it)
    j = (_ans_idx(f) + 1) % 4
    f["options"][j] = f["options"][_ans_idx(f)]          # duplicate the answer value
    return f


def flaw_bad_spelling(it):
    f = copy.deepcopy(it)
    i = _ans_idx(f); w = f["options"][i]
    if len(w) < 3 or not w.isalpha():
        return None
    f["options"][i] = w[:1] + w[2] + w[1] + w[3:]        # transpose two letters
    return f


def flaw_ambiguous(it):
    """Add a second valid answer where the type allows it (word types)."""
    k = it["_check"]["kind"]
    f = copy.deepcopy(it)
    import vocab
    i = _ans_idx(f); ans = f["options"][i]
    j = (i + 1) % 4
    if k == "odd_word":
        # make a second 'odd' by inserting a word from a brand-new category
        used = {next(iter({n for n, ws in vocab.CATS.items() if o in ws}), None) for o in f["options"]}
        for name, ws in vocab.CATS.items():
            if name not in used and ws:
                f["options"][j] = sorted(ws)[0]
                return f
        return None
    if k == "word_analogy":
        rel = it["_check"]["rel"]; c1 = it["_check"]["pair"][0]
        pool = vocab.ALL if hasattr(vocab, "ALL") else []
        for w in pool:
            if w in f["options"]:
                continue
            ok = vocab.same_meaning(w, c1) if rel == "syn" else vocab.opposite_of(c1, w)
            if ok:
                f["options"][j] = w
                return f
        return None
    return None


def flaw_grammar(it):
    if it["_check"]["kind"] != "grammar_agree":
        return None
    f = copy.deepcopy(it)
    f["answer"] = _letter(f, (_ans_idx(f) + 1) % 4)      # pick the non-agreeing option
    return f


FLAWS = {"wrong_key": flaw_wrong_key, "two_correct": flaw_two_correct,
         "bad_spelling": flaw_bad_spelling, "ambiguous": flaw_ambiguous,
         "grammar_error": flaw_grammar}


def measure():
    rows = []
    cost = {}
    for kind, (subj, check) in KINDS.items():
        items = _gen(kind, N)
        if not items:
            continue
        t0 = time.perf_counter()
        clean_pass = sum(1 for it in items if check(it))
        cost[kind] = (time.perf_counter() - t0) / max(1, len(items))
        per_flaw = {}
        for fname, planter in FLAWS.items():
            flawed = [planter(it) for it in items]
            flawed = [x for x in flawed if x is not None]
            if not flawed:
                per_flaw[fname] = None       # not applicable
                continue
            caught = sum(1 for x in flawed if not check(x))
            per_flaw[fname] = 100.0 * caught / len(flawed)
        rows.append((kind, subj, len(items), 100.0 * clean_pass / len(items), per_flaw))
    return rows, cost


def report(rows, cost):
    lines = ["# English / VR verification — measurement report", "",
             f"Harness: {N} items per type; each flaw planted on every item; the data-based "
             "checker's **catch rate** (% of flawed items rejected) is shown. No language-model "
             "judgement is used, and **nothing here is served**.", "",
             f"A type is *guardable today* only if it catches **>= {THRESHOLD:.0f}%** of every "
             "applicable flaw. Clean items should pass ~100%.", "",
             "| Type | Subject | Clean pass | wrong_key | two_correct | bad_spelling | ambiguous | grammar | Guardable? |",
             "|---|---|---|---|---|---|---|---|---|"]
    guard = {}
    for kind, subj, n, clean, pf in rows:
        def cell(v):
            return "n/a" if v is None else f"{v:.1f}%"
        applicable = [v for v in pf.values() if v is not None]
        ok = clean >= 99 and all(v >= THRESHOLD for v in applicable)
        guard[kind] = ok
        lines.append(f"| {kind} | {subj} | {clean:.0f}% | {cell(pf['wrong_key'])} | "
                     f"{cell(pf['two_correct'])} | {cell(pf['bad_spelling'])} | "
                     f"{cell(pf['ambiguous'])} | {cell(pf['grammar_error'])} | "
                     f"{'✅ yes' if ok else '❌ no'} |")
    lines += ["", "## Cost per item (data-based checker, no tokens)",
              "| Type | seconds/item |", "|---|---|"]
    for k, c in cost.items():
        lines.append(f"| {k} | {c*1000:.3f} ms |")
    reach = [k for k, v in guard.items() if v]
    miss = [k for k, v in guard.items() if not v]
    lines += ["", "## Verdict",
              f"- **Reach >= {THRESHOLD:.0f}% on all applicable flaws:** {', '.join(reach) or 'none'}.",
              f"- **Not yet guardable:** {', '.join(miss) or 'none'}.",
              "", "## Proposed data-based generators (no language-model judgement) to close gaps",
              "- **Synonym/antonym:** generate ONLY from a curated thesaurus with explicit "
              "sense tags and a hand-checked 'confusable' blocklist, so a distractor can never be a "
              "second correct answer; verify both directions against the word list.",
              "- **Spelling:** draw from a fixed misspelling list (one correct, three attested "
              "misspellings) so 'bad_spelling' is the item, not a flaw — checker confirms exactly "
              "one dictionary word.",
              "- **Grammar agreement:** rule-based subject/verb and determiner agreement over a "
              "closed template set; the checker re-derives the only grammatical option.",
              "- **Comprehension / inference:** NOT data-based — needs the blind-solve + adversarial "
              "LLM pipeline; stays unserved until that is built and measured here."]
    from pathlib import Path
    out = Path(__file__).resolve().parent.parent / "reports" / "english_measurement.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines) + "\n")
    return out, guard


if __name__ == "__main__":
    rows, cost = measure()
    out, guard = report(rows, cost)
    for kind, subj, n, clean, pf in rows:
        print(f"{kind:16} clean={clean:5.0f}%  " +
              "  ".join(f"{k}={'n/a' if v is None else f'{v:.0f}%'}" for k, v in pf.items()))
    print("written:", out)
