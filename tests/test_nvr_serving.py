"""The Wiwaxia station serves verified image-option NVR items: the topic is
flagged nvr, the question returns rendered SVGs + a prompt (answer hidden), and
/api/answer marks the chosen picture against the verified key."""
import age1_app as A


def _client(tmp_path):
    A.DB = tmp_path / "t.db"
    A.init_db()
    return A.app.test_client()


def test_wiwaxia_has_nvr_topics():
    topics = A.AGE1_BY_KEY["wiwaxia"]["topics"]
    assert topics, "Wiwaxia should now be served with NVR topics"
    assert any(t.get("nvr") and t["id"] == "NV-A01" for t in topics)


def test_nvr_question_is_image_option_and_hides_answer(tmp_path):
    c = _client(tmp_path)
    q = c.get("/api/question?who=child_a&topic=NV-A01&level=2").get_json()
    assert q["nvr"] is True and q["prompt"]
    assert len(q["seq"]) >= 3 and all("<svg" in s for s in q["seq"])
    assert len(q["options"]) >= 4 and all("<svg" in s for s in q["options"])
    assert "answer_index" not in q           # the key must not leak to the client


def test_nvr_answer_marks_against_verified_key(tmp_path):
    c = _client(tmp_path)
    q = c.get("/api/question?who=child_a&topic=NV-C01&level=2").get_json()
    item = A.NVR_BY_ID[q["id"]]
    right = item["answer_index"]
    r = c.post("/api/answer", json={"who": "child_a", "topic": "NV-C01", "qid": q["id"], "chosen": right}).get_json()
    assert r["correct"] is True and r["explanation"]
    wrong = (right + 1) % len(item["options"])
    r2 = c.post("/api/answer", json={"who": "child_a", "topic": "NV-C01", "qid": q["id"], "chosen": wrong}).get_json()
    assert r2["correct"] is False
