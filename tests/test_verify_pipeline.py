"""End-to-end: generator -> independent verify -> serve gate.

Proves (a) genuine generated items verify and become servable, and (b) a planted
wrong key is rejected by the pipeline and blocked by the serve gate. This links
the testers' mutation coverage to the schema-level serve gate.
"""
import copy

import train_all as TA
import verify_computable as VC
from qschema import Status

GEN = {"maths": TA.gen_maths, "vr": TA.gen_vr,
       "english": TA.gen_english, "nvr": TA.gen_nvr}


def _mk(subject, it, seed):
    return VC.make_question(subject, it, topic_id="TEST", qtype=subject, level=2,
                            generator=f"{subject}_gen", generator_version=1, seed=seed)


def test_generated_items_verify_and_serve():
    for subject, gen in GEN.items():
        n = 20 if subject == "nvr" else 40
        for seed in (101, 202, 303):
            for it in gen(n, seed):
                q = _mk(subject, it, seed)
                assert q.status == Status.auto_approved.value, \
                    (subject, q.verification.failed_checks())
                assert q.servable(), (subject, q.id)


def test_planted_wrong_key_rejected_and_unservable():
    it = TA.gen_maths(1, 5)[0]
    good = _mk("maths", it, 5)
    assert good.servable()
    bad_it = copy.deepcopy(it)
    cur = ord(bad_it["answer"]) - 65
    bad_it["answer"] = chr(65 + (cur + 1) % len(bad_it["options"]))  # mark a distractor
    bad = _mk("maths", bad_it, 5)
    assert not bad.servable()
    assert bad.status == Status.rejected.value
    assert "independent_solver" in bad.verification.failed_checks()


def test_planted_duplicate_option_rejected():
    it = TA.gen_vr(10, 9)[0]
    bad = copy.deepcopy(it)
    bad["options"][1] = bad["options"][0]           # duplicate option
    q = VC.make_question("vr", bad, "TEST", "vr", 2, "vr_gen", 1, 9)
    assert not q.servable()
    assert "options_distinct" in q.verification.failed_checks()
