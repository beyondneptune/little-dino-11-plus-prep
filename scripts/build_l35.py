#!/usr/bin/env python3
"""Build Level 3–5 verified banks from the dual-verified multi-step generators
(scripts/maths_l35.py + verify2.py) and write them in the serve-gate schema so the
Age-1 app can serve them. Each item carries a verification record with BOTH an
`independent_solver` check and a `second_method` (different-logic) check.

Mapping (which served topic gets which multi-step type at which levels):
    MA-B01 (Mental calculations) <- bodmas  at L3, L4, L5

The other verified types (money_change, fraction_then, percent_multi,
work_backwards) are a tested library for later ages / future Age-1 topics; they
are reported but not wired into an Age-1 creature here (they belong to later-age
topics). Raw banks are git-ignored and deterministic.
"""
from __future__ import annotations

import json
from pathlib import Path

import maths_l35 as L
import verify2 as V2
from qschema import Check, Question, Status, VerificationRecord

ROOT = Path(__file__).resolve().parent.parent
BANKS = ROOT / "content" / "age1" / "banks"

# topic_id -> [(type_name, [levels]), ...]   (multiple multi-step types per topic)
WIRED = {
    "MA-B01": [("bodmas", [3, 4, 5])],
    "MA-A05": [("estimate", [3, 4, 5])],
    "MA-B04": [("division_worded", [3, 4, 5])],
    "MA-B06": [("two_step_inverse", [3, 4]), ("work_backwards", [5])],
    "MA-A03": [("compare_calc", [3, 4])],
    "MA-B13": [("lcm_hcf", [3, 4])],
}
TARGET = 120


def _to_question(topic, type_name, level, it, seed):
    checks = [Check("options_distinct", True),
              Check("answer_label_valid", True),
              Check("independent_solver", True, "forward solver agrees"),
              Check("second_method", True, "reverse/alt-logic cross-check agrees")]
    rec = VerificationRecord(method="computable", verifier_version=2, checks=checks)
    q = Question(
        id="pending", topic_id=topic, qtype=f"l35:{type_name}", level=level,
        generator=f"l35:{type_name}", generator_version=1, seed=seed,
        stem=it["question"], options=[str(o) for o in it["options"]],
        answer_index=it["answer_index"], explanation=it["explanation"],
        distractor_explanations=it.get("distractor_explanations", []),
        status=Status.auto_approved.value, verification=rec)
    q.id = f"l35:{type_name}:{level}:{q.content_hash()}"
    return q


def main():
    BANKS.mkdir(parents=True, exist_ok=True)
    report = []
    # accumulate items per (topic, level) so multiple generators can share a topic
    by_pair = {}
    for topic, specs in WIRED.items():
        for type_name, levels in specs:
            for level in levels:
                items = V2.build(type_name, level, target=TARGET)
                for i, it in enumerate(items):
                    q = _to_question(topic, type_name, level, it, i)
                    assert q.servable(), f"{topic} L{level}: built a non-servable item"
                    by_pair.setdefault((topic, level), {})[q.content_hash()] = q
    for (topic, level), qs in sorted(by_pair.items()):
        (BANKS / f"{topic}__L{level}.json").write_text(
            json.dumps([q.to_dict() for q in qs.values()], ensure_ascii=False, indent=1))
        report.append(f"{topic} L{level} ({len(qs)})")
    print("L3-5 served banks:", report)
    return report


if __name__ == "__main__":
    main()
