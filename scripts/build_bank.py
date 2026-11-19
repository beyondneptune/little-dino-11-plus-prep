#!/usr/bin/env python3
"""
Build verified question banks for the Age-1 topics that can be served today,
PER LEVEL (parent STEP 1b). Topics, levels, generators and solvers all come from
scripts/registry.py. Every item passes the independent verifier + serve gate;
only servable, de-duplicated items are kept. A (topic, level) that cannot reach
MIN_BANK is reported and not served — a child is never shown a level with no
verified content.

Raw banks (content/age1/banks/<topic>__L<n>.json) are deterministic and
git-ignored; content/age1/bank_manifest.yaml (per-topic, per-level counts +
samples) is committed.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import yaml

import registry as R
import verify_computable as VC

ROOT = Path(__file__).resolve().parent.parent
MIN_BANK = 60
TARGET = 150
AGES = (1, 2, 3)                      # ages with playable content today


def _topic_age():
    topics = yaml.safe_load((ROOT / "content" / "topics.yaml").read_text())["topics"]
    return {t["id"]: t["age"] for t in topics if t["content_readiness"] == "V"}


def _v_entries_for_age(age):
    ta = _topic_age()
    return [e for e in R.REGISTRY if ta.get(e.topic) == age]


def build_one(entry, level, target=TARGET):
    """Return servable, de-duplicated Question objects for one (topic, level)."""
    rng = random.Random(hash((entry.topic, entry.qtype, level)) & 0xFFFFFFFF)
    seen, bank, scanned = set(), [], 0
    while len(bank) < target and scanned < target * 120:
        scanned += 1
        it = entry.make(rng, level)
        if it is None:
            continue
        q = VC.make_question(entry.subject, it, entry.topic, entry.qtype, level,
                             f"reg:{entry.qtype}", 1, scanned)
        if not q.servable():
            continue
        h = q.content_hash()
        if h in seen:
            continue
        seen.add(h)
        bank.append(q)
    return bank


def build_age(age):
    banks = ROOT / "content" / f"age{age}" / "banks"
    banks.mkdir(parents=True, exist_ok=True)
    manifest = {"age": age, "min_bank": MIN_BANK, "topics": {}}
    served, short = [], []
    for entry in _v_entries_for_age(age):
        tinfo = manifest["topics"].setdefault(
            entry.topic, {"subject": entry.subject, "generator": entry.qtype, "levels": {}})
        for level in entry.levels:
            bank = build_one(entry, level)
            (banks / f"{entry.topic}__L{level}.json").write_text(
                json.dumps([q.to_dict() for q in bank], ensure_ascii=False, indent=1))
            ok = len(bank) >= MIN_BANK
            tinfo["levels"][level] = {"count": len(bank), "served": ok,
                                      "samples": [{"stem": q.stem, "answer": q.options[q.answer_index]}
                                                  for q in bank[:2]]}
            (served if ok else short).append(f"{entry.topic} L{level} ({len(bank)})")
    (ROOT / "content" / f"age{age}" / "bank_manifest.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True))
    return served, short


def main():
    for age in AGES:
        served, short = build_age(age)
        print(f"age {age} served:", served)
        if short:
            print(f"  age {age} below MIN_BANK:", short)


if __name__ == "__main__":
    main()
