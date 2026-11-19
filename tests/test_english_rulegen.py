"""The rule/data-based English generators: every item is well-formed with exactly
one vetted-correct option, and every type clears the full harness (structural +
ambiguity) at the 99% bar. These are the objective English types that may be served."""
import english_harness as H
import english_rulegen as R


def test_all_types_clean_and_wellformed():
    for kind in R.TYPES:
        items = R.generate(kind, 60, 7)
        assert items, f"no items for {kind}"
        _, check = R.TYPES[kind]
        for it in items:
            assert len(set(it["options"])) == 4, f"{kind}: options not 4 distinct"
            assert check(it), f"{kind}: generated an item its own checker rejects"


def test_harness_all_types_clear_the_bar():
    for kind, n, clean, wk, tc, amb, servable in H.measure():
        assert clean == 100.0, f"{kind} clean {clean}"
        assert wk >= 99.0 and tc >= 99.0, f"{kind} structural flaw not caught"
        if amb is not None:
            assert amb >= 99.0, f"{kind} ambiguity flaw not caught ({amb})"
        assert servable, f"{kind} not servable"


def test_homophone_distractors_never_correct():
    for sent, correct, wrongs in R.HOMOPHONES:
        assert correct not in wrongs
        assert R._HOMO_CORRECT[sent] == correct


def test_mutated_checker_is_caught():
    # a checker that accepts anything must fail the structural flaws it should catch
    items = R.generate("spelling", 30, 1)
    bad = [{**it, "answer": chr(65 + (ord(it["answer"]) - 65 + 1) % 4)} for it in items]
    assert all(not R.check_spelling(it) for it in bad), "a wrong-key spelling item slipped through"
