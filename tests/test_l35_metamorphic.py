"""Metamorphic tests for the Level 3–5 maths solvers: a known change to the input
must produce a known change in the output, and the two independent methods must
agree on every generated item. These catch solver bugs that golden cases miss."""
import random

import maths_l35 as L
import verify2 as V2


def test_two_methods_agree_on_every_generated_item():
    # the forward solver and the different-method cross-check must agree for all
    for name, (_, solve, check, levels) in L.TYPES.items():
        for lv in levels:
            for it in V2.build(name, lv, target=30):
                a = solve(it["question"])
                assert a == it["answer"], f"{name} L{lv}: forward solver off"
                assert check(it["question"], it["answer"]), f"{name} L{lv}: cross-check off"


def test_bodmas_metamorphic():
    for a in range(2, 10):
        for b in range(2, 10):
            base = L.solve_bodmas(f"Work out {a} × {b} − 5.")
            # follow-up: subtract one more -> answer drops by exactly one
            assert L.solve_bodmas(f"Work out {a} × {b} − 6.") == base - 1
            # commutativity of ×: swapping operands leaves the answer unchanged
            assert L.solve_bodmas(f"Work out {b} × {a} − 5.") == base


def test_money_change_metamorphic():
    s = "Priya buys 6 pencils at £0.45 each and pays with a £5.00 note. How much change should Priya get?"
    # a £1 bigger note gives £1 more change
    s2 = s.replace("£5.00", "£6.00")
    assert L.solve_money(s2) - L.solve_money(s) == 1
    # doubling the number of items increases the cost by one item-batch
    base = "Sam buys 3 apples at £0.50 each and pays with a £10.00 note. How much change should Sam get?"
    dbl = base.replace("3 apples", "6 apples")
    assert L.solve_money(base) - L.solve_money(dbl) == 3 * L.num("£0.50")


def test_fraction_then_metamorphic():
    base = L.solve_fraction_then("Work out 3/4 of 48, then add 9.")
    assert L.solve_fraction_then("Work out 3/4 of 48, then add 10.") == base + 1
    # doubling the whole doubles the fraction part (the +9 is unchanged)
    dbl = L.solve_fraction_then("Work out 3/4 of 96, then add 9.")
    assert dbl - 9 == (base - 9) * 2


def test_percent_multi_metamorphic():
    s = "A £60 coat is reduced by 25% in a sale, then a further £5 is taken off. What is the final price?"
    # a £1 bigger extra reduction gives £1 less
    s2 = s.replace("a further £5", "a further £6")
    assert L.solve_percent_multi(s) - L.solve_percent_multi(s2) == 1


def test_work_backwards_round_trips():
    # for any generated item, simulating forward from the solved start returns the remainder
    rng = random.Random(3)
    made = 0
    while made < 40:
        it = L.gen_work_backwards(rng, 5)
        if not it:
            continue
        made += 1
        assert L.check_work_backwards(it["question"], it["answer"])
