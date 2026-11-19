"""Every question in a built Age-1 bank must be servable (passed the gate),
auto_approved and distinct, for each served level. Self-contained: builds small
banks on the fly from the registry (the committed banks are git-ignored)."""
import registry as R
import build_bank as B


def _entry(topic):
    return next(e for e in R.REGISTRY if e.topic == topic)


def _check(bank, target):
    assert len(bank) >= target, f"only {len(bank)} items"
    assert all(q.servable() for q in bank), "a banked item is not servable"
    assert all(q.status == "auto_approved" for q in bank)
    assert len({q.content_hash() for q in bank}) == len(bank), "duplicate items"


def test_mental_single_bank_each_level():
    e = _entry("MA-B01")
    for level in e.levels:
        _check(B.build_one(e, level, target=40), 40)


def test_rounding_bank_each_level():
    e = _entry("MA-A05")
    for level in e.levels:
        _check(B.build_one(e, level, target=40), 40)


def test_division_fact_bank_each_level():
    e = _entry("MA-B04")
    for level in e.levels:
        _check(B.build_one(e, level, target=40), 40)


def test_vr_letter_series_bank():
    e = _entry("VR-C02")
    _check(B.build_one(e, e.levels[0], target=30), 30)
