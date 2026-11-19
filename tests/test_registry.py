"""The generator+solver registry must be internally sound (parent STEP 1c/1a):
every entry's generator and independent solver agree, and the question template
matches the topic it is registered under; verifier_status is derived from it."""
import yaml

import parse_syllabus as P
import registry as R
from taxonomy_rules import verifier_status


def test_registry_validates():
    issues = R.validate()
    assert not issues, "registry problems:\n" + "\n".join(issues)


def test_every_registry_topic_is_a_real_syllabus_topic():
    master = {t["id"] for t in P.parse()}
    for t in R.registry_topics():
        assert t in master, f"registry claims unknown topic {t}"


def test_verifier_status_matches_registry():
    # topics.yaml verifier_status must equal 'built' iff the topic is in the registry
    topics = yaml.safe_load((P.ROOT / "content" / "topics.yaml").read_text())["topics"]
    reg = R.registry_topics()
    for t in topics:
        want = "built" if t["id"] in reg else "to_build"
        assert t["verifier_status"] == want, \
            f"{t['id']} verifier_status {t['verifier_status']} != {want}"
        assert verifier_status(t) == want


def test_ma_b01_is_single_operation_not_order_of_operations():
    """Guards the exact bug the parent caught: MA-B01 must be mental single-op,
    and the a*b+-c order-of-operations template must live under MA-B05."""
    b01 = [e for e in R.REGISTRY if e.topic == "MA-B01"]
    assert b01 and all("× \\d+ [+−]" not in (e.stem_re or "") for e in b01)
    b05 = [e for e in R.REGISTRY if e.topic == "MA-B05"]
    assert b05 and any("× " in (e.stem_re or "") and "[+−]" in (e.stem_re or "") for e in b05)
