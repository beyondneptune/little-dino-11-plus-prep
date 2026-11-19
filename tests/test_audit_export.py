"""The independent-audit export must be complete, honest and not easy-filtered:
400 questions covering every served (topic, level) across all ages — Maths (incl
MA-B01 L3-5), English SPaG, Age 2/3 — each key a valid option, typed items carry
accepted forms, and every item has an honest verification-risk tag."""
import audit_export as A


def test_sample_covers_all_pairs_and_the_hard_levels():
    sample, pairs = A.build_sample()
    assert len(sample) == A.SAMPLE_TOTAL
    covered = {(r["topic_id"], r["level"]) for r in sample}
    assert covered == {(t, lv) for _a, t, lv, _f in pairs}, "a served (topic,level) is missing"
    for lv in (3, 4, 5):
        assert any(r["topic_id"] == "MA-B01" and r["level"] == lv for r in sample), f"no MA-B01 L{lv}"
    # all three ages and the English SPaG are represented
    assert {r["age"] for r in sample} == {1, 2, 3}
    assert any(r["topic_id"].startswith("EN-") for r in sample), "no English SPaG in the audit"


def test_every_key_is_a_real_option():
    sample, _ = A.build_sample()
    for r in sample:
        assert 0 <= r["answer_index"] < len(r["options"])
        assert r["key"] == r["options"][r["answer_index"]]


def test_typed_items_carry_accepted_forms():
    sample, _ = A.build_sample()
    typed = [r for r in sample if r.get("typed")]
    assert typed, "no typed items in the audit"
    for r in typed:
        assert r["key"] in r["accepted_typed_forms"], f"{r['topic_id']} key not in its accepted forms"


def test_every_item_has_a_risk_tag():
    sample, _ = A.build_sample()
    tags = {r["risk"] for r in sample}
    assert all(t.startswith(("lower", "higher")) for t in tags)
    # L3-5 dual-method items are tagged lower risk; single-solver items higher
    assert any(r["risk"].startswith("lower") for r in sample if str(r["qtype"]).startswith("l35:"))
    assert any(r["risk"].startswith("higher") for r in sample)
