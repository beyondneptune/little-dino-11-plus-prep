"""Phase 1 validation: the taxonomy must obey every hard rule in brief 3b, or the
build fails. These guard content/{topics,ages,creatures}.yaml. (Topic ids/titles
vs the master are guarded separately by tests/test_syllabus_sync.py.)
"""
from collections import Counter

import build_taxonomy as B
import coverage_report as C

SUB = C.SUBJECTS                 # ["Maths", "English", "VR", "NVR"]
PROP = C.PROPORTION              # {"Maths":38, "English":35, "VR":13, "NVR":14}


def data():
    topics, ages = C.load()
    return topics, ages, C.load_creatures()


def test_no_integrity_problems():
    topics, ages = C.load()
    assert not C.validate(topics, ages), C.validate(topics, ages)


def test_all_351_placed_once():
    topics, _ = C.load()
    ids = [t["id"] for t in topics]
    assert len(ids) == 351 and len(set(ids)) == 351


def test_age_subject_total_in_30_38():
    topics, ages, _ = data()
    for a in ages:
        n = sum(1 for t in topics if t["subject"] in SUB and t["age"] == a["id"])
        assert 30 <= n <= 38, f"age {a['id']} has {n} subject topics (want 30-38)"


def test_subject_mix_within_2pp():
    topics, ages, _ = data()
    for a in ages:
        rows = [t for t in topics if t["subject"] in SUB and t["age"] == a["id"]]
        tot = len(rows)
        for s in SUB:
            share = 100 * sum(1 for t in rows if t["subject"] == s) / tot
            assert abs(share - PROP[s]) <= 2, \
                f"age {a['id']} {s} share {share:.1f}% vs {PROP[s]} (>2pp)"


def test_every_age_has_all_four_subject_strands():
    topics, ages, _ = data()
    for a in ages:
        present = {t["subject"] for t in topics
                   if t["age"] == a["id"] and t["subject"] in SUB}
        assert present == set(SUB), f"age {a['id']} missing strand(s): {set(SUB) - present}"


def test_creatures_2_2_1_1_and_size_4_7():
    _, ages, creatures = data()
    for a in ages:
        cs = [c for c in creatures if c["age"] == a["id"]]
        counts = Counter(c["subject"] for c in cs)
        assert counts == {"Maths": 2, "English": 2, "VR": 1, "NVR": 1}, \
            f"age {a['id']} creature subjects {dict(counts)}"
        for c in cs:
            assert 4 <= len(c["topics"]) <= 7, f"{c['id']} has {len(c['topics'])} topics"


def test_dinosaur_flags_only_real_dinosaurs_in_ages_5_8():
    _, _, creatures = data()
    for c in creatures:
        if c["is_dinosaur"]:
            assert c["name"] in B.REAL_DINOSAURS, \
                f"{c['name']} flagged is_dinosaur but is not a real dinosaur"
            assert 5 <= c["age"] <= 8, f"dinosaur {c['name']} outside Ages 5-8 (age {c['age']})"
    # and every real dinosaur present is flagged and within 5-8
    for c in creatures:
        if c["name"] in B.REAL_DINOSAURS:
            assert c["is_dinosaur"] and 5 <= c["age"] <= 8, \
                f"real dinosaur {c['name']} not flagged / outside 5-8"


def test_stretch_and_enh_only_age_6_plus():
    topics, _, _ = data()
    for t in topics:
        if t["level"] in ("Stretch", "School-specific"):
            assert t["age"] >= 6, f"{t['id']} ({t['level']}) placed at age {t['age']} (<6)"


def test_prerequisites_never_on_a_later_age():
    topics, _, _ = data()
    by_id = {t["id"]: t for t in topics}
    for t in topics:
        for p in t["prerequisites"]:
            assert p in by_id, f"{t['id']} has unknown prereq {p}"
            assert by_id[p]["age"] <= t["age"], \
                f"{t['id']} (age {t['age']}) depends on {p} (age {by_id[p]['age']})"


def test_every_creature_has_two_source_urls():
    _, _, creatures = data()
    for c in creatures:
        fc = c["fact_card"]
        assert fc["source_1"].startswith("http"), f"creature {c['id']} missing source_1"
        assert fc["source_2"].startswith("http"), f"creature {c['id']} missing source_2"
        assert fc["source_1"] != fc["source_2"], f"creature {c['id']} sources identical"
        assert "wikipedia.org" not in (fc["source_1"] + fc["source_2"]), \
            f"creature {c['id']} uses Wikipedia (not allowed)"


def test_preview_topics_scoped_and_have_a_later_return_visit():
    """DECISIONS D1: preview = above-foundation subject topics in Ages 1-3.
    Each must be introduced early but have a spiral return visit at a later age
    (so it can be required there instead)."""
    topics, _, _ = data()
    for t in topics:
        if not t.get("preview"):
            continue
        assert t["subject"] in SUB, f"{t['id']} preview but not a subject topic"
        assert t["age"] <= 3, f"{t['id']} preview but on age {t['age']}"
        assert t["id"] not in B.FOUNDATION_IDS, f"{t['id']} preview but is foundational"
        rv = t["return_visits"]
        assert rv and any(v["age"] > t["age"] for v in rv), \
            f"{t['id']} preview but has no later return visit"
    previews = [t["id"] for t in topics if t.get("preview")]
    expected = [t["id"] for t in topics
                if t["subject"] in SUB and t["age"] <= 3 and t["id"] not in B.FOUNDATION_IDS]
    assert sorted(previews) == sorted(expected)
    assert len(previews) == 28, f"expected 28 preview topics, got {len(previews)}"


def test_et_homed_to_fossil_digs_of_ages_4_10():
    topics, ages, _ = data()
    et = [t for t in topics if t["subject"] == "ET"]
    assert len(et) == 11
    for t in et:
        assert t.get("creature") is None and t.get("station") == "fossil_dig", \
            f"{t['id']} not homed to a Fossil Dig"
        assert 4 <= t["age"] <= 10, f"{t['id']} on age {t['age']} (want 4-10)"
    for a in ages:
        listed = set(a["fossil_dig"]["et_topics"])
        here = {t["id"] for t in et if t["age"] == a["id"]}
        assert listed == here, f"age {a['id']} fossil-dig ET list {listed} != placed {here}"
