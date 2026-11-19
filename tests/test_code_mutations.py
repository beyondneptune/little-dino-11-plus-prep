"""Mutation testing of the generator & solver CODE (parent STEP 1d). Single-sided
bugs must be caught by the independent other half; the shared-convention bug is
pinned as the KNOWN blind spot so the honesty claim can't silently drift."""
import mutation_test as MT


def test_code_mutations_catch_rates():
    res = MT.measure()
    single = [(n, r) for n, w, r in res if w != "blind-spot"]
    uncaught = [n for n, r in single if r != 1.0]
    assert not uncaught, f"single-sided mutations not caught: {uncaught}"

    blind = [r for n, w, r in res if w == "blind-spot"]
    assert blind and blind[0] == 0.0, \
        "the shared generator+solver blind spot changed; update the honesty claims"
