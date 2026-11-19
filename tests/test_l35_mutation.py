"""Planted-bug (mutation) tests: deliberately break each tester and prove the
dual-method verifier CATCHES it. If a mutated solver or cross-check slips through,
the tester is not actually testing. One mutation per tester, per item type."""
import pytest

import maths_l35 as L
import verify2 as V2

TYPE_LEVEL = [(n, levels[0]) for n, (_, _, _, levels) in L.TYPES.items()]


def _good_items(name, level, n=25):
    return V2.build(name, level, target=n)


@pytest.mark.parametrize("name,level", TYPE_LEVEL)
def test_mutated_forward_solver_is_caught(name, level):
    items = _good_items(name, level)
    assert items, f"no items for {name} L{level}"
    g, solve, check, lv = L.TYPES[name]
    # off-by-one bug in the forward solver
    L.TYPES[name] = (g, lambda s, _o=solve: (lambda r: None if r is None else r + 1)(_o(s)), check, lv)
    try:
        caught = sum(1 for it in items if not V2.verify(name, it)[0])
    finally:
        L.TYPES[name] = (g, solve, check, lv)
    assert caught == len(items), f"{name}: off-by-one solver bug not caught ({caught}/{len(items)})"


@pytest.mark.parametrize("name,level", TYPE_LEVEL)
def test_always_true_crosscheck_is_caught(name, level):
    items = _good_items(name, level)
    g, solve, check, lv = L.TYPES[name]
    # a cross-check that accepts anything must be rejected (it accepts a wrong answer)
    L.TYPES[name] = (g, solve, lambda s, a: True, lv)
    try:
        caught = sum(1 for it in items if not V2.verify(name, it)[0])
    finally:
        L.TYPES[name] = (g, solve, check, lv)
    assert caught == len(items), f"{name}: always-true cross-check not caught"


@pytest.mark.parametrize("name,level", TYPE_LEVEL)
def test_always_false_crosscheck_is_caught(name, level):
    items = _good_items(name, level)
    g, solve, check, lv = L.TYPES[name]
    L.TYPES[name] = (g, solve, lambda s, a: False, lv)
    try:
        caught = sum(1 for it in items if not V2.verify(name, it)[0])
    finally:
        L.TYPES[name] = (g, solve, check, lv)
    assert caught == len(items), f"{name}: always-false cross-check not caught"
