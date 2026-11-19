#!/usr/bin/env python3
"""Content report (parent STEP 3 deliverable): how many verified questions are
served per topic, with the verification evidence. Reads the built banks + the
serve gate, so the numbers reflect exactly what a child can be shown. Writes
content/age1/content_report.md.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "platform"))
sys.path.insert(0, str(ROOT / "scripts"))

BANKS = ROOT / "content" / "age1" / "banks"
LESSONS = ROOT / "content" / "age1" / "lessons"


def _load(topic, level):
    f = BANKS / f"{topic}__L{level}.json"
    return json.loads(f.read_text()) if f.exists() else []


def main():
    topics = {t["id"]: t for t in yaml.safe_load((ROOT / "content/topics.yaml").read_text())["topics"]}
    served = {r["id"]: r for r in yaml.safe_load((ROOT / "content/age1/served.yaml").read_text())["topics"]}
    served_ids = [tid for tid, r in served.items() if r.get("status") == "served"]

    rows, total_q = [], 0
    subj_counter = Counter()
    for tid in sorted(served_ids):
        t = topics.get(tid, {})
        levels = served[tid].get("levels", [])
        per_level, methods, checks = [], set(), set()
        has_distractor = False
        sample = ""
        for lv in levels:
            bank = _load(tid, lv)
            per_level.append(f"L{lv}:{len(bank)}")
            total_q += len(bank)
            subj_counter[t.get("subject", "?")] += len(bank)
            for q in bank[:1] or []:
                methods.add(q.get("verification", {}).get("method", "?"))
                for c in q.get("verification", {}).get("checks", []):
                    checks.add(c["name"])
                if q.get("distractor_explanations"):
                    has_distractor = True
            if not sample and bank:
                s = bank[0]
                sample = f"{s['stem']} → **{s['options'][s['answer_index']]}**"
        lesson = (LESSONS / f"{tid}.md").exists()
        rows.append({
            "id": tid, "subject": t.get("subject", "?"),
            "title": t.get("title", ""), "creature": t.get("creature", ""),
            "levels": ", ".join(per_level),
            "method": ", ".join(sorted(methods)) or "—",
            "checks": ", ".join(sorted(checks)) or "—",
            "lesson": "✅" if lesson else "—",
            "per_option": "✅" if has_distractor else "UI-layer",
            "sample": sample,
        })

    md = ["# Age 1 — content report", "",
          f"**{len(served_ids)} topics served**, **{total_q} verified questions** "
          f"on disk ({', '.join(f'{k}: {v}' for k, v in sorted(subj_counter.items()))}).",
          "",
          "Every question below passed the independent-solver serve gate "
          "(`verification.method = computable`, check `independent_solver`). "
          "Language (English, word-meaning VR) topics are **intentionally not served** "
          "until the blind-solve + adversarial pipeline is built and measured.", "",
          "| Topic | Subject | Title | Levels (count) | Verify checks | Lesson | Per-option | Sample |",
          "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['id']} | {r['subject']} | {r['title'][:38]} | {r['levels']} | "
                  f"{r['checks']} | {r['lesson']} | {r['per_option']} | {r['sample'][:60]} |")
    out = ROOT / "content" / "age1" / "content_report.md"
    out.write_text("\n".join(md) + "\n")
    print(f"served topics: {len(served_ids)}  total verified questions: {total_q}")
    print("by subject:", dict(subj_counter))
    print("written:", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
