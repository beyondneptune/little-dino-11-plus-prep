#!/usr/bin/env python3
"""Independent-audit export (Checkpoint-8 refresh). Writes reports/audit_sample.json:

  * 400 random SERVED questions across EVERY served bank — Maths (L1–L5), the six
    English SPaG types, Age 1/2/3 — stratified by (topic, level), NOT filtered.
    Each: stem, options, key, explanation, topic, level, verification, and (for
    typed-answer topics) example accepted typed forms.
  * the served NVR image items (prompt + answer index; options are figures).
  * each item tagged with its verification risk: lower = two independent methods
    (the L3–5 dual-verified types); higher = a single solver written from the same
    reading of the problem as the generator.

Deterministic (fixed seed) so the audit is reproducible.
"""
from __future__ import annotations

import glob
import json
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "platform"))
import answer_norm  # noqa: E402

OUT = ROOT / "reports" / "audit_sample.json"
SAMPLE_TOTAL = 400
SEED = 20261118
TYPED_TOPICS = {"MA-B06", "MA-F11", "EN-F01", "EN-F10"}


def _risk(qtype):
    # the L3-5 types have a forward solver AND a different-method cross-check
    return "lower (two independent methods)" if str(qtype).startswith("l35:") \
        else "higher (single same-reading solver)"


def _accepted_forms(key):
    """A few equivalent written forms the typed normaliser accepts (for the audit)."""
    p = answer_norm.parse(key)
    if not p:                                           # a word answer
        return [key, key.upper(), f" {key} "]
    v, kind, _u = p
    if kind == "money":
        return [key, key.replace("£", ""), str(float(v)).rstrip("0").rstrip("."),
                f"{int(v * 100)}p" if v.denominator in (1, 2, 4, 5, 10, 20, 25, 50, 100) else key]
    if kind == "percent":
        return [key, str(float(v)), f"{v.numerator}/{v.denominator}"]
    return [key, f" {key} ", f"0{key}"]                 # plain number


def _served_pairs():
    pairs = []
    for f in sorted(glob.glob(str(ROOT / "content" / "age*" / "banks" / "*__L*.json"))):
        age = int(Path(f).parent.parent.name.replace("age", ""))
        topic, lv = os.path.basename(f)[:-5].split("__L")
        pairs.append((age, topic, int(lv), f))
    return pairs


def _row(age, topic, level, q):
    key = q["options"][q["answer_index"]]
    row = {"age": age, "topic_id": topic, "level": level, "id": q.get("id"),
           "qtype": q.get("qtype"), "stem": q["stem"], "options": q["options"],
           "answer_index": q["answer_index"], "key": key,
           "explanation": q.get("explanation", ""),
           "verification": {"method": q.get("verification", {}).get("method"),
                            "checks": [c["name"] for c in q.get("verification", {}).get("checks", [])]},
           "risk": _risk(q.get("qtype"))}
    if topic in TYPED_TOPICS:
        row["typed"] = True
        row["accepted_typed_forms"] = _accepted_forms(key)
    return row


def build_sample():
    rng = random.Random(SEED)
    pairs = _served_pairs()
    per = max(1, SAMPLE_TOTAL // max(1, len(pairs)))
    sample, pool = [], []
    for age, topic, level, f in pairs:
        bank = json.loads(Path(f).read_text())
        rng.shuffle(bank)
        sample += [_row(age, topic, level, q) for q in bank[:per]]
        pool += [(age, topic, level, q) for q in bank[per:]]
    rng.shuffle(pool)
    for age, topic, level, q in pool:
        if len(sample) >= SAMPLE_TOTAL:
            break
        sample.append(_row(age, topic, level, q))
    rng.shuffle(sample)
    return sample[:SAMPLE_TOTAL], pairs


def _nvr_sample(rng, k=12):
    f = ROOT / "content" / "age1" / "nvr_bank.json"
    if not f.exists():
        return []
    bank = json.loads(f.read_text())
    out = []
    for topic, items in bank.items():
        for it in rng.sample(items, min(k, len(items))):
            out.append({"topic_id": topic, "type": it["type"], "prompt": it["prompt"],
                        "answer_index": it["answer_index"], "options": f"{len(it['options'])} image figures",
                        "explanation": it["explanation"], "risk": "higher (single same-reading solver)"})
    return out


def main():
    sample, pairs = build_sample()
    rng = random.Random(SEED)
    doc = {
        "generated": datetime.now(timezone.utc).isoformat(), "seed": SEED,
        "note": "Random SERVED questions across all banks (Maths L1-5, English SPaG, Ages 1-3), "
                "NOT filtered. NVR items are image-option (options described, not inlined). "
                "`risk` flags items whose generator and solver share a reading of the problem.",
        "served_pairs": [{"age": a, "topic": t, "level": lv, "count": len(json.loads(Path(f).read_text()))}
                         for a, t, lv, f in pairs],
        "sample_size": len(sample), "sample": sample,
        "nvr_sample": _nvr_sample(rng),
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1))
    from collections import Counter
    subj = Counter(r["topic_id"][:2] for r in sample)
    higher = sum(1 for r in sample if r["risk"].startswith("higher"))
    print(f"wrote {OUT.relative_to(ROOT)}: {len(sample)} Qs across {len(pairs)} (topic,level) pairs "
          f"+ {len(doc['nvr_sample'])} NVR")
    print("  by subject prefix:", dict(subj), "| typed items:",
          sum(1 for r in sample if r.get("typed")), "| higher-risk:", higher)


if __name__ == "__main__":
    main()
