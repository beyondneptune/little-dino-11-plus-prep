"""The serve gate must let verified items through and block everything else.
These are hand-worked examples (brief 5e engineering: scoring/gating unit-tested)."""
import pytest

from qschema import (Check, Question, ServeError, Status, VerificationRecord,
                     serve_or_none, serve_strict)


def _ok_record():
    return VerificationRecord(method="computable", verifier_version=1,
                              checks=[Check("solver_agrees", True),
                                      Check("unique_answer", True)])


def _good_question(**over):
    base = dict(id="q1", topic_id="MA-B01", qtype="arithmetic", level=2,
                generator="maths_gen", generator_version=1, seed=7,
                stem="Work out 3 x 4 + 5", options=["17", "12", "20", "35"],
                answer_index=0, explanation="3x4=12, +5=17",
                distractor_explanations=["added wrong", "forgot +5", "x then x", "added first"],
                reading_grade=3.0, status=Status.auto_approved.value,
                verification=_ok_record())
    base.update(over)
    return Question(**base)


def test_verified_item_serves():
    q = _good_question()
    assert q.servable()
    assert serve_or_none(q) is q
    assert serve_strict(q) is q


def test_unverified_item_never_serves():
    # status still draft -> blocked even though a record exists
    q = _good_question(status=Status.draft.value)
    assert not q.servable()
    assert serve_or_none(q) is None
    with pytest.raises(ServeError):
        serve_strict(q)


def test_missing_verification_record_blocks():
    q = _good_question(verification=None)
    assert not q.servable()


def test_failed_check_blocks():
    rec = VerificationRecord(method="computable", verifier_version=1,
                             checks=[Check("solver_agrees", False, "solver got 18")])
    q = _good_question(verification=rec)
    assert not q.servable()
    with pytest.raises(ServeError):
        serve_strict(q)


def test_empty_checklist_blocks():
    rec = VerificationRecord(method="computable", verifier_version=1, checks=[])
    q = _good_question(verification=rec)
    assert not rec.ok and not q.servable()


def test_tampered_answer_index_blocks():
    q = _good_question(answer_index=9)   # out of range despite "approved" status
    assert not q.servable()


def test_duplicate_options_block():
    q = _good_question(options=["17", "17", "20", "35"])
    assert not q.servable()


def test_bad_level_blocks():
    assert not _good_question(level=0).servable()
    assert not _good_question(level=6).servable()


def test_status_approved_but_record_method_language_ok_if_checks_pass():
    rec = VerificationRecord(method="language", verifier_version=1,
                             checks=[Check("blind_solve_agree", True),
                                     Check("adversarial_no_second_answer", True),
                                     Check("reading_level_ok", True)])
    assert _good_question(verification=rec).servable()
