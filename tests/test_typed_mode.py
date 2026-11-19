"""Typed-answer serving: a typed topic is flagged for the UI, and /api/answer
marks a typed answer via the normaliser (equivalent forms accepted, near-misses
rejected) — only for fully-computable topics."""
import age1_app as A


def _client(tmp_path):
    A.DB = tmp_path / "t.db"
    A.init_db()
    return A.app.test_client()


def test_typed_topic_is_flagged_for_ui():
    meta = A.AGE1_BY_KEY["anomalocaris"]
    mb06 = next(t for t in meta["topics"] if t["id"] == "MA-B06")
    assert mb06["typed"] is True


def test_typed_answer_accepts_equivalent_and_rejects_wrong(tmp_path):
    c = _client(tmp_path)
    q = c.get("/api/question?who=child_a&topic=MA-B06&level=1").get_json()
    qid = q["id"]
    # learn the key via a throwaway typed submit
    key = c.post("/api/answer", json={"who": "child_a", "topic": "MA-B06", "qid": qid,
                                      "typed": "999999", "count": False}).get_json()["key"]
    for form in (key, f"  {key} ", f"0{key}"):
        r = c.post("/api/answer", json={"who": "child_a", "topic": "MA-B06", "qid": qid,
                                        "typed": form, "count": False}).get_json()
        assert r["correct"] is True, f"equivalent form {form!r} rejected"
    for bad in (str(int(key) + 1), "", "nope"):
        r = c.post("/api/answer", json={"who": "child_a", "topic": "MA-B06", "qid": qid,
                                        "typed": bad, "count": False}).get_json()
        assert r["correct"] is False, f"wrong form {bad!r} accepted"


def test_mcq_still_works_alongside_typed(tmp_path):
    c = _client(tmp_path)
    q = c.get("/api/question?who=child_a&topic=MA-A05&level=1").get_json()
    r = c.post("/api/answer", json={"who": "child_a", "topic": "MA-A05", "qid": q["id"], "chosen": 0}).get_json()
    assert "correct" in r and "key" in r
