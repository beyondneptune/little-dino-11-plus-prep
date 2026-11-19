"""Lesson verification (parent STEP 1e): every worked example re-computes with the
independent solver, and lesson text is at the right reading level. A planted wrong
worked example must fail."""
import lesson_check as LC
import parse_syllabus as P

LESSONS = P.ROOT / "content" / "age1" / "lessons"


def test_all_lesson_examples_verify_and_are_readable():
    for p in sorted(LESSONS.glob("*.md")):
        issues = LC.check_lesson(p.read_text(), reading_ceiling=6.0)
        assert not issues, f"{p.stem}: {issues}"


def test_planted_wrong_arithmetic_example_is_caught():
    bad = (LESSONS / "MA-B01.md").read_text().replace("7 × 8 = **56**", "7 × 8 = **54**")
    issues = LC.check_examples(bad)
    assert any("solver gives" in i for i in issues), issues


def test_planted_wrong_rounding_example_is_caught():
    bad = (LESSONS / "MA-A05.md").read_text().replace("→ **2320**", "→ **2330**")
    issues = LC.check_examples(bad)
    assert any("Round 2321" in i for i in issues), issues
