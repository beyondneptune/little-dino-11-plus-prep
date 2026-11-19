"""Taxonomy integrity: every topic on a valid age, prerequisites valid and
not on a later age, ids unique. Guards content/topics.yaml + ages.yaml."""
import coverage_report as C


def test_taxonomy_has_no_integrity_problems():
    topics, ages = C.load()
    issues = C.validate(topics, ages)
    assert not issues, "taxonomy problems:\n" + "\n".join(issues)
