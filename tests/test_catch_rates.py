"""Catch-rate guard (brief 5c): the deterministic verifiers must catch 100% of
every planted flaw and wrongly reject 0 genuine items. A drop fails the build."""
import planted_corpus as PC


def test_catch_rates_meet_threshold():
    res = PC.measure(target=30)   # small per-run; the full 250-item report is separate
    assert res, "no results"
    for (subject, name), r in res.items():
        if name == "control_false_reject":
            assert r["caught"] == 0, f"{subject}: {r['caught']} genuine items wrongly rejected"
        else:
            assert r["rate"] >= PC.THRESHOLD, f"{subject}/{name} catch rate {r['rate']:.2f}"
            assert r["n"] >= 20, f"{subject}/{name} only {r['n']} planted (need >=20)"
