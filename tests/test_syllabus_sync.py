"""content/topics.yaml must stay a faithful copy of the master syllabus.

Fails the build if any topic is missing, duplicated, renamed or invented, or if
subject/level drift from what the parser derives from the master file. This is
the guard that the taxonomy is never retyped away from the parent's source.
"""
import yaml

import parse_syllabus as P


def _topics_yaml():
    return yaml.safe_load((P.ROOT / "content" / "topics.yaml").read_text())["topics"]


def test_counts_match_master():
    counts = P.check(P.parse())  # raises if master itself is malformed
    assert counts == {"English": 119, "Maths": 128, "VR": 45, "NVR": 48, "ET": 11}


def test_topics_yaml_matches_master_exactly():
    master = {t["id"]: t for t in P.parse()}
    got = _topics_yaml()

    got_ids = [t["id"] for t in got]
    dupes = sorted({i for i in got_ids if got_ids.count(i) > 1})
    assert not dupes, f"duplicate ids in topics.yaml: {dupes}"

    got_map = {t["id"]: t for t in got}
    missing = sorted(set(master) - set(got_map))
    invented = sorted(set(got_map) - set(master))
    assert not missing, f"topics.yaml is missing master ids: {missing}"
    assert not invented, f"topics.yaml invents ids not in master: {invented}"

    renamed = [i for i in master if got_map[i]["title"] != master[i]["title"]]
    assert not renamed, "titles differ from master: " + ", ".join(renamed[:10])

    drift = [i for i in master
             if got_map[i]["subject"] != master[i]["subject"]
             or got_map[i]["level"] != master[i]["level"]]
    assert not drift, "subject/level drift from master: " + ", ".join(drift[:10])
