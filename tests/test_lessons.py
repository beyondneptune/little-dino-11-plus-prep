"""Every servable Age-1 topic must have a lesson (learn + worked examples +
remember) before it can be taught. Served topics without a lesson fail the build."""
import yaml

import parse_syllabus as P

ROOT = P.ROOT
LESSONS = ROOT / "content" / "age1" / "lessons"


def _served():
    rows = yaml.safe_load((ROOT / "content" / "age1" / "served.yaml").read_text())["topics"]
    return [r["id"] for r in rows if r["status"] == "served"]


def test_every_served_topic_has_a_lesson():
    for tid in _served():
        path = LESSONS / f"{tid}.md"
        assert path.exists(), f"no lesson for served topic {tid}"
        text = path.read_text()
        assert len(text) > 150, f"lesson {tid} too short"
        low = text.lower()
        assert "## learn" in low, f"lesson {tid} missing a Learn section"
        assert "worked example" in low, f"lesson {tid} missing worked examples"
        assert "common mistake" in low, f"lesson {tid} missing a common-mistake note"
        assert "## remember" in low, f"lesson {tid} missing a Remember section"
