"""Hang guard (Phase 1b b): no generator or tester call may take more than 2
seconds. A genuine infinite loop would otherwise hang the whole suite; here a
hard per-call SIGALRM timer turns any >2s call into a test FAILURE instead.

Covers thousands of seeds across all four generators and all four testers, using
the same entry points train_all.py uses in production.
"""
import signal
from functools import partial

import pytest

import train_all as TA

TIMEOUT_S = 2
GENERATORS = {"maths": TA.gen_maths, "vr": TA.gen_vr,
              "english": TA.gen_english, "nvr": TA.gen_nvr}
TESTERS = {"maths": TA.test_maths, "vr": TA.test_vr,
           "english": TA.test_english, "nvr": TA.test_nvr}


class _Timeout(Exception):
    pass


def _on_alarm(signum, frame):
    raise _Timeout()


def _guard(fn, label):
    """Run fn() but fail the test if it takes longer than TIMEOUT_S seconds."""
    old = signal.signal(signal.SIGALRM, _on_alarm)
    signal.setitimer(signal.ITIMER_REAL, TIMEOUT_S)
    try:
        return fn()
    except _Timeout:
        pytest.fail(f"{label} exceeded {TIMEOUT_S}s — possible hang")
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def _n(name):
    return 6 if name == "nvr" else 12


def test_no_generator_call_exceeds_2s():
    for seed in range(2000):
        for name, gen in GENERATORS.items():
            _guard(partial(gen, _n(name), seed), f"gen_{name}(seed={seed})")


def test_no_tester_call_exceeds_2s():
    for seed in range(600):
        for name, gen in GENERATORS.items():
            items = gen(_n(name), seed)
            _guard(partial(TESTERS[name], items), f"test_{name}(seed={seed})")
