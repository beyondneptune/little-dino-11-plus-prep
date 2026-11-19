"""The ambiguity harness must stay honest: it has to DETECT that word-meaning
items can carry a second valid answer the current checker misses (so we never
mistake a 100% structural score for soundness), and no language type may be served
while that gap is open."""
import english_ambiguity as AMB


def test_ambiguity_harness_flags_the_word_meaning_gap():
    rows = {(k, f): rate for k, f, n, rate, _ in AMB.measure()}
    syn = rows.get(("word_analogy", "second_correct_synonym"))
    # a genuine second synonym slips past far more than the 1% the serve bar allows
    assert syn is not None and syn < 95.0, (
        "the harness should expose that many second-correct synonyms are NOT caught; "
        f"got {syn}")


def test_judgement_language_stays_unserved():
    # synonym/antonym and comprehension must stay unserved while their ambiguity
    # catch is below the bar; only objective SPaG (harness-passed) may be served.
    import age1_app as A
    served = {t["id"] for age in A.AGES for m in A.AGE_META[age] for t in m["topics"]}
    assert not any(t.startswith("EN-A") for t in served)
    assert "EN-B01" not in served
    assert "VR-A05" not in served and "VR-A07" not in served
