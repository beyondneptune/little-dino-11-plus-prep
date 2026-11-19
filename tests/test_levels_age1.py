"""Age-1 level definitions must cover every Age-1 subject topic, with levels 1-5
and titles matching the taxonomy (so generation targets the right skills)."""
import yaml

import parse_syllabus as P

ROOT = P.ROOT
SUBJECTS = {"Maths", "English", "VR", "NVR"}


def _load():
    lv = yaml.safe_load((ROOT / "content" / "levels" / "age1.yaml").read_text())
    topics = yaml.safe_load((ROOT / "content" / "topics.yaml").read_text())["topics"]
    return lv, topics


def test_levels_cover_all_age1_topics_with_1_to_5():
    lv, topics = _load()
    age1 = {t["id"]: t for t in topics if t["age"] == 1 and t["subject"] in SUBJECTS}
    assert len(age1) == 35
    defined = lv["topics"]
    assert set(defined) == set(age1), \
        f"missing {set(age1) - set(defined)}; extra {set(defined) - set(age1)}"
    for tid, d in defined.items():
        assert d["subject"] == age1[tid]["subject"], tid
        assert d["title"] == age1[tid]["title"], f"{tid} title drift"
        assert d["readiness"] == age1[tid]["content_readiness"], f"{tid} readiness drift"
        for key in ("focus", "distractors"):
            assert key in d, f"{tid} missing {key}"
        assert set(d["focus"]) == {1, 2, 3, 4, 5}, f"{tid} focus levels != 1-5"
        assert d["distractors"], f"{tid} has no distractor types"


def test_rubrics_and_reading_ceiling_present():
    lv, _ = _load()
    assert lv["reading_grade_ceiling"] == 6.0
    for s in SUBJECTS:
        assert s in lv["rubrics"], f"no rubric for {s}"
