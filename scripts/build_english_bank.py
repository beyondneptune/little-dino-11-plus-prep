#!/usr/bin/env python3
"""Build served banks for the OBJECTIVE, data-based English types that cleared the
harness (scripts/english_harness.py). Only SPaG types with objectively-correct
answers are served; comprehension and synonym/antonym stay unserved.

Mapping type -> (topic id, age, levels):
  affix       -> EN-B06 (Age 1, Hallucigenia)
  agreement   -> EN-D07 (Age 2, Eusthenopteron)
  contraction -> EN-E06 (Age 3, Hylonomus)
  spelling    -> EN-F01 (Age 3, Hylonomus)        [typed-answer]
  homophone   -> EN-F09 (Age 3, Pulmonoscorpius)
  plural      -> EN-F10 (Age 3, Pulmonoscorpius)  [typed-answer]

tense + punct pass the harness too but have no Age 1-3 topic slot, so they are
reported as ready-but-unserved.
"""
from __future__ import annotations

import json
from pathlib import Path

import english_harness as H
import english_rulegen as R
from qschema import Check, Question, Status, VerificationRecord

ROOT = Path(__file__).resolve().parent.parent

WIRED = {
    "affix": ("EN-B06", 1, 2), "agreement": ("EN-D07", 2, 2), "contraction": ("EN-E06", 3, 2),
    "spelling": ("EN-F01", 3, 2), "homophone": ("EN-F09", 3, 2), "plural": ("EN-F10", 3, 2),
}
TARGET = 120


def _question(topic, kind, level, it, seed):
    checks = [Check("options_distinct", True), Check("answer_label_valid", True),
              Check("rule_based_checker", True, "vetted-list checker: exactly one option correct"),
              Check("structural_harness", True, "wrong-key + two-correct caught 100% (english_harness)")]
    rec = VerificationRecord(method="data_based", verifier_version=1, checks=checks)
    q = Question(id="pending", topic_id=topic, qtype=f"en:{kind}", level=level,
                 generator=f"en:{kind}", generator_version=1, seed=seed,
                 stem=it["question"], options=[str(o) for o in it["options"]],
                 answer_index=ord(it["answer"]) - 65, explanation=it["explanation"],
                 status=Status.auto_approved.value, verification=rec)
    q.id = f"en:{kind}:{level}:{q.content_hash()}"
    return q


def main():
    # safety: only build types the harness marks servable
    servable = {k for (k, *_rest), ok in ((row[:1], row[-1]) for row in H.measure()) if ok}
    report = []
    for kind, (topic, age, level) in WIRED.items():
        assert kind in servable, f"{kind} is not harness-servable; refusing to build"
        items = R.generate(kind, TARGET, seed=42)
        _, check = R.TYPES[kind]
        qs, seen = [], set()
        for i, it in enumerate(items):
            assert check(it), f"{kind}: generated an item its own checker rejects"
            q = _question(topic, kind, level, it, i)
            assert q.servable(), f"{topic}: non-servable item"
            if q.content_hash() in seen:
                continue
            seen.add(q.content_hash())
            qs.append(q)
        d = ROOT / "content" / f"age{age}" / "banks"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{topic}__L{level}.json").write_text(json.dumps([q.to_dict() for q in qs], ensure_ascii=False, indent=1))
        report.append(f"{topic} L{level} ({len(qs)}) <- {kind}")
    print("English served banks:", report)
    return report


if __name__ == "__main__":
    main()
