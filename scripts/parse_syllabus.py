#!/usr/bin/env python3
"""
Parse the parent's master syllabus into a canonical topic list.

This is the ONE place the syllabus is read. The topic IDs and titles are taken
VERBATIM from the markdown — never retyped — so that content/topics.yaml can be
rebuilt from here and a sync test can prove the two never drift apart.

The master file is markdown. Every real topic is a bullet whose first token is a
back-tick-wrapped stable ID, e.g.

    - `MA-C05` Adding and subtracting fractions with unlike denominators
    - `EN-C08` Pathetic fallacy (stretch)
    - `ET-01`  Reading unfamiliar questions accurately ...

Tables, prose and headings have no back-tick ID at the start of a bullet, so the
regex below ignores them automatically.

Level is derived from the master, per its own key (section 1 of the file):
  - "(stretch)" or "(useful extension)" in the title            -> Stretch
  - the enclosing "### ..." section is marked "(school-specific)" -> School-specific
  - otherwise                                                     -> Core
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "11 Syllabus Master Topic List.md"

# EN-A01 / MA-C05 (two letters, a section letter, two digits) OR ET-01 (no section letter).
TOPIC_RE = re.compile(r"^-\s+`([A-Z]{2}-(?:[A-Z]\d{2}|\d{2}))`\s+(.+?)\s*$")
SECTION_RE = re.compile(r"^###\s+(.*?)\s*$")

PREFIX_TO_SUBJECT = {
    "EN": "English",
    "MA": "Maths",
    "VR": "VR",
    "NV": "NVR",
    "ET": "ET",
}

# The counts the parent's document states for itself, used as a self-check.
EXPECTED = {"English": 119, "Maths": 128, "VR": 45, "NVR": 48, "ET": 11}


def _level(title: str, section_heading: str) -> str:
    low = title.lower()
    if "(stretch)" in low or "(useful extension)" in low:
        return "Stretch"
    if "school-specific" in section_heading.lower():
        return "School-specific"
    return "Core"


def parse(path: Path = MASTER) -> list[dict]:
    """Return the canonical topic list in document order.

    Each item: {id, subject, title, level, section}. Titles are verbatim.
    """
    text = path.read_text()
    topics: list[dict] = []
    section = ""
    for line in text.splitlines():
        m_sec = SECTION_RE.match(line)
        if m_sec:
            section = m_sec.group(1)
            continue
        m = TOPIC_RE.match(line)
        if not m:
            continue
        tid, title = m.group(1), m.group(2)
        prefix = tid.split("-", 1)[0]
        subject = PREFIX_TO_SUBJECT.get(prefix)
        if subject is None:
            raise ValueError(f"Unknown subject prefix in id {tid!r}")
        topics.append(
            {"id": tid, "subject": subject, "title": title,
             "level": _level(title, section), "section": section}
        )
    return topics


def check(topics: list[dict] | None = None) -> dict[str, int]:
    """Return per-subject counts and assert IDs are unique and counts match."""
    topics = topics if topics is not None else parse()
    ids = [t["id"] for t in topics]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise ValueError(f"duplicate ids in master: {sorted(dupes)}")
    counts: dict[str, int] = {}
    for t in topics:
        counts[t["subject"]] = counts.get(t["subject"], 0) + 1
    if counts != EXPECTED:
        raise ValueError(f"count mismatch: parsed {counts} vs expected {EXPECTED}")
    return counts


if __name__ == "__main__":
    ts = parse()
    counts = check(ts)
    for subj in ["English", "Maths", "VR", "NVR", "ET"]:
        print(f"  {subj:8} {counts[subj]:>3}")
    print(f"  {'TOTAL':8} {len(ts):>3}")
    # Show a couple of derived levels as a spot check.
    for sample in ("EN-C08", "EN-H01", "MA-D07", "MA-A01", "ET-01"):
        t = next(x for x in ts if x["id"] == sample)
        print(f"    {t['id']}  level={t['level']:14}  {t['title']}")
    sys.exit(0)
