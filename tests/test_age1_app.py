"""The Age-1 app serves only gated, verified questions and guards the serve gate,
profiles and parent PIN area."""
import age1_app as A


def _client(tmp_path):
    A.DB = tmp_path / "t.db"
    A.init_db()
    return A.app.test_client()


def test_core_screens_render(tmp_path):
    c = _client(tmp_path)
    for path in ("/", "/map/child_a", "/map/child_b", "/station/child_a/trilobite",
                 "/museum/child_a", "/parent"):
        assert c.get(path).status_code == 200, path
    assert c.get("/map/nobody").status_code == 404
    assert c.get("/station/child_a/dragon").status_code == 404


def test_only_verified_questions_served_and_marked(tmp_path):
    c = _client(tmp_path)
    r = c.get("/api/question?who=child_a&topic=MA-A05&level=1")
    assert r.status_code == 200
    j = r.get_json()
    assert j["stem"] and len(j["options"]) >= 2 and j["id"]
    ans = c.post("/api/answer",
                 json={"who": "child_a", "topic": "MA-A05", "qid": j["id"], "chosen": 0})
    assert ans.status_code == 200
    body = ans.get_json()
    assert "correct" in body and "explanation" in body


def test_serve_gate_refuses_unserved_topic(tmp_path):
    c = _client(tmp_path)
    # MA-A02 has no verified bank -> must refuse, never improvise
    assert c.get("/api/question?who=child_a&topic=MA-A02&level=1").status_code == 503


def test_every_loaded_bank_item_is_servable(tmp_path):
    # the app only ever holds items that pass the serve gate
    for items in A.BANK.values():
        assert all(q.servable() for q in items)
    assert A.BANK, "no banks loaded"
