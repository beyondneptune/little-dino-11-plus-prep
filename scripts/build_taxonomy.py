#!/usr/bin/env python3
"""
Build the Dino Ages taxonomy: content/ages.yaml, content/creatures.yaml and
content/topics.yaml, from the master syllabus (via parse_syllabus) + the rules
in brief v2 section 3.

Everything here is DERIVED and DETERMINISTIC — rerun it any time. Topic ids and
titles always come from the parser, so content/topics.yaml can never drift from
the master (tests/test_syllabus_sync guards that).

Placement rules implemented (brief 3b):
  * Age > Creature > Topic. 10 ages in geological order.
  * 6 creatures per age: 2 Maths, 2 English, 1 VR, 1 NVR. Each creature is one
    subject strand with 4-7 topics in prerequisite order.
  * Each age holds 30-38 subject topics (target ~34). Subject mix per age within
    +-2 percentage points of 38/35/13/14 (Maths/English/VR/NVR).
  * Stretch and EN-H (creative writing) topics only in Age 6+.
  * ET-01..ET-11 are homed to the Fossil Dig of Ages 4-10 (not a subject
    creature) — see NOTE below.
  * A topic is never taught before its prerequisites.
  * Spiral: topics get return_visits in later ages.

NOTE on ET: exam technique is about timing, answer sheets, skipping/returning
and reviewing errors — not a single subject. The 6 creatures per age stay purely
Maths/English/VR/NVR (so the subject mix maths is clean and matches the brief's
38/35/13/14, which sums to 100 without ET). Each ET topic's home is its age's
Fossil Dig (the timed mixed test), which is exactly where exam technique belongs.
Flagged for parent approval in the checkpoint report.

NOTE on foundations: only ~77 of the 340 topics are genuinely Year 3-4 SCHOOL
level (English fits; VR/NVR are reasoning skills schools do not teach at all, so
almost none are "school level"). To keep Ages 1-3 at >=30 topics each, they
necessarily include some above-Year-4 topics. build_report() lists exactly which
(this is the honest finding required by rule 3b: tell the parent, do not bend).
"""
from __future__ import annotations

from pathlib import Path

import parse_syllabus as P
from creature_facts import FACTS
from taxonomy_rules import content_readiness, verifier_status

ROOT = P.ROOT
CONTENT = ROOT / "content"
SUBJECTS = ["Maths", "English", "VR", "NVR"]

# --- 10 ages (brief 3a), with geological periods (fact-checked in step 5) ------
AGES = [
    (1,  "Cambrian Seas",            "Cambrian (~538-485 Ma)",          "foundations", (1, 2)),
    (2,  "Devonian (Age of Fishes)", "Devonian (~419-359 Ma)",          "foundations", (1, 2)),
    (3,  "Carboniferous Swamps",     "Carboniferous (~359-299 Ma)",     "foundations", (1, 2)),
    (4,  "Permian Wilds",            "Permian (~299-252 Ma)",           "core",        (2, 4)),
    (5,  "Triassic",                 "Triassic (~252-201 Ma)",          "core",        (2, 4)),
    (6,  "Jurassic",                 "Jurassic (~201-145 Ma)",          "core",        (2, 4)),
    (7,  "Early Cretaceous",         "Early Cretaceous (~145-100 Ma)",  "stretch",     (3, 5)),
    (8,  "Late Cretaceous",          "Late Cretaceous (~100-66 Ma)",    "stretch",     (3, 5)),
    (9,  "Paleogene (Rise of Mammals)", "Paleogene (~66-23 Ma)",        "stretch",     (3, 5)),
    (10, "Ice Age",                  "Quaternary / Pleistocene (~2.6 Ma-11.7 ka)", "stretch+mocks", (3, 5)),
]

# --- suggested creatures per age (brief 3a); subjects assigned by position -----
# positions: 0,1 -> Maths; 2,3 -> English; 4 -> VR; 5 -> NVR
CREATURES = {
    1:  ["Trilobite", "Anomalocaris", "Opabinia", "Hallucigenia", "Pikaia", "Wiwaxia"],
    2:  ["Dunkleosteus", "Tiktaalik", "Cladoselache", "Eusthenopteron", "Hyneria", "Stethacanthus"],
    3:  ["Meganeura", "Arthropleura", "Hylonomus", "Pulmonoscorpius", "Petrolacosaurus", "Pholiderpeton"],
    4:  ["Dimetrodon", "Edaphosaurus", "Gorgonops", "Inostrancevia", "Helicoprion", "Diadectes"],
    5:  ["Eoraptor", "Herrerasaurus", "Coelophysis", "Plateosaurus", "Postosuchus", "Tanystropheus"],
    6:  ["Brachiosaurus", "Diplodocus", "Stegosaurus", "Allosaurus", "Ceratosaurus", "Archaeopteryx"],
    7:  ["Iguanodon", "Deinonychus", "Utahraptor", "Baryonyx", "Polacanthus", "Hypsilophodon"],
    8:  ["Tyrannosaurus rex", "Triceratops", "Velociraptor", "Ankylosaurus", "Pachycephalosaurus", "Parasaurolophus"],
    9:  ["Titanoboa", "Gastornis", "Basilosaurus", "Uintatherium", "Paraceratherium", "Andrewsarchus"],
    10: ["Woolly mammoth", "Smilodon", "Woolly rhinoceros", "Megatherium", "Megaloceros", "Cave bear"],
}
CREATURE_SUBJECT_BY_POS = ["Maths", "Maths", "English", "English", "VR", "NVR"]

# Real dinosaurs only, and only in Ages 5-8 (brief rule 5 / 3a). Archaeopteryx is
# an avialan theropod dinosaur (NHM) — kept true, noted in the fact-check.
REAL_DINOSAURS = {
    "Eoraptor", "Herrerasaurus", "Coelophysis", "Plateosaurus",       # age 5
    "Brachiosaurus", "Diplodocus", "Stegosaurus", "Allosaurus",
    "Ceratosaurus", "Archaeopteryx",                                  # age 6
    "Iguanodon", "Deinonychus", "Utahraptor", "Baryonyx",
    "Polacanthus", "Hypsilophodon",                                   # age 7
    "Tyrannosaurus rex", "Triceratops", "Velociraptor", "Ankylosaurus",
    "Pachycephalosaurus", "Parasaurolophus",                          # age 8
}

# --- per-age subject counts (derived; see module docstring / report) -----------
# sums: Maths 128, English 119, VR 45, NVR 48; every age total in 30-38.
PER_AGE = {
    "Maths":   [13, 13, 13, 13, 13, 13, 13, 13, 12, 12],
    "English": [12, 12, 12, 12, 12, 12, 12, 12, 12, 11],
    "VR":      [5,  5,  5,  4,  5,  4,  5,  4,  4,  4],
    "NVR":     [5,  5,  5,  5,  5,  5,  5,  4,  5,  4],
}

# ET-01..ET-11 across the Fossil Digs of Ages 4-10 (brief 3b).
ET_BY_AGE = {4: 1, 5: 1, 6: 1, 7: 2, 8: 2, 9: 2, 10: 2}

# --- foundational (Year 3-4) topic ids: pulled into the early ages first -------
# English maps cleanly to Year 3-4 school content; Maths partly; VR/NVR barely
# (schools do not teach reasoning), so the early ages introduce the gentlest
# versions of those. This set defines "difficulty 1" ordering, nothing else.
FOUNDATION_IDS = {
    # Maths (Year 3-4 arithmetic/shape/measure/data)
    "MA-A02", "MA-A03", "MA-A05", "MA-A07", "MA-A08", "MA-A09",
    "MA-B01", "MA-B02", "MA-B04", "MA-B06", "MA-B13",
    "MA-C01", "MA-C02", "MA-C03", "MA-C08", "MA-C10",
    "MA-F01", "MA-F05", "MA-F07", "MA-F11", "MA-F12",
    "MA-G01", "MA-G03", "MA-G09", "MA-G10",
    "MA-I01", "MA-I02", "MA-I04",
    # English (Year 3-4 reading / grammar / punctuation / spelling / vocab)
    "EN-A01", "EN-A02", "EN-A03", "EN-A04", "EN-A05", "EN-A06", "EN-A07",
    "EN-B01", "EN-B02", "EN-B06", "EN-B08",
    "EN-C01", "EN-C02", "EN-C03",
    "EN-D01", "EN-D02", "EN-D03", "EN-D04", "EN-D05", "EN-D06", "EN-D07", "EN-D08", "EN-D16",
    "EN-E01", "EN-E02", "EN-E03", "EN-E05", "EN-E06", "EN-E07",
    "EN-F01", "EN-F02", "EN-F03", "EN-F04", "EN-F05", "EN-F09", "EN-F10",
    # VR (gentlest)
    "VR-A01", "VR-A02", "VR-A05", "VR-C01", "VR-C02", "VR-D01", "VR-D02",
    # NVR (gentlest)
    "NV-A01", "NV-A02", "NV-A03", "NV-C01", "NV-C03", "NV-C05",
}


def _section(tid: str) -> str:
    """'MA-C05' -> 'MA-C'; 'ET-01' -> 'ET'."""
    tail = tid.split("-", 1)[1]
    return tid.split("-", 1)[0] + "-" + (tail[0] if tail[0].isalpha() else "")


def _gated(t: dict) -> bool:
    """Stretch or EN-H (creative writing): only Age 6+."""
    return t["level"] in ("Stretch", "School-specific")


def _order_rank(t: dict) -> int:
    """0 foundation, 1 normal core, 2 stretch/EN-H — easiest first."""
    if _gated(t):
        return 2
    if t["id"] in FOUNDATION_IDS:
        return 0
    return 1


def _band_level(age_id: int) -> int:
    if age_id <= 3:
        return 2
    if age_id <= 6:
        return 3
    if age_id <= 9:
        return 4
    return 5


def place(topics: list[dict]) -> dict:
    """Return {id: {age, creature, station, prerequisites, return_visits}} plus
    the per-age creature->topics structure. Pure function of the parsed topics."""
    subj_topics = {s: [] for s in SUBJECTS}
    et_topics = []
    for t in topics:
        if t["subject"] == "ET":
            et_topics.append(t)
        else:
            subj_topics[t["subject"]].append(t)

    # --- assign a home age per subject topic (easiest -> earliest age) ---------
    home_age: dict[str, int] = {}
    for subj in SUBJECTS:
        ordered = sorted(subj_topics[subj], key=lambda t: (_order_rank(t), t["id"]))
        counts = PER_AGE[subj]
        assert sum(counts) == len(ordered), (subj, sum(counts), len(ordered))
        i = 0
        for age_idx, n in enumerate(counts, start=1):
            for t in ordered[i:i + n]:
                home_age[t["id"]] = age_idx
            i += n

    # --- enforce the Age-6+ gate for stretch/EN-H (should already hold) --------
    for t in topics:
        if t["subject"] != "ET" and _gated(t) and home_age[t["id"]] < 6:
            raise AssertionError(f"gated topic {t['id']} placed before Age 6")

    # --- split each age's subject topics into creatures -----------------------
    # creature topics in (age,id) prerequisite order.
    by_id = {t["id"]: t for t in topics}
    age_subject_topics: dict[int, dict[str, list[str]]] = {
        a: {s: [] for s in SUBJECTS} for a in range(1, 11)
    }
    for tid, a in home_age.items():
        age_subject_topics[a][by_id[tid]["subject"]].append(tid)
    for a in range(1, 11):
        for s in SUBJECTS:
            age_subject_topics[a][s].sort()

    creatures = []  # list of dicts (ordered)
    creature_of: dict[str, str] = {}
    for a in range(1, 11):
        names = CREATURES[a]
        # how many creatures per subject this age (2 Maths, 2 English, 1 VR, 1 NVR)
        for pos, name in enumerate(names):
            subj = CREATURE_SUBJECT_BY_POS[pos]
            cid = f"a{a:02d}-{_slug(name)}"
            creatures.append({"id": cid, "age": a, "subject": subj, "name": name,
                              "is_dinosaur": name in REAL_DINOSAURS, "topics": []})
        # distribute topics: Maths -> first two creatures, English -> next two,
        # VR -> fifth, NVR -> sixth.
        age_creatures = [c for c in creatures if c["age"] == a]
        _fill_subject(age_creatures, "Maths", age_subject_topics[a]["Maths"])
        _fill_subject(age_creatures, "English", age_subject_topics[a]["English"])
        _fill_subject(age_creatures, "VR", age_subject_topics[a]["VR"])
        _fill_subject(age_creatures, "NVR", age_subject_topics[a]["NVR"])
    for c in creatures:
        for tid in c["topics"]:
            creature_of[tid] = c["id"]

    # --- ET -> Fossil Digs of Ages 4-10 ---------------------------------------
    et_sorted = sorted(et_topics, key=lambda t: t["id"])
    et_home: dict[str, int] = {}
    fossil_et: dict[int, list[str]] = {a: [] for a in range(1, 11)}
    k = 0
    for a in range(4, 11):
        for _ in range(ET_BY_AGE.get(a, 0)):
            tid = et_sorted[k]["id"]
            et_home[tid] = a
            fossil_et[a].append(tid)
            k += 1
    assert k == len(et_sorted), (k, len(et_sorted))

    # --- prerequisites: previous topic in same section by (age, id) -----------
    prereqs: dict[str, list[str]] = {}
    full_age = dict(home_age)
    full_age.update(et_home)
    by_section: dict[str, list[str]] = {}
    for t in topics:
        by_section.setdefault(_section(t["id"]), []).append(t["id"])
    for sec, ids in by_section.items():
        ids_sorted = sorted(ids, key=lambda i: (full_age[i], i))
        prev = None
        for i in ids_sorted:
            prereqs[i] = [prev] if prev else []
            prev = i

    # --- spiral return visits: home age <= 7 -> one visit at home+3 -----------
    return_visits: dict[str, list[dict]] = {}
    for t in topics:
        a = full_age[t["id"]]
        if t["subject"] != "ET" and a <= 7:
            ra = min(a + 3, 10)
            return_visits[t["id"]] = [{"age": ra, "level": _band_level(ra)}]
        else:
            return_visits[t["id"]] = []

    return {
        "home_age": full_age, "creature_of": creature_of, "et_home": et_home,
        "fossil_et": fossil_et, "creatures": creatures, "prereqs": prereqs,
        "return_visits": return_visits, "age_subject_topics": age_subject_topics,
    }


def _fill_subject(age_creatures, subject, tids):
    cs = [c for c in age_creatures if c["subject"] == subject]
    if len(cs) == 1:
        cs[0]["topics"] = list(tids)
        return
    # two creatures: split as evenly as possible, first gets the ceiling.
    half = (len(tids) + 1) // 2
    cs[0]["topics"] = list(tids[:half])
    cs[1]["topics"] = list(tids[half:])


def _slug(name: str) -> str:
    return name.lower().replace(". ", "-").replace(" ", "-").replace(".", "")


def _q(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_files(topics, pl):
    _write_ages(pl)
    _write_creatures(pl)
    _write_topics(topics, pl)


def _write_ages(pl):
    L = ["# GENERATED by scripts/build_taxonomy.py — do not edit by hand.",
         "# 10 ages in geological order (brief 3a). Periods fact-checked in step 5.",
         "ages:"]
    for (aid, name, period, band, lr) in AGES:
        et = pl["fossil_et"][aid]
        L += [
            f"  - id: {aid}",
            f"    name: {_q(name)}",
            f"    period: {_q(period)}",
            f"    band: {band}",
            f"    level_range: [{lr[0]}, {lr[1]}]",
            f"    fossil_dig:",
            f"      name: {_q(name + ' Fossil Dig')}",
            f"      review_fraction: 0.25",
            f"      et_topics: [{', '.join(et)}]",
        ]
    (CONTENT / "ages.yaml").write_text("\n".join(L) + "\n")


def _write_creatures(pl):
    L = ["# GENERATED by scripts/build_taxonomy.py — do not edit by hand.",
         "# 6 creatures per age (2 Maths, 2 English, 1 VR, 1 NVR). Biology fields",
         "# (group/diet/size) and fact cards are filled + fact-checked in step 5;",
         "# fact_card.verified stays false until the parent approves.",
         "creatures:"]
    missing = [c["name"] for c in pl["creatures"] if c["name"] not in FACTS]
    if missing:
        raise AssertionError(f"no fact-check data for creatures: {missing}")
    for c in pl["creatures"]:
        f = FACTS[c["name"]]
        L += [
            f"  - id: {c['id']}",
            f"    name: {_q(c['name'])}",
            f"    pronunciation: {_q(f.get('pronunciation', ''))}",
            f"    age: {c['age']}",
            f"    subject: {c['subject']}",
            f"    is_dinosaur: {str(c['is_dinosaur']).lower()}",
            f"    group: {_q(f['group'])}",
            f"    diet: {_q(f['diet'])}",
            f"    size: {_q(f['size'])}",
            f"    lived: {_q(f['lived'])}",
            f"    topics: [{', '.join(c['topics'])}]",
            f"    fact_card:",
            f"      fact: {_q(f['fact'])}",
            f"      source_1: {_q(f['source_1'])}",
            f"      source_2: {_q(f['source_2'])}",
            f"      verified: false",
        ]
    (CONTENT / "creatures.yaml").write_text("\n".join(L) + "\n")


def _write_topics(topics, pl):
    L = [
     "# ============================================================================",
     "# Dino Ages topic taxonomy — the 351 topics of the master syllabus, placed.",
     "#",
     "# GENERATED by scripts/build_taxonomy.py from '11 Syllabus Master Topic List.md'",
     "# (ids + titles verbatim, never retyped). tests/test_syllabus_sync.py fails the",
     "# build if this drifts from the master. tests/test_taxonomy.py checks placement.",
     "#",
     "# Fields: id, subject, title, level, content_readiness (V/R/P), age (home age),",
     "#   creature (home creature id; null for ET), station (fossil_dig for ET),",
     "#   prerequisites[], tested_by[] (empty until a target school is confirmed),",
     "#   return_visits[] (spiral: later {age, level}).",
     "# ============================================================================",
     "",
     "topics:",
    ]
    for t in topics:
        tid = t["id"]
        r = content_readiness(t)
        a = pl["home_age"][tid]
        if t["subject"] == "ET":
            home = "creature: null, station: fossil_dig"
        else:
            home = f"creature: {pl['creature_of'][tid]}"
        pr = "[" + ", ".join(pl["prereqs"].get(tid, [])) + "]"
        rv = "[" + ", ".join("{age: %d, level: %d}" % (v["age"], v["level"])
                             for v in pl["return_visits"].get(tid, [])) + "]"
        vs = verifier_status(t)
        # 'preview' (DECISIONS D1): above-Year-3/4 topics placed in Ages 1-3 are
        # introduced gently but not required for mastery / to open the next age
        # until their spiral return visit.
        preview = (t["subject"] in SUBJECTS and a <= 3 and tid not in FOUNDATION_IDS)
        prev = "preview: true, " if preview else ""
        L.append(
            f"  - {{id: {tid}, subject: {t['subject']}, level: {t['level']}, "
            f"content_readiness: {r}, verifier_status: {vs}, {prev}age: {a}, {home}, "
            f"prerequisites: {pr}, tested_by: [], return_visits: {rv},")
        L.append(f"     title: {_q(t['title'])}}}")
    (CONTENT / "topics.yaml").write_text("\n".join(L) + "\n")


def main():
    topics = P.parse()
    P.check(topics)
    pl = place(topics)
    write_files(topics, pl)
    # quick self-report
    print("Ages:", len(AGES), " Creatures:", len(pl["creatures"]),
          " Topics placed:", len(pl["home_age"]))
    for a in range(1, 11):
        counts = {s: len(pl["age_subject_topics"][a][s]) for s in SUBJECTS}
        tot = sum(counts.values())
        et = len(pl["fossil_et"][a])
        print(f"  Age {a:>2}: " + " ".join(f"{s[:2]}{counts[s]:>2}" for s in SUBJECTS)
              + f"  subj_total={tot:>2}  ET={et}")


if __name__ == "__main__":
    main()
