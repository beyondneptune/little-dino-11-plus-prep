#!/usr/bin/env python3
"""Full harness for the rule-based English generators (scripts/english_rulegen.py):
per type, run the STRUCTURAL flaw classes (wrong key, two correct answers) and the
AMBIGUITY flaw classes (a second genuinely-valid option), and report the catch
rate of each. A type is 'servable' only if clean pass AND every applicable flaw
clear the 99% bar. Writes reports/english_rulegen_harness.md.
"""
from __future__ import annotations

import copy

import english_rulegen as R

N = 200
BAR = 99.0


def _ai(it):
    return ord(it["answer"]) - 65


def flaw_wrong_key(it, _):
    f = copy.deepcopy(it); f["answer"] = chr(65 + (_ai(it) + 1) % 4); return f


def flaw_two_correct(it, _):
    f = copy.deepcopy(it); i = _ai(it); f["options"][(i + 1) % 4] = f["options"][i]; return f


def flaw_second_valid(it, kind):
    """Insert a DIFFERENT genuinely-valid option (only possible for spelling, where
    a second real word exists). For the other types the answer is unique, so this
    flaw cannot be built -> reported n/a."""
    if kind != "spelling":
        return None
    f = copy.deepcopy(it)
    marked = f["options"][_ai(f)]
    other = next((w for w in R.VALID_WORDS if w not in f["options"]), None)
    if other is None:
        return None
    f["options"][(_ai(f) + 1) % 4] = other              # now two real words
    return f


def _rate(items, planter, check, kind):
    flawed = [planter(it, kind) for it in items]
    flawed = [x for x in flawed if x is not None]
    if not flawed:
        return None
    caught = sum(1 for x in flawed if not check(x))
    return 100.0 * caught / len(flawed)


def measure():
    rows = []
    for kind, (_gen, check) in R.TYPES.items():
        items = R.generate(kind, N, 1)
        clean = 100.0 * sum(check(it) for it in items) / len(items)
        wk = _rate(items, flaw_wrong_key, check, kind)
        tc = _rate(items, flaw_two_correct, check, kind)
        amb = _rate(items, flaw_second_valid, check, kind)
        applicable = [v for v in (wk, tc, amb) if v is not None]
        servable = clean >= 99 and all(v >= BAR for v in applicable)
        rows.append((kind, len(items), clean, wk, tc, amb, servable))
    return rows


def report(rows):
    def c(v):
        return "n/a" if v is None else f"{v:.1f}%"
    lines = ["# Rule-based English — full harness (structural + ambiguity)", "",
             f"{N} items per type. A type is servable only if clean pass AND every applicable "
             f"flaw clear {BAR:.0f}%. Ambiguity (a second genuinely-valid option) can only be "
             "constructed for spelling (two real words); for the other types the answer is unique "
             "by the vetted data, so that class is n/a.", "",
             "| Type | Clean | wrong_key | two_correct | ambiguity(2nd valid) | Servable? |",
             "|---|---|---|---|---|---|"]
    serv = []
    for kind, n, clean, wk, tc, amb, servable in rows:
        lines.append(f"| {kind} | {clean:.0f}% | {c(wk)} | {c(tc)} | {c(amb)} | "
                     f"{'✅ yes' if servable else '❌ no'} |")
        if servable:
            serv.append(kind)
    lines += ["", f"**Servable types (clear both bars): {', '.join(serv) or 'none'}.**",
              "", "Synonym/antonym multiple choice stay UNSERVED until a vetted sense-cluster "
              "list passes the ambiguity check (currently ~26%, reports/english_ambiguity.md)."]
    from pathlib import Path
    out = Path(__file__).resolve().parent.parent / "reports" / "english_rulegen_harness.md"
    out.write_text("\n".join(lines) + "\n")
    return out, serv


if __name__ == "__main__":
    rows = measure()
    out, serv = report(rows)
    for kind, n, clean, wk, tc, amb, servable in rows:
        print(f"{kind:12} clean={clean:5.0f}  wk={'n/a' if wk is None else f'{wk:.0f}'}  "
              f"tc={'n/a' if tc is None else f'{tc:.0f}'}  amb={'n/a' if amb is None else f'{amb:.0f}'}  "
              f"{'SERVABLE' if servable else '-'}")
    print("servable:", serv, "->", out)
