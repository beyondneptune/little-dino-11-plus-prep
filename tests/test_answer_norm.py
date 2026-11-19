"""Typed-answer normaliser: accept every equivalent written form, reject
near-misses and wrong forms, and prove (mutation tests) the normaliser is actually
discriminating — a broken normaliser that accepts anything must fail these."""
from fractions import Fraction

import answer_norm as A


def test_integer_forms():
    for ok in ["40", " 40 ", "40.0", "40.00", "1,240"]:
        assert A.accepts(ok, 40 if ok.strip() != "1,240" else 1240, "number")
    for bad in ["41", "40%", "£40", "4/10", "forty"]:
        assert not A.accepts(bad, 40, "number"), bad


def test_fraction_and_mixed_equivalence():
    for ok in ["3/2", "1 1/2", "1.5", "6/4"]:
        assert A.accepts(ok, Fraction(3, 2), "number"), ok
    for bad in ["1/2", "2/3", "1 1/3", "3/4"]:
        assert not A.accepts(bad, Fraction(3, 2), "number"), bad


def test_proportion_equivalence():
    # 0.5 = 1/2 = 50% all accepted for a proportion answer
    for ok in ["0.5", "1/2", "50%", "50 %", ".5", "2/4"]:
        assert A.accepts(ok, Fraction(1, 2), "proportion"), ok
    for bad in ["0.51", "1/3", "5%", "50"]:   # 50 (as a bare number) is NOT the proportion 1/2... but 0.5 is
        if bad == "50":
            # a bare 50 means 50, not 0.5 -> must reject as a proportion of value 1/2
            assert not A.accepts(bad, Fraction(1, 2), "proportion")
        else:
            assert not A.accepts(bad, Fraction(1, 2), "proportion"), bad


def test_money_forms():
    for ok in ["£2.50", "2.50", "2.5", "250p", "£2.5"]:
        assert A.accepts(ok, Fraction(5, 2), "money"), ok
    for bad in ["2.5%", "2.51", "£2.55", "2.5 cm"]:
        assert not A.accepts(bad, Fraction(5, 2), "money"), bad


def test_measure_units():
    assert A.accepts("12", 12, "measure", unit="cm")
    assert A.accepts("12 cm", 12, "measure", unit="cm")
    assert A.accepts("12cm", 12, "measure", unit="cm")
    assert not A.accepts("12 m", 12, "measure", unit="cm")   # wrong unit
    assert not A.accepts("13 cm", 12, "measure", unit="cm")  # wrong value


def test_near_misses_rejected():
    assert not A.accepts("0.49", Fraction(1, 2), "proportion")
    assert not A.accepts("0.501", Fraction(1, 2), "proportion")
    assert not A.accepts("49", 50, "number")


# ---- mutation tests: a broken normaliser must be caught by these cases -------
def test_mutation_accept_all_is_caught():
    # if accepts() were replaced by 'always True', these wrong answers would pass
    wrong_cases = [("41", 40, "number"), ("1/3", Fraction(1, 2), "proportion"),
                   ("£2.55", Fraction(5, 2), "money"), ("13 cm", 12, "measure")]
    # the real normaliser must reject all of them
    assert all(not A.accepts(t, v, d, unit="cm" if d == "measure" else None) for t, v, d in wrong_cases)


def test_mutation_parser_route_consistency():
    # the independent decimal re-read guards against a parser that returns a wrong Fraction
    assert A.parse("1 1/2")[0] == Fraction(3, 2)
    assert A.parse("250p") == (Fraction(5, 2), "money", None)
    assert A.parse("50%") == (Fraction(1, 2), "percent", None)
