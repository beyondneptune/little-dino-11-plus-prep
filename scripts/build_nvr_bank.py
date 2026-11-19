#!/usr/bin/env python3
"""Build a served NVR bank (content/age1/nvr_bank.json) from the verified,
uniqueness-proving generators in nvr_svg.py. Each item is pre-rendered to clean
SVG (sequence figures + option figures) with the answer index and a plain-English
explanation, so the Wiwaxia station can serve tap-the-picture NVR items.

Topics: NV-A01 (series / next figure) and NV-C01 (odd one out). Only items whose
answer is proven UNIQUE by nvr_svg.verify are written.
"""
from __future__ import annotations

import json
from pathlib import Path

import nvr_svg as N

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "content" / "age1" / "nvr_bank.json"
PER = 80

RULE_WORDS = {
    ("rotate", 90): "each figure turns a quarter-turn",
    ("rotate", 180): "each figure turns halfway round",
    ("count", 1): "there is one more dot each time",
    ("shade", 0): "the shading flips each time",
    ("grow", 1): "the shape gains a side each time",
}
PROP_WORDS = {"shape": "it is a different shape", "shaded": "it is shaded differently",
              "count": "it has a different number of dots", "rot": "it points a different way"}


def _item(it, topic):
    key = N.LETTERS[it["answer_index"]]
    if it["type"] == "series":
        prompt = "Which figure comes next in the series?"
        seq = [N.figure_svg(f) for f in it["seq"]]
        expl = f"The pattern is: {RULE_WORDS.get(it['rule'], 'a steady rule')}. The next figure is {key}."
    else:
        prompt = "Which one is the odd one out?"
        seq = []
        expl = f"Figure {key} is the odd one out — {PROP_WORDS.get(it['prop'], 'it breaks the pattern')}."
    return {
        "id": f"nvr:{topic}:{it['type']}:{abs(hash(tuple(o.as_tuple() for o in it['options']))) & 0xffffffff:x}",
        "topic": topic, "type": it["type"], "prompt": prompt,
        "seq": seq, "options": [N.figure_svg(o) for o in it["options"]],
        "answer_index": it["answer_index"], "explanation": expl,
    }


def main():
    bank = {"NV-A01": [], "NV-C01": []}
    for it in N.build("series", PER):
        ok, _ = N.verify(it)
        if ok:
            bank["NV-A01"].append(_item(it, "NV-A01"))
    for it in N.build("odd", PER):
        ok, _ = N.verify(it)
        if ok:
            bank["NV-C01"].append(_item(it, "NV-C01"))
    OUT.write_text(json.dumps(bank, ensure_ascii=False))
    print("NVR bank:", {k: len(v) for k, v in bank.items()}, "->", OUT.relative_to(ROOT))
    return bank


if __name__ == "__main__":
    main()
