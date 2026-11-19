"""Honest level labelling. Age 1 may now serve 11+ multi-step levels (3-5), but
ONLY where every item is verified by TWO independent methods (a forward solver
AND a different-method cross-check). Foundation levels (1-2) stay single-step.
The served-status report must describe this truthfully."""
import json

import yaml

import parse_syllabus as P

SERVED = yaml.safe_load((P.ROOT / "content" / "age1" / "served.yaml").read_text())["topics"]
BANKS = P.ROOT / "content" / "age1" / "banks"


def _max_served_level():
    return max((lv for r in SERVED if r.get("status") == "served"
                for lv in r.get("levels", [])), default=0)


def test_served_levels_are_in_range():
    for r in SERVED:
        if r.get("status") != "served":
            continue
        for lv in r.get("levels", []):
            assert 1 <= lv <= 5, f"{r['id']} serves out-of-range level {lv}"


def test_served_l3plus_requires_dual_method_verification():
    for r in SERVED:
        if r.get("status") != "served":
            continue
        for lv in r.get("levels", []):
            if lv < 3:
                continue
            f = BANKS / f"{r['id']}__L{lv}.json"
            assert f.exists(), f"{r['id']} L{lv} served but no bank on disk"
            items = json.loads(f.read_text())
            assert items, f"{r['id']} L{lv} bank is empty"
            names = {c["name"] for c in items[0]["verification"]["checks"]}
            assert {"independent_solver", "second_method"} <= names, (
                f"{r['id']} L{lv}: an 11+ level without dual-method verification "
                "must not be served")


def test_served_status_report_is_honest():
    report = (P.ROOT / "reports" / "age1_served_status.md").read_text().lower()
    if _max_served_level() >= 3:
        assert "two independent methods" in report, "report must disclose the L3-5 dual check"
    else:
        assert "foundation" in report and "not yet built or claimed" in report
