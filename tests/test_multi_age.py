"""Ages 2 (Devonian) and 3 (Carboniferous) are playable on the kit: their maps,
stations, per-age Fossil Dig and Museum render, and they serve ONLY verified
topics with their own lessons."""
import age1_app as A


def _client(tmp_path):
    A.DB = tmp_path / "t.db"
    A.init_db()
    return A.app.test_client()


def test_ages_2_3_have_served_creatures():
    served2 = [m["key"] for m in A.AGE_META[2] if m["topics"]]
    served3 = [m["key"] for m in A.AGE_META[3] if m["topics"]]
    assert "dunkleosteus" in served2 and "hyneria" in served2 and "stethacanthus" in served2
    assert "meganeura" in served3 and "pholiderpeton" in served3


def test_age_maps_and_stations_render(tmp_path):
    c = _client(tmp_path)
    for path in ("/map/child_a/2", "/map/child_a/3", "/station/child_a/dunkleosteus",
                 "/station/child_a/meganeura", "/museum/child_a/2", "/museum/child_a/3",
                 "/dig/child_a/2", "/dig/child_a/3"):
        assert c.get(path).status_code == 200, path
    assert c.get("/map/child_a/9").status_code == 404     # no such age


def test_age2_3_serve_verified_questions_with_lessons(tmp_path):
    c = _client(tmp_path)
    for topic in ("MA-C08", "MA-F07", "MA-F11", "VR-D01", "MA-B03", "MA-B05", "MA-B08"):
        q = c.get(f"/api/question?who=child_a&topic={topic}&level=3").get_json()
        if "error" in q:
            q = c.get(f"/api/question?who=child_a&topic={topic}&level=2").get_json()
        assert q.get("stem"), f"{topic} served no question"
        les = c.get(f"/api/lesson/{topic}").get_json()["markdown"]
        assert "Coming soon" not in les, f"{topic} has no lesson"


def test_locked_creatures_are_not_servable(tmp_path):
    c = _client(tmp_path)
    # reading-comprehension creatures (judgement language) must stay locked
    assert c.get("/station/child_a/opabinia").status_code == 404      # Age-1 comprehension
    assert c.get("/station/child_a/cladoselache").status_code == 404  # Age-2 comprehension
