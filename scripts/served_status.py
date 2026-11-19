#!/usr/bin/env python3
"""
Which Age-1 topics can actually be SERVED today, and which cannot (and why).

A topic is servable now only if it is fully computable (readiness V) AND an
independent tester already exists (verifier_status built). Everything else is
not_served (hidden, never blocking progress) with a reason:
  - R / P  -> needs the authored + blind-solve/adversarial language pipeline
             (R) or is parent-marked open-ended (P); not auto-served.
  - V but verifier to_build -> needs a per-topic generator + independent tester
             (with its own mutation test) before it can be served.

Writes content/age1/served.yaml (operational list the app uses to hide stations)
and reports/age1_served_status.md.
"""
from pathlib import Path

import yaml

import build_l35 as L35
import registry as R

ROOT = Path(__file__).resolve().parent.parent
SUBJECTS = ["Maths", "English", "VR", "NVR"]


def served_levels(topic_id: str) -> list:
    """Registry levels (L1-2 foundation) plus any dual-verified L3-5 wired in."""
    lvls = set(R.levels_for(topic_id))
    for _type, levels in L35.WIRED.get(topic_id, []):
        lvls.update(levels)
    return sorted(lvls)


def classify(t: dict) -> tuple[str, str]:
    if t["content_readiness"] == "V" and t["verifier_status"] == "built":
        return "served", "computable + independent tester exists"
    if t["content_readiness"] == "P":
        return "not_served", "parent-marked / open-ended (not auto-served)"
    if t["content_readiness"] == "R":
        return "not_served", "language/judgement item — needs blind-solve pipeline"
    return "not_served", "computable but needs a generator + independent tester"


def build():
    topics = yaml.safe_load((ROOT / "content" / "topics.yaml").read_text())["topics"]
    age1 = [t for t in topics if t["age"] == 1 and t["subject"] in SUBJECTS]
    rows = []
    for t in sorted(age1, key=lambda t: t["id"]):
        status, reason = classify(t)
        row = {"id": t["id"], "subject": t["subject"], "title": t["title"],
               "status": status, "reason": reason}
        if status == "served":
            row["levels"] = served_levels(t["id"])   # foundation + any dual-verified L3-5
        rows.append(row)
    (ROOT / "content" / "age1").mkdir(parents=True, exist_ok=True)
    (ROOT / "content" / "age1" / "served.yaml").write_text(
        yaml.safe_dump({"age": 1, "topics": rows}, sort_keys=False, allow_unicode=True))
    return rows


def report(rows):
    served = [r for r in rows if r["status"] == "served"]
    max_level = max((lv for r in served for lv in r.get("levels", [])), default=0)
    if max_level <= 2:
        claim = ("> All currently-served content is **foundation (levels 1-2, single-step)**. "
                 "11+ standard (levels 3-5, multi-step) is NOT yet built or claimed for Age 1.")
    else:
        claim = ("> Served content now spans **foundation (L1-2)** and **11+ multi-step (L3-5)**. "
                 "Every L3-5 item is verified by **two independent methods** (a forward solver "
                 "and a different-method cross-check), with metamorphic + mutation tests "
                 "(`tests/test_l35_*`). Levels 3-5 exist only where that dual check passes.")
    lines = ["# Age 1 — served status", "",
             f"**{len(served)} of {len(rows)} topics can be served today.** The rest are",
             "hidden (not_served) and never block progress until their generator/tester",
             "or the language pipeline is built.", "",
             claim, "",
             "| Topic | Subject | Status | Levels | Reason | Title |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        mark = "✅" if r["status"] == "served" else "⬜"
        lv = ",".join(f"L{n}" for n in r.get("levels", [])) or "—"
        lines.append(f"| {r['id']} | {r['subject']} | {mark} {r['status']} | {lv} | "
                     f"{r['reason']} | {r['title']} |")
    from collections import Counter
    byreason = Counter(r["reason"] for r in rows if r["status"] == "not_served")
    lines += ["", "## Work remaining for Age 1"]
    for reason, n in byreason.most_common():
        lines.append(f"- {n} topics: {reason}")
    out = "\n".join(lines) + "\n"
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "age1_served_status.md").write_text(out)
    return out


if __name__ == "__main__":
    rows = build()
    print(report(rows))
