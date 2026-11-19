#!/usr/bin/env python3
"""
Generate a one-page printable approval sheet for the parent (Phase 1b decision 3):
one row per creature with the fact, both sources and a tick box. The parent ticks
each row they approve; nothing is served to a child until fact_card.verified is
set true. Writes content/creature_approval_sheet.md.
"""
from pathlib import Path

import yaml

from creature_facts import THINLY_SOURCED

ROOT = Path(__file__).resolve().parent.parent


def main():
    creatures = yaml.safe_load((ROOT / "content" / "creatures.yaml").read_text())["creatures"]
    ages = {a["id"]: a["name"]
            for a in yaml.safe_load((ROOT / "content" / "ages.yaml").read_text())["ages"]}

    L = ["# Creature fact-card approval sheet", "",
         "Print this, tick each row whose fact and sources you are happy with, then",
         "tell me and I will set `verified: true` for the ticked creatures. Until then",
         "**no fact card is shown to a child**. ⚠ = sourced only from peer-reviewed",
         "papers / general pages (no dedicated kid-friendly museum page) — you may",
         "accept it or ask me to swap the creature.", "",
         "| ✓ | Age | Creature | Fact | Source 1 | Source 2 |",
         "|---|---|---|---|---|---|"]
    for c in creatures:
        name = c["name"]
        if c.get("pronunciation"):
            name += f" _(say: {c['pronunciation']})_"
        if name.split(" _")[0] in THINLY_SOURCED or c["name"] in THINLY_SOURCED:
            name = "⚠ " + name
        fc = c["fact_card"]
        L.append(f"| ☐ | {c['age']}. {ages[c['age']]} | {name} | {fc['fact']} | "
                 f"[source 1]({fc['source_1']}) | [source 2]({fc['source_2']}) |")
    L += ["", f"**{len(creatures)} creatures.** ⚠ thinly-sourced: "
          + ", ".join(sorted(THINLY_SOURCED)) + ".",
          "", "Facts checked 2026-11-14; `verified: false` for all until you approve."]
    (ROOT / "content" / "creature_approval_sheet.md").write_text("\n".join(L) + "\n")
    print(f"Wrote content/creature_approval_sheet.md ({len(creatures)} rows)")


if __name__ == "__main__":
    main()
