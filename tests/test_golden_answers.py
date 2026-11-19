"""Golden known-answer tests (parent STEP 3): fixed cases whose answers are
checked by the INDEPENDENT solver, plus a re-verification sweep of a sample from
every served Maths bank. If a generator ever drifts, these catch it."""
import age1_more as AM
import build_bank
import registry as R
import testers as T

SERVED_MATHS = {"MA-A03", "MA-A05", "MA-A07", "MA-B01", "MA-B04", "MA-B06", "MA-B13"}


def _it(q, opts, ans_idx):
    return {"question": q, "options": [str(o) for o in opts], "answer": chr(65 + ans_idx)}


def test_golden_rounding():
    assert T.check_maths_item(_it("Round 79 to the nearest 10.", ["80", "90", "70", "79"], 0))[0]
    # a wrong key must be rejected
    assert not T.check_maths_item(_it("Round 79 to the nearest 10.", ["70", "90", "80", "79"], 0))[0]


def test_golden_roman():
    assert AM.roman_to_int("XIV") == 14
    assert AM.roman_to_int("XL") == 40
    assert AM.roman_to_int("MCMXC") == 1990
    assert AM.to_roman(49) == "XLIX"
    assert AM.to_roman(4) == "IV"
    assert T.check_maths_item(_it("What number does the Roman numeral XIV represent?",
                                  ["14", "16", "24", "11"], 0))[0]


def test_golden_compare():
    assert T.check_maths_item(_it("Which of these numbers is the largest?", ["83", "28", "59", "68"], 0))[0]
    assert T.check_maths_item(_it("Which of these numbers is the smallest?", ["28", "83", "59", "68"], 0))[0]


def test_golden_parity_and_multiples():
    assert T.check_maths_item(_it("Which of these is an even number?", ["34", "11", "57", "23"], 0))[0]
    assert T.check_maths_item(_it("Which of these is an odd number?", ["45", "34", "12", "20"], 0))[0]
    assert T.check_maths_item(_it("Which of these is a multiple of 5?", ["45", "52", "31", "28"], 0))[0]
    assert not T.check_maths_item(_it("Which of these is a multiple of 5?", ["52", "45", "31", "28"], 0))[0]


def test_golden_missing_number():
    assert T.check_maths_item(_it("What number goes in the box? 7 × ? = 56", ["8", "7", "6", "9"], 0))[0]
    assert T.check_maths_item(_it("What number goes in the box? 48 ÷ ? = 6", ["8", "6", "7", "9"], 0))[0]
    assert T.check_maths_item(_it("What number goes in the box? 23 + ? = 40", ["17", "18", "16", "15"], 0))[0]


def test_every_served_maths_item_independently_reverifies():
    checked = set()
    for e in R.REGISTRY:
        if e.topic not in SERVED_MATHS:
            continue
        for lv in e.levels:
            bank = build_bank.build_one(e, lv, target=20)
            assert len(bank) >= 20, f"{e.topic} L{lv}: only {len(bank)}"
            for q in bank:
                it = {"question": q.stem, "options": q.options, "answer": chr(65 + q.answer_index)}
                ok, reason = T.check_maths_item(it)
                assert ok, f"{e.topic} L{lv}: {q.stem!r} {reason}"
            checked.add(e.topic)
    assert checked == SERVED_MATHS, f"missed {SERVED_MATHS - checked}"
