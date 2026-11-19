#!/usr/bin/env python3
"""
Phase 1b (d): PROPOSAL ONLY. Lists the above-level topics now sitting in the
foundation ages (1-3) and proposes a 'preview' status for them. This script
writes a proposal document — it does NOT modify topics.yaml or any logic. The
'preview' flag is implemented only if the parent approves.

Writes content/preview_status_proposal.md.
"""
from collections import defaultdict
from pathlib import Path

import yaml

import build_taxonomy as B

ROOT = Path(__file__).resolve().parent.parent
SUBJECTS = ["Maths", "English", "VR", "NVR"]


def main():
    topics = yaml.safe_load((ROOT / "content" / "topics.yaml").read_text())["topics"]
    by_id = {t["id"]: t for t in topics}
    above = [t for t in topics
             if t["subject"] in SUBJECTS and t["age"] <= 3 and t["id"] not in B.FOUNDATION_IDS]
    by_subj = defaultdict(list)
    for t in above:
        by_subj[t["subject"]].append(t)

    L = ["# Proposal: a 'preview' status for above-level foundation-age topics",
         "",
         "**This is a proposal only — nothing is implemented yet.** It needs your",
         "yes/no before I add anything.", "",
         "## The problem it solves",
         "",
         "Ages 1-3 should rebuild Year 3-4 school level, but to keep every age at",
         f"30-38 topics, **{len(above)} above-level topics** currently sit in Ages 1-3",
         "(Maths "
         + ", ".join(f"{s} {len(by_subj[s])}" for s in SUBJECTS if by_subj[s]).replace("Maths ", "")
         + "). We don't want to drill a Year-4 child on Year-5 material too early,",
         "but we also don't want holes in the map.", "",
         "## The proposed 'preview' status",
         "",
         "Tag each of these topics `preview: true`. A preview topic would be:",
         "- **Introduced gently** in its Age 1-3 home — a short lesson and a few easy",
         "  examples, so the child meets the idea in context with its creature.",
         "- **Not required for mastery of the age**, and **not required to pass the",
         "  Fossil Dig** or open the next age. It would not drag down the age's",
         "  mastery percentage or block progress.",
         "- **Promoted to a normal, required topic at its spiral return visit**",
         "  (Ages 5-7), when the child is developmentally ready. From then on it",
         "  counts towards mastery like any other topic.",
         "",
         "Net effect: the child sees everything in a natural order, nothing is forced",
         "early, and no topic is skipped — it just becomes 'for real' later.",
         "",
         "## What I would change if you approve (not done yet)",
         "- add `preview: true` to the listed topics in `topics.yaml`;",
         "- make the (future) mastery + Fossil-Dig gating logic ignore preview topics",
         "  until their return-visit age;",
         "- add a validation test so a preview topic must have a later return visit.",
         "",
         "## The topics this would apply to", ""]
    for s in SUBJECTS:
        if not by_subj[s]:
            continue
        L.append(f"### {s} ({len(by_subj[s])})")
        for t in sorted(by_subj[s], key=lambda t: t["id"]):
            rv = by_id[t["id"]]["return_visits"]
            rvtxt = f" → returns Age {rv[0]['age']}" if rv else " → (no return visit yet)"
            L.append(f"- `{t['id']}` (Age {t['age']}) {t['title']}{rvtxt}")
        L.append("")
    L += ["## Your call",
          "- **Approve** — I add the flag and wire the gating when the platform is built.",
          "- **Reject** — these stay as normal required topics in Ages 1-3.",
          "- **Other** — tell me a different rule (e.g. move some to Age 4 instead)."]
    (ROOT / "content" / "preview_status_proposal.md").write_text("\n".join(L) + "\n")
    print(f"Wrote content/preview_status_proposal.md ({len(above)} topics)")


if __name__ == "__main__":
    main()
