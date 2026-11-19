"""The platform gate must DISCARD a candidate its tester rejects and only serve a
verified one — proving section 2 ("nothing unverified reaches a child")."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "platform"))
import app                                           # noqa: E402


def test_gate_discards_failing_candidate(tmp_path, monkeypatch):
    q = "Round 5305 to the nearest 10."
    opts = ["5300", "5310", "5290", "5320"]
    calls = {"n": 0}

    def fake_candidate(subject, rng):
        calls["n"] += 1
        # 1st candidate has the banker's-rounding bug (marks 5300); 2nd is correct (5310)
        answer = "A" if calls["n"] == 1 else "B"
        return {"subject": "maths", "topic": "rounding", "question": q,
                "options": opts, "answer": answer, "image": None}

    monkeypatch.setattr(app, "_candidate", fake_candidate)
    monkeypatch.setattr(app, "REJECT_LOG", tmp_path / "rejected.log")

    served = app.make_question("maths")
    assert served is not None
    assert served["answer"] == "B"                   # the verified one, not the buggy one
    assert calls["n"] == 2                            # it tried the bad, rejected, then the good
    assert (tmp_path / "rejected.log").exists()       # the bad one was logged, never served


def test_gate_returns_none_if_nothing_verifies(tmp_path, monkeypatch):
    # every candidate is the banker's-rounding bug -> nothing can be served
    def always_bad(subject, rng):
        return {"subject": "maths", "topic": "rounding",
                "question": "Round 5305 to the nearest 10.",
                "options": ["5300", "5310", "5290", "5320"], "answer": "A", "image": None}

    monkeypatch.setattr(app, "_candidate", always_bad)
    monkeypatch.setattr(app, "REJECT_LOG", tmp_path / "rejected.log")
    assert app.make_question("maths") is None
