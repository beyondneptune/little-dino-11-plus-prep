"""NVR (SVG) tests: every served item must have a UNIQUE computed answer; the
independent solver (which does not see the generator's rule) must re-derive it;
ambiguous items must be rejected; a wrong key must be caught."""
import nvr_svg as N
from nvr_svg import Fig


def test_series_solver_reinfers_rule_uniquely():
    for it in N.build("series", 60):
        # solve_series is given only the figures, not it["rule"]
        idx = N.solve_series(it["seq"], it["options"])
        assert idx == it["answer_index"], f"series solver {idx} != {it['answer_index']}"


def test_odd_solver_unique():
    for it in N.build("odd", 60):
        assert N.solve_odd(it["options"]) == it["answer_index"]


def test_build_items_all_pass_verify():
    for kind in ("series", "odd"):
        items = N.build(kind, 40)
        assert len(items) == 40
        for it in items:
            ok, reason = N.verify(it)
            assert ok, f"{kind}: {reason}"


def test_ambiguous_odd_is_rejected():
    # two different properties each single out a different figure -> ambiguous
    figs = [Fig("square", 0, 1, False), Fig("square", 90, 1, False),
            Fig("square", 180, 1, True),      # the only shaded one
            Fig("square", 270, 1, False),
            Fig("triangle", 0, 1, False)]     # the only triangle
    item = {"type": "odd", "options": figs, "answer_index": 4}
    assert N.solve_odd(figs) is None, "ambiguous odd-one-out should have no unique answer"
    ok, reason = N.verify(item)
    assert not ok and "ambiguous" in reason


def test_non_rule_series_has_no_solution():
    seq = [Fig("square", 0, 1, False), Fig("triangle", 90, 2, True),
           Fig("pentagon", 180, 1, False), Fig("hexagon", 0, 3, True)]  # follows no single rule
    assert N.solve_series(seq, [Fig("square", 0, 1, False)] * 1 + [Fig("triangle", 0, 1, False)] * 3) is None


def test_wrong_key_is_caught():
    it = N.build("series", 5)[0]
    bad = dict(it, answer_index=(it["answer_index"] + 1) % 4)
    ok, _ = N.verify(bad)
    assert not ok, "a flipped answer key must fail verification"


def test_svg_is_wellformed():
    svg = N.figure_svg(Fig("pentagon", 90, 3, True))
    assert svg.startswith("<svg") and "polygon" in svg and svg.rstrip().endswith("</svg>")
