"""Lock in the measurable guarantees of the data-based English/VR checker: clean
items pass, and the STRUCTURAL flaws (wrong key, two correct answers) are caught
100% of the time. Semantic/comprehension guarding is NOT claimed here — those stay
unserved pending the adversarial pipeline (see reports/english_measurement.md)."""
import english_measure as M


def test_structural_flaws_always_caught():
    for kind, (subj, check) in M.KINDS.items():
        items = M._gen(kind, 40)
        assert items, f"no items generated for {kind}"
        # clean items pass
        assert all(check(it) for it in items), f"{kind}: a clean item failed its own checker"
        # a wrong key must always be caught
        wrong = [M.flaw_wrong_key(it) for it in items]
        assert all(not check(x) for x in wrong), f"{kind}: a wrong key slipped through"
        # two identical correct answers must always be caught (duplicate option)
        dup = [M.flaw_two_correct(it) for it in items]
        assert all(not check(x) for x in dup), f"{kind}: two-correct-answers slipped through"


# objective, data-based SPaG types that cleared the rule-gen harness (servable)
OBJECTIVE_EN = {"EN-B06", "EN-D07", "EN-E06", "EN-F01", "EN-F09", "EN-F10"}


def test_only_objective_english_is_served():
    # the app serves from banks on disk; judgement language must stay unserved
    import age1_app as A
    served = {t["id"] for age in A.AGES for m in A.AGE_META[age] for t in m["topics"]}
    assert not any(t.startswith("EN-A") for t in served), "a reading-comprehension topic is served"
    assert "EN-B01" not in served, "synonyms/antonyms vocabulary is served"
    assert "VR-A05" not in served and "VR-A07" not in served, "a word-meaning VR topic is served"
    for t in served:
        if t.startswith("EN-"):
            assert t in OBJECTIVE_EN, f"{t} served but is not a harness-passed objective SPaG type"
