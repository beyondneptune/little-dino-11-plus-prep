#!/usr/bin/env python3
"""
Dino Ages — playable Age 1 (Cambrian Seas) slice (UI overhaul).

Serves ONLY verified questions from the gated banks (content/age1/banks), through
the qschema serve gate, re-checked at serve time. The ENGINE (generators, solver,
serve gate, mastery logic) is unchanged by the UI overhaul — this file only
presents what the API serves. Profiles for Child A and Child B with separate
progress; a parent area behind a PIN; no external network requests (fonts, CSS,
JS, art are all local).

Run:  .venv/bin/python platform/age1_app.py            (http://127.0.0.1:5000)
"""
from __future__ import annotations

import json
import random
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

import yaml
from flask import (Flask, abort, g, jsonify, redirect, render_template_string,
                   request, send_from_directory, session, url_for)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from qschema import Check, Question, VerificationRecord  # noqa: E402

import mastery  # noqa: E402  (state model shared with the engine/tests)
import answer_norm  # noqa: E402  (typed-answer normaliser)

DB = Path(__file__).resolve().parent / "age1.db"

PROFILES = {"child_a": ("Child A", "#59c08a"), "child_b": ("Child B", "#ff9a5c")}
AGES = (1, 2, 3)
AGE_THEME = {1: "cambrian", 2: "devonian", 3: "carboniferous"}
AGE_NAME = {1: "Cambrian Seas", 2: "Devonian Seas", 3: "Carboniferous Swamps"}
# six map slots (shared layout) + the Fossil Dig slot
SLOTS = [(18, 34), (46, 52), (74, 34), (82, 60), (20, 72), (48, 82)]
FOSSIL_SLOT = (80, 84)


def banks_dir(age):
    return ROOT / "content" / f"age{age}" / "banks"


def lessons_dir(age):
    return ROOT / "content" / f"age{age}" / "lessons"


# topics served in TYPED-ANSWER mode (fully-computable answer set; for written-answer
# entrance tests / second-stage papers). MCQ stays the default.
TYPED_TOPICS = {"MA-B06", "MA-F11", "EN-F10"}      # plurals: type the word (spelling stays MCQ)
TOPIC_TITLES = {"MA-A05": "Rounding", "MA-B01": "Mental calculations",
                "MA-B04": "Division facts", "VR-C02": "Letter sequences",
                "MA-A03": "Comparing numbers", "MA-A07": "Roman numerals",
                "MA-B06": "Missing numbers", "MA-B13": "Odd, even & multiples",
                "MA-C08": "Fractions of amounts", "MA-F07": "Perimeter",
                "MA-F11": "Money & change", "VR-D01": "Number sequences",
                "MA-B05": "Order of operations", "MA-B03": "Long multiplication",
                "MA-B08": "Prime numbers",
                "EN-B06": "Prefixes & suffixes", "EN-D07": "Sentence grammar",
                "EN-E06": "Apostrophes", "EN-F01": "Spelling",
                "EN-F09": "Homophones", "EN-F10": "Plurals"}
GREETS = {
    "trilobite": "Hello! I've rolled through these warm seas for ages. Shall we practise some number skills together?",
    "anomalocaris": "I'm the great hunter of the Cambrian! Can you help me hunt down these division facts?",
    "pikaia": "I wiggle like a little ribbon. Let's spot the pattern hiding in these letters!",
    "dunkleosteus": "I'm the armoured giant of the Devonian seas. Ready for some trickier number work?",
    "hyneria": "I lurk in the deep for number patterns. Can you find what comes next?",
    "stethacanthus": "I'm an early shark! Let's hunt for the odd shape out.",
    "meganeura": "I buzz over the swamp on giant wings. Fancy some big multiplication?",
    "pholiderpeton": "I slither through the swamp. Spot the shape pattern with me!",
    "hallucigenia": "I'm a spiky little puzzle! Let's build some words with prefixes and suffixes.",
    "eusthenopteron": "I'm learning to crawl onto land. Help me get my sentences right!",
    "hylonomus": "I'm one of the first reptiles. Let's sort out spelling and apostrophes.",
    "pulmonoscorpius": "I'm a giant scorpion! Let's pinch down the right spellings and plurals.",
}
DEFAULT_GREET = {1: "Let's explore the Cambrian!", 2: "Welcome to the Devonian seas!",
                 3: "Welcome to the steamy Carboniferous swamp!"}

app = Flask(__name__)
app.secret_key = "dino-ages-local-only"


# ---- NVR: image-option items (series + odd-one-out), served at NVR stations ---
def load_nvr():
    f = ROOT / "content" / "age1" / "nvr_bank.json"      # abstract shapes, age-agnostic
    return json.loads(f.read_text()) if f.exists() else {}


NVR_BANK = load_nvr()
NVR_BY_ID = {it["id"]: it for items in NVR_BANK.values() for it in items}
NVR_STATIONS = {"wiwaxia", "stethacanthus", "pholiderpeton"}   # each age's NVR creature
NVR_TOPIC_TITLES = {"NV-A01": "Shape series", "NV-C01": "Odd one out"}

# template-kit figure configs for ages 2-3 creatures (Age-1 uses the hand code kit)
CREATURE_FIG = {
    "dunkleosteus": {"plan": "swimmer", "colors": {"main": "#5a8f9a", "belly": "#dceef0", "accent": "#2d5f68"}, "size": 1.05},
    "hyneria": {"plan": "swimmer", "colors": {"main": "#7a9a4a", "belly": "#eaf3c6", "accent": "#4b6d2e"}},
    "tiktaalik": {"plan": "quadruped", "colors": {"main": "#8a6a4a", "belly": "#efe0c0", "accent": "#5a4028"}},
    "cladoselache": {"plan": "swimmer", "colors": {"main": "#6a7a8a", "belly": "#e4ecf2", "accent": "#3a4a58"}},
    "stethacanthus": {"plan": "swimmer", "colors": {"main": "#5a7a8a", "belly": "#dceef0", "accent": "#36566a"}},
    "eusthenopteron": {"plan": "swimmer", "colors": {"main": "#8a8f5a", "belly": "#eef0c8", "accent": "#5a5f2e"}},
    "meganeura": {"plan": "flyer", "colors": {"main": "#3f9a8a", "belly": "#ddf3ee", "accent": "#2a6f62"}, "crest": True},
    "arthropleura": {"plan": "arthropod", "colors": {"main": "#8a6a3a", "belly": "#efe0c0", "accent": "#5a4020"}},
    "hylonomus": {"plan": "quadruped", "colors": {"main": "#8a7a4a", "belly": "#efe6c6", "accent": "#5a4a28"}},
    "pulmonoscorpius": {"plan": "arthropod", "colors": {"main": "#9a6a4a", "belly": "#f0dccb", "accent": "#6a3a28"}},
    "petrolacosaurus": {"plan": "quadruped", "colors": {"main": "#6a8f5a", "belly": "#e7f0cc", "accent": "#41602e"}},
    "pholiderpeton": {"plan": "swimmer", "colors": {"main": "#5a8a7a", "belly": "#dcefe8", "accent": "#376258"}},
}


# --------------------------- gated question banks ----------------------------
def _to_question(d: dict) -> Question:
    v = d.get("verification")
    rec = VerificationRecord(method=v["method"], verifier_version=v["verifier_version"],
                             checks=[Check(**c) for c in v["checks"]]) if v else None
    return Question(verification=rec, **{k: val for k, val in d.items() if k != "verification"})


def load_banks() -> dict:
    banks = {}
    for age in AGES:
        for f in sorted(banks_dir(age).glob("*__L*.json")):
            topic, level = f.stem.split("__L")
            qs = [_to_question(d) for d in json.loads(f.read_text())]
            banks[(topic, int(level))] = [q for q in qs if q.servable()]   # serve gate
    return banks


BANK = load_banks()
BY_ID = {q.id: q for items in BANK.values() for q in items}


def _served_levels(age):
    """Served (topic -> [levels]) derived from the banks actually on disk."""
    out = defaultdict(list)
    for (topic, lv) in BANK:
        f = banks_dir(age) / f"{topic}__L{lv}.json"
        if f.exists():
            out[topic].append(lv)
    return {t: sorted(ls) for t, ls in out.items()}


# --------------------------- creature meta per age ---------------------------
def _age_meta(age):
    creatures = [c for c in yaml.safe_load((ROOT / "content" / "creatures.yaml").read_text())["creatures"]
                 if c["age"] == age]
    topics_all = yaml.safe_load((ROOT / "content" / "topics.yaml").read_text())["topics"]
    served = _served_levels(age)
    by_creature = defaultdict(list)
    for t in topics_all:
        if t.get("creature"):
            by_creature[t["creature"]].append(t)
    meta = []
    for c in creatures:
        key = c["id"].split("-", 1)[1]
        st = [t for t in by_creature[c["id"]] if t["id"] in served]
        tlist = [{"id": t["id"], "title": TOPIC_TITLES.get(t["id"], t["title"]),
                  "levels": served[t["id"]], "typed": t["id"] in TYPED_TOPICS} for t in st]
        if key in NVR_STATIONS:
            for tid in ("NV-A01", "NV-C01"):
                if NVR_BANK.get(tid):
                    tlist.append({"id": tid, "title": NVR_TOPIC_TITLES[tid], "levels": [2], "nvr": True})
        meta.append({"key": key, "name": c["name"], "subject": c["subject"],
                     "greet": GREETS.get(key, DEFAULT_GREET[age]), "topics": tlist, "age": age})
    return meta


AGE_META = {age: _age_meta(age) for age in AGES}
KEY_META = {m["key"]: m for age in AGES for m in AGE_META[age]}      # creature key -> meta (unique keys)
KEY_AGE = {m["key"]: age for age in AGES for m in AGE_META[age]}
# backward-compatible Age-1 aliases
AGE1 = AGE_META[1]
AGE1_BY_KEY = {m["key"]: m for m in AGE1}


def _trivial_rounding(q) -> bool:
    """A rounding item whose number is already a multiple of the base is weak
    (nothing to decide). Presentation-layer filter only — bank is untouched."""
    m = re.match(r"\s*Round\s+(\d+)\s+to the nearest\s+(\d+)", q.stem, re.I)
    if not m:
        return False
    n, base = int(m.group(1)), int(m.group(2))
    return base and n % base == 0


def pick_question(topic, level, seen):
    full = BANK.get((topic, level), [])
    fresh = [q for q in full if q.id not in seen]
    pool = [q for q in fresh if not _trivial_rounding(q)] or fresh \
        or [q for q in full if not _trivial_rounding(q)] or full
    return random.choice(pool) if pool else None


def why_wrong(q, chosen) -> str:
    """A short, child-friendly reason the *chosen* option is wrong, derived from
    the stem in the UI layer (engine/keys untouched). Rounding for now; other
    topics fall back to the worked explanation alone."""
    try:
        picked, right = q.options[chosen], q.options[q.answer_index]
    except (IndexError, TypeError):
        return ""
    stem = q.stem
    m = re.match(r"\s*Round\s+(\d+)\s+to the nearest\s+(\d+)", stem, re.I)
    if m:
        n, base = int(m.group(1)), int(m.group(2))
        digit = (n % 10) if base == 10 else (n // 10 % 10)
        place = "ones" if base == 10 else "tens"
        return (f"{picked} isn’t right. The {place} digit of {n} is {digit}, "
                f"and {digit} is {'5 or more, so round up' if digit >= 5 else 'less than 5, so round down'} "
                f"— {n} rounds to {right}.")
    m = re.fullmatch(r"Which of these numbers is the (largest|smallest)\?", stem)
    if m:
        bigger = "bigger" if m.group(1) == "largest" else "smaller"
        return f"{picked} isn’t the {m.group(1)} — {right} is {bigger}."
    m = re.fullmatch(r"Which of these is an (even|odd) number\?", stem)
    if m:
        other = "odd" if m.group(1) == "even" else "even"
        return f"{picked} is an {other} number, so it isn’t the {m.group(1)} one — {right} is."
    m = re.fullmatch(r"Which of these is a multiple of (\d+)\?", stem)
    if m:
        k = int(m.group(1))
        try:
            return f"{picked} isn’t in the {k} times table — {right} is, because {int(right)} ÷ {k} = {int(right) // k}."
        except ValueError:
            return f"{picked} isn’t a multiple of {k} — {right} is."
    if stem.startswith("What number goes in the box?"):
        return f"{picked} doesn’t balance both sides — the missing number is {right}. Use the inverse operation to check."
    if "Roman numeral" in stem:
        return f"{picked} isn’t right — this Roman numeral is {right}."
    return ""


# --------------------------- progress database -------------------------------
def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def _close(_):
    d = g.pop("db", None)
    if d:
        d.close()


def init_db():
    con = sqlite3.connect(DB)
    con.executescript("""
    CREATE TABLE IF NOT EXISTS mastery(profile TEXT, topic TEXT, mastered INT DEFAULT 0,
        attempts INT DEFAULT 0, correct INT DEFAULT 0, sessions INT DEFAULT 0,
        PRIMARY KEY(profile, topic));
    CREATE TABLE IF NOT EXISTS cards(profile TEXT, creature TEXT, PRIMARY KEY(profile, creature));
    CREATE TABLE IF NOT EXISTS setting(k TEXT PRIMARY KEY, v TEXT);
    CREATE TABLE IF NOT EXISTS timespent(profile TEXT, topic TEXT, seconds INT DEFAULT 0,
        PRIMARY KEY(profile, topic));
    CREATE TABLE IF NOT EXISTS fossils(profile TEXT, fossil TEXT, PRIMARY KEY(profile, fossil));
    """)
    # migrate older DBs that predate the sessions column
    cols = {r[1] for r in con.execute("PRAGMA table_info(mastery)")}
    if "sessions" not in cols:
        con.execute("ALTER TABLE mastery ADD COLUMN sessions INT DEFAULT 0")
    con.commit()
    con.close()


def mastered_topics(profile):
    return {r["topic"] for r in db().execute(
        "SELECT topic FROM mastery WHERE profile=? AND mastered=1", (profile,))}


def record_attempt(profile, topic, correct):
    d = db()
    d.execute("INSERT OR IGNORE INTO mastery(profile, topic) VALUES(?,?)", (profile, topic))
    d.execute("UPDATE mastery SET attempts=attempts+1, correct=correct+? WHERE profile=? AND topic=?",
              (1 if correct else 0, profile, topic))
    d.commit()


def topic_stats(profile, topic):
    r = db().execute("SELECT attempts, correct, sessions FROM mastery WHERE profile=? AND topic=?",
                     (profile, topic)).fetchone()
    return (r["attempts"], r["correct"], r["sessions"]) if r else (0, 0, 0)


def record_session(profile, topic):
    """Count one completed session for a topic, then recompute 'Mastered' from
    the strict cross-session rule (never from a single session)."""
    d = db()
    d.execute("INSERT OR IGNORE INTO mastery(profile, topic) VALUES(?,?)", (profile, topic))
    d.execute("UPDATE mastery SET sessions=sessions+1 WHERE profile=? AND topic=?", (profile, topic))
    att, cor, ses = topic_stats(profile, topic)
    if mastery.is_mastered(att, cor, ses):
        d.execute("UPDATE mastery SET mastered=1 WHERE profile=? AND topic=?", (profile, topic))
        done = mastered_topics(profile)
        for m in KEY_META.values():                      # award a creature's card once all its topics are mastered
            if m["topics"] and all(t["id"] in done for t in m["topics"]):
                d.execute("INSERT OR IGNORE INTO cards(profile, creature) VALUES(?,?)", (profile, m["key"]))
    d.commit()
    return {"state": mastery.mastery_state(att, cor, ses),
            "mastered": mastery.is_mastered(att, cor, ses),
            "pct": round(mastery.pct(cor, att)), "attempts": att, "sessions": ses}


def require_profile(who):
    if who not in PROFILES:
        abort(404)


def fact_for(key):
    data = yaml.safe_load((ROOT / "content" / "creatures.yaml").read_text())["creatures"]
    return next(c for c in data if c["id"].endswith(key))


# --------------------------- templates ---------------------------------------
JS = ("creatures", "creature_templates", "themes", "rig", "scene", "audio", "fx", "app")
BASE_MODERN = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Dino Ages</title><link rel="stylesheet" href="/static/age1/ui.css"></head>
<body><div class="stage"></div>{{ body|safe }}
""" + "".join(f'<script src="/static/age1/{m}.js"></script>' for m in JS) + "</body></html>"

BASE_CLASSIC = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dino Ages</title><link rel="stylesheet" href="/static/age1/style.css"></head>
<body class="{{bodyclass}}">{{ body|safe }}</body></html>"""


def page(body, modern=True, bodyclass=""):
    tmpl = BASE_MODERN if modern else BASE_CLASSIC
    return render_template_string(tmpl, body=body, bodyclass=bodyclass)


@app.route("/")
def home():
    players = "".join(
        f'<a class="player" data-who="{k}" data-color="{col}" href="{url_for("age_map", who=k)}">'
        f'<div class="buddy-holder"></div><span class="pname">{name}</span>'
        f'<span class="streak"></span><span class="cont">Continue your expedition ▶</span></a>'
        for k, (name, col) in PROFILES.items())
    body = f"""<div class="content home" data-screen="home">
      <h1 class="logo">Dino Ages<span class="sub">An expedition through time</span></h1>
      <div class="players">{players}</div>
      <div class="grown"><a href="/parent">Grown-ups</a></div></div>"""
    return page(body)


@app.route("/map/<who>")
@app.route("/map/<who>/<int:age>")
def age_map(who, age=1):
    require_profile(who)
    if age not in AGES:
        abort(404)
    done = mastered_topics(who)
    meta = AGE_META[age]
    def progress(m):
        tot = len(m["topics"]); d = sum(1 for t in m["topics"] if t["id"] in done)
        return d, tot
    nxt, best = None, 2.0
    for m in (m for m in meta if m["topics"]):
        d, tot = progress(m)
        if d < tot and d / tot < best:
            best, nxt = d / tot, m["key"]
    stations = []
    for i, m in enumerate(meta):
        x, y = SLOTS[i % len(SLOTS)]
        d, tot = progress(m)
        stations.append({"cre": m["key"], "name": m["name"], "subj": m["subject"],
                         "served": bool(m["topics"]), "done": d, "total": tot,
                         "x": x, "y": y, "next": m["key"] == nxt, "fig": CREATURE_FIG.get(m["key"])})
    stations.append({"cre": "fossil", "name": "Fossil Dig", "served": False, "done": 0, "total": 0,
                     "x": FOSSIL_SLOT[0], "y": FOSSIL_SLOT[1], "next": False, "fossil": True})
    prev_a = age - 1 if (age - 1) in AGES else None
    next_a = age + 1 if (age + 1) in AGES else None
    nav = ""
    if prev_a:
        nav += f'<a class="pill" href="/map/{who}/{prev_a}">◀ Age {prev_a}</a>'
    if next_a:
        nav += f'<a class="pill" href="/map/{who}/{next_a}">Age {next_a} ▶</a>'
    body = f"""<div class="content" data-screen="map" data-who="{who}" data-theme="{AGE_THEME[age]}" data-age="{age}">
      <div class="hud"><a class="pill" href="/">◀</a><h2>Age {age} · {AGE_NAME[age]}</h2>{nav}
        <a class="pill" href="{url_for('museum', who=who, age=age)}">🦴 Museum</a></div>
      <div class="stations" data-stations='{json.dumps(stations)}'></div></div>"""
    return page(body)


@app.route("/station/<who>/<creature>")
def station(who, creature):
    require_profile(who)
    m = KEY_META.get(creature)
    if m is None or not m["topics"]:
        abort(404)
    age = KEY_AGE[creature]
    body = f"""<div class="content station-stage" data-screen="station" data-who="{who}" data-theme="{AGE_THEME[age]}">
      <div class="hud"><a class="pill" href="{url_for('age_map', who=who, age=age)}">◀</a><h2>{m['name']}</h2></div>
      <main id="station" style="flex:1;display:flex;flex-direction:column;position:relative;z-index:3"
        data-who="{who}" data-name="{PROFILES[who][0]}" data-creature="{creature}" data-greet="{m['greet']}"
        data-age="{age}" data-fig='{json.dumps(CREATURE_FIG.get(creature) or {})}'
        data-topics='{json.dumps(m["topics"])}'></main></div>"""
    return page(body)


# ---- scaling-kit demo: a Jurassic theme + 3 template-built dinosaurs ----------
JURASSIC_DINOS = [
    {"id": "rella", "name": "Rella the Runner", "plan": "biped",
     "colors": {"main": "#e07a3c", "belly": "#f6dcae", "accent": "#a84e1e"},
     "size": 1.0, "horns": 1, "crest": True, "tail": "long",
     "blurb": "A quick two-legged hunter with a little head crest."},
    {"id": "nessa", "name": "Nessa the Longneck", "plan": "longneck",
     "colors": {"main": "#4aa6c4", "belly": "#dff1f6", "accent": "#2d6f8a"},
     "size": 1.0, "blurb": "Reaches the tallest leaves with her long neck."},
    {"id": "stego", "name": "Stego the Spiky", "plan": "armoured",
     "colors": {"main": "#7bbf4a", "belly": "#e7f3c6", "accent": "#4b7d2e"},
     "plates": True, "spikes": True, "horns": 1,
     "blurb": "Bony back plates and a spiky tail for defence."},
]


DEVONIAN_CREATURES = [
    {"id": "dunkle", "name": "Dunkle the Armoured", "plan": "swimmer",
     "colors": {"main": "#5a8f9a", "belly": "#dceef0", "accent": "#2d5f68"}, "size": 1.05,
     "blurb": "A giant armoured fish with bony jaws."},
    {"id": "hyn", "name": "Hyn the Hunter", "plan": "swimmer",
     "colors": {"main": "#7a9a4a", "belly": "#eaf3c6", "accent": "#4b6d2e"},
     "blurb": "A long lobe-finned fish that lurks in the deep."},
    {"id": "tik", "name": "Tik the First-Stepper", "plan": "quadruped",
     "colors": {"main": "#8a6a4a", "belly": "#efe0c0", "accent": "#5a4028"}, "horns": 0,
     "blurb": "Fins becoming legs — creeping onto land."},
    {"id": "ceph", "name": "Ceph the Shielded", "plan": "swimmer",
     "colors": {"main": "#9a7a5a", "belly": "#f0e4cc", "accent": "#6a4a2e"},
     "blurb": "A little fish with a head like a shield."},
    {"id": "steth", "name": "Steth the Early Shark", "plan": "swimmer",
     "colors": {"main": "#6a7a8a", "belly": "#e4ecf2", "accent": "#3a4a58"},
     "blurb": "An early shark with an anvil-shaped fin."},
    {"id": "both", "name": "Both the Box-Fish", "plan": "arthropod",
     "colors": {"main": "#8a8f5a", "belly": "#eef0c8", "accent": "#5a5f2e"},
     "blurb": "A boxy armoured fish that scoots along the floor."},
]

CARBONIFEROUS_CREATURES = [
    {"id": "mega", "name": "Mega the Dragonfly", "plan": "flyer",
     "colors": {"main": "#3f9a8a", "belly": "#ddf3ee", "accent": "#2a6f62"}, "crest": True,
     "blurb": "A dragonfly as wide as a hawk."},
    {"id": "arthro", "name": "Arthro the Long One", "plan": "arthropod",
     "colors": {"main": "#8a6a3a", "belly": "#efe0c0", "accent": "#5a4020"},
     "blurb": "A giant millipede longer than you."},
    {"id": "eryops", "name": "Eryops the Big-Mouth", "plan": "quadruped",
     "colors": {"main": "#6a8f5a", "belly": "#e7f0cc", "accent": "#41602e"}, "horns": 0,
     "blurb": "A chunky amphibian with a huge grin."},
    {"id": "hylo", "name": "Hylo the First-Reptile", "plan": "quadruped",
     "colors": {"main": "#8a7a4a", "belly": "#efe6c6", "accent": "#5a4a28"},
     "blurb": "One of the very first reptiles."},
    {"id": "pulmo", "name": "Pulmo the Scorpion", "plan": "arthropod",
     "colors": {"main": "#9a6a4a", "belly": "#f0dccb", "accent": "#6a3a28"},
     "blurb": "A land scorpion the size of a dog."},
    {"id": "prot", "name": "Prot the Swimmer", "plan": "swimmer",
     "colors": {"main": "#5a8a7a", "belly": "#dcefe8", "accent": "#376258"},
     "blurb": "An eel-like hunter of the swamp pools."},
]

KIT_AGES = {
    "jurassic": ("Jurassic", JURASSIC_DINOS),
    "devonian": ("Devonian (Age of Fishes)", DEVONIAN_CREATURES),
    "carboniferous": ("Carboniferous Swamps", CARBONIFEROUS_CREATURES),
}


@app.route("/kit")
def kit():
    age = request.args.get("age", "jurassic")
    if age not in KIT_AGES:
        age = "jurassic"
    title, roster = KIT_AGES[age]
    nav = " · ".join(
        (f'<a class="pill" href="/kit?age={a}">{n.split(" (")[0]}</a>') for a, (n, _) in KIT_AGES.items())
    body = f"""<div class="content kit-screen" data-screen="kit">
      <div class="hud"><a class="pill" href="/">◀</a><h2>Scaling Kit · {title}</h2></div>
      <div class="kitnav">{nav}</div>
      <div class="kit" data-theme="{age}" data-dinos='{json.dumps(roster)}'></div></div>"""
    return page(body)


@app.route("/art/manifest.json")
def art_manifest():
    base = ROOT / "assets" / "art"
    creatures = sorted(d.name for d in base.glob("*") if d.is_dir()
                       and d.name != "scenes" and (d / "rig.json").is_file())
    scenes = sorted(d.name for d in (base / "scenes").glob("*")
                    if d.is_dir() and (d / "scene.json").is_file()) if (base / "scenes").is_dir() else []
    return jsonify({"creatures": creatures, "scenes": scenes})


@app.route("/art/<path:p>")
def art(p):
    # serve drop-in creature/scene art from assets/art (local only); 404 -> code fallback
    base = ROOT / "assets" / "art"
    if not (base / p).is_file():
        abort(404)
    return send_from_directory(base, p)


@app.route("/lineup")
def lineup():
    # QA/review: all 6 Age-1 creatures at hero size, for the creature-quality gate
    cards = "".join(
        f'<figure class="lu"><div class="holder" style="width:220px;height:220px">'
        f'<div class="cr-slot" data-cre="{m["key"]}"></div></div>'
        f'<figcaption>{m["name"]}<small>{m["subject"]}</small></figcaption></figure>'
        for m in AGE1)
    body = f"""<div class="content" data-screen="lineup" style="position:relative;z-index:3">
      <div class="hud"><a class="pill" href="/map/child_a">◀</a><h2>Age 1 creatures</h2></div>
      <main style="flex:1;display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:22px;padding:20px;overflow:auto">
        {cards}</main></div>
      <style>.lu{{text-align:center;color:#fff}}.lu figcaption{{font-family:Fredoka;font-size:1.2rem;font-weight:600;
        text-shadow:0 2px 8px #0008}}.lu small{{display:block;opacity:.8;font-size:.9rem}}</style>"""
    return page(body)


@app.route("/api/lesson/<topic>")
def api_lesson(topic):
    for age in AGES:                                   # a topic's lesson lives in its age folder
        f = lessons_dir(age) / f"{topic}.md"
        if f.exists():
            return jsonify({"markdown": f.read_text()})
    return jsonify({"markdown": "## Learn\nComing soon."})


@app.route("/api/question")
def api_question():
    who, topic = request.args.get("who"), request.args.get("topic")
    level = int(request.args.get("level", 1))
    require_profile(who)
    seen = set(session.get("seen", []))
    if topic in NVR_BANK:                        # image-option NVR (verified, unique answer)
        pool = [it for it in NVR_BANK[topic] if it["id"] not in seen] or NVR_BANK[topic]
        it = random.choice(pool)
        seen.add(it["id"]); session["seen"] = list(seen)[-200:]
        return jsonify({"id": it["id"], "nvr": True, "prompt": it["prompt"],
                        "seq": it["seq"], "options": it["options"], "level": 2})
    q = pick_question(topic, level, seen)
    if q is None or not q.servable():           # serve gate on every question
        return jsonify({"error": "no_verified_content"}), 503
    seen.add(q.id)
    session["seen"] = list(seen)[-200:]
    return jsonify({"id": q.id, "stem": q.stem, "options": q.options, "level": q.level})


def _key_spec(key):
    """Canonical (value, domain) for a bank item's key, for the typed normaliser."""
    p = answer_norm.parse(key)
    if not p:
        return key, "word"                     # a word answer (spelling / plural)
    v, kind, _u = p
    return v, ("money" if kind == "money" else "proportion" if kind == "percent" else "number")


@app.route("/api/answer", methods=["POST"])
def api_answer():
    data = request.get_json(force=True)
    who, topic, qid = data["who"], data["topic"], data["qid"]
    require_profile(who)
    nvr = NVR_BY_ID.get(qid)
    if nvr is not None:                           # image-option NVR
        chosen = int(data["chosen"])
        correct = (chosen == nvr["answer_index"])
        if data.get("count", True):
            record_attempt(who, topic, correct)
        return jsonify({"correct": correct, "answer_index": nvr["answer_index"],
                        "explanation": nvr["explanation"],
                        "why_wrong": "" if correct else nvr["explanation"]})
    q = BY_ID.get(qid)
    if q is None:
        abort(400)
    key = q.options[q.answer_index]
    if "typed" in data:                               # typed-answer mode (written schools)
        val, domain = _key_spec(key)
        if domain == "word":                          # spelling / plural: case-insensitive exact word
            correct = str(data["typed"]).strip().lower() == str(key).strip().lower()
        else:
            correct = answer_norm.accepts(str(data["typed"]), val, domain)
        chosen = -1
    else:
        chosen = int(data["chosen"])
        correct = (chosen == q.answer_index)
    if data.get("count", True):
        record_attempt(who, topic, correct)
    ww = ""
    if not correct:
        if chosen < 0:                                          # typed answer
            ww = f"Not quite — the answer is {key}."
        else:
            de = getattr(q, "distractor_explanations", None) or []
            named = de[chosen] if 0 <= chosen < len(de) else None   # bank's named-slip reason (L3-5)
            if named:
                picked = q.options[chosen] if 0 <= chosen < len(q.options) else ""
                ww = f"{picked} — you {named}."
            else:
                ww = why_wrong(q, chosen)                       # stem-derived reason (L1-2)
    return jsonify({"correct": correct, "answer_index": q.answer_index, "key": key,
                    "explanation": q.explanation, "why_wrong": ww})


@app.route("/api/master", methods=["POST"])
def api_master():
    data = request.get_json(force=True)
    who, topic, creature = data["who"], data["topic"], data.get("creature")
    require_profile(who)
    st = record_session(who, topic)            # state from accumulated, cross-session performance
    done = mastered_topics(who)
    m = KEY_META.get(creature)
    card = creature if m and m["topics"] and all(t["id"] in done for t in m["topics"]) else None
    st.update({"card": card})
    return jsonify(st)


# time-on-task analytics for the parent dashboard (not part of the question
# engine, serve gate or mastery logic — just a usage counter).
@app.route("/api/tick", methods=["POST"])
def api_tick():
    data = request.get_json(force=True)
    who, topic = data.get("who"), data.get("topic")
    secs = max(0, min(60, int(data.get("seconds", 0))))        # clamp per call
    if who in PROFILES and topic and secs:
        d = db()
        d.execute("INSERT OR IGNORE INTO timespent(profile, topic) VALUES(?,?)", (who, topic))
        d.execute("UPDATE timespent SET seconds=seconds+? WHERE profile=? AND topic=?", (secs, who, topic))
        d.commit()
    return jsonify({"ok": True})


# ------------------------------ Fossil Dig -----------------------------------
FOSSILS = [
    {"id": "trilobite_cast", "name": "Trilobite cast",
     "fact": "A trilobite left its shape pressed into the mud, which hardened into rock over millions of years."},
    {"id": "ammonite", "name": "Ammonite",
     "fact": "Ammonites grew their spiral shells in chambers, adding a bigger room as they got older."},
    {"id": "brachiopod", "name": "Brachiopod",
     "fact": "Brachiopods look like clams but are a different animal — some kinds are still alive today."},
]


@app.route("/dig/<who>")
@app.route("/dig/<who>/<int:age>")
def dig(who, age=1):
    require_profile(who)
    if age not in AGES:
        abort(404)
    body = f"""<div class="content" data-screen="dig" data-who="{who}" data-theme="{AGE_THEME[age]}" data-age="{age}">
      <div class="hud"><a class="pill" href="{url_for('age_map', who=who, age=age)}">◀</a><h2>Fossil Dig</h2></div>
      <main id="dig" style="flex:1;display:flex;flex-direction:column;position:relative;z-index:3"
        data-who="{who}" data-age="{age}" data-fossils='{json.dumps(FOSSILS)}'></main></div>"""
    return page(body)


@app.route("/api/dig", methods=["POST"])
def api_dig():
    data = request.get_json(force=True)
    who, fossil = data.get("who"), data.get("fossil")
    if who in PROFILES and fossil:
        d = db()
        d.execute("INSERT OR IGNORE INTO fossils(profile, fossil) VALUES(?,?)", (who, fossil))
        d.commit()
    return jsonify({"ok": True})


# ------------------------------ Museum ---------------------------------------
@app.route("/museum/<who>")
@app.route("/museum/<who>/<int:age>")
def museum(who, age=1):
    require_profile(who)
    if age not in AGES:
        abort(404)
    done = mastered_topics(who)
    got = {r["creature"] for r in db().execute("SELECT creature FROM cards WHERE profile=?", (who,))}
    found = {r["fossil"] for r in db().execute("SELECT fossil FROM fossils WHERE profile=?", (who,))}
    items = []
    for m in AGE_META[age]:
        if not m["topics"]:
            continue
        c = fact_for(m["key"])
        items.append({"key": m["key"], "name": m["name"], "subject": m["subject"],
                      "earned": m["key"] in got, "fact": c["fact_card"]["fact"],
                      "done": sum(1 for t in m["topics"] if t["id"] in done),
                      "total": len(m["topics"]), "fig": CREATURE_FIG.get(m["key"])})
    fossils = [{"id": f["id"], "name": f["name"], "fact": f["fact"], "found": f["id"] in found}
               for f in FOSSILS]
    body = f"""<div class="content museum-screen" data-screen="museum" data-who="{who}" data-theme="{AGE_THEME[age]}" data-age="{age}">
      <div class="hud"><a class="pill" href="{url_for('age_map', who=who, age=age)}">◀</a>
        <h2>🦴 Fossil Museum · Age {age}</h2></div>
      <div class="hall" data-items='{json.dumps(items)}' data-fossils='{json.dumps(fossils)}'></div></div>"""
    return page(body)


def _fmt_secs(s):
    s = int(s or 0)
    return f"{s // 60}m {s % 60:02d}s" if s >= 60 else f"{s}s"


def _get_pin():
    r = db().execute("SELECT v FROM setting WHERE k='pin'").fetchone()
    return r["v"] if r else None


# heatmap cell class per state (colours defined in ui.css, kept in sync with mastery.STATE_COLOUR)
STATE_CLASS = {"Not started": "st-none", "Learning": "st-learning", "Developing": "st-developing",
               "Secure": "st-secure", "Strong": "st-strong", "Mastered": "st-mastered"}


@app.route("/parent", methods=["GET", "POST"])
def parent():
    pin = _get_pin()
    if request.method == "POST":
        entered = (request.form.get("pin", "") or "").strip()
        if pin is None:                                   # first use: the parent SETS their own PIN
            if not (entered.isdigit() and 4 <= len(entered) <= 8):
                return _parent_gate(setting=True, msg="Pick a 4–8 digit PIN.")
            db().execute("INSERT OR REPLACE INTO setting(k,v) VALUES('pin',?)", (entered,))
            db().commit()
            session["parent_ok"] = True
        elif entered == pin:
            session["parent_ok"] = True
        else:
            return _parent_gate(msg="That PIN did not match — try again.")
        return redirect("/parent")
    if pin is None:
        return _parent_gate(setting=True)
    if not session.get("parent_ok"):
        return _parent_gate()

    sections = ""
    for who, (name, col) in PROFILES.items():
        tspent = {r["topic"]: r["seconds"] for r in
                  db().execute("SELECT topic, seconds FROM timespent WHERE profile=?", (who,))}
        total_secs, mastered_n, topic_n, weak = 0, 0, 0, []
        cells = ""
        for age in AGES:
            age_cells = ""
            for m in AGE_META[age]:
                for t in m["topics"]:
                    topic_n += 1
                    att, cor, ses = topic_stats(who, t["id"])
                    secs = tspent.get(t["id"], 0); total_secs += secs
                    state = mastery.mastery_state(att, cor, ses)
                    if state == "Mastered":
                        mastered_n += 1
                    label = state if att == 0 or state == "Not started" else f"{state} · {round(mastery.pct(cor, att))}%"
                    if att and state in ("Learning", "Developing"):
                        weak.append((t["title"], m["name"], round(mastery.pct(cor, att)), att))
                    age_cells += (f'<div class="cell {STATE_CLASS[state]}" title="{t["title"]} · {m["name"]} · '
                                  f'{cor}/{att} correct · {ses} sessions · {_fmt_secs(secs)}">'
                                  f'<span class="ct">{t["title"]}</span><span class="cv">{label}</span></div>')
            if age_cells:
                cells += (f'<div class="agehead">Age {age} · {AGE_NAME[age]}</div>'
                          f'<div class="heatmap">{age_cells}</div>')
        weak.sort(key=lambda x: x[2])
        weak_html = ("".join(f'<li><b>{w[0]}</b> <span>({w[1]} · {w[2]}% over {w[3]})</span></li>'
                             for w in weak[:4])
                     or '<li class="none">No weak spots yet.</li>')
        sections += (
            f'<section class="pcard"><div class="phead"><span class="pdot" style="background:{col}"></span>'
            f'<h3>{name}</h3><div class="pstats"><span>🏆 {mastered_n}/{topic_n} mastered</span>'
            f'<span>⏱ {_fmt_secs(total_secs)} on task</span></div></div>'
            f'{cells}'
            f'<div class="weak"><h4>Needs practice</h4><ul>{weak_html}</ul></div></section>')

    legend = "".join(
        f'<span class="lg {STATE_CLASS[s]}">{s}</span>' for s in mastery.STATES)
    body = (f'<div class="content parent-screen" data-screen="parent">'
            f'<div class="hud"><a class="pill" href="/">◀</a><h2>Grown-ups dashboard</h2>'
            f'<a class="pill" href="/parent/reset" onclick="return confirm(\'Change the PIN? You will set a new one.\')">Change PIN</a></div>'
            f'<main class="parent">'
            f'<p class="note">Age 1 serves foundation (levels 1–2) content only; every question shown '
            f'has passed the automated verification gate. <b>Mastered</b> needs 90%+ across several '
            f'sessions on unseen questions — never from one session.</p>'
            f'<div class="legend">{legend}</div>'
            f'{sections}'
            f'<section class="pcard backup"><h3>Backup &amp; restore</h3>'
            f'<p class="note">Progress is stored only on this computer. Download a copy to keep it safe, '
            f'or restore from a file (this replaces current progress).</p>'
            f'<div class="backup-row"><a class="btn teal" href="/parent/backup">⬇ Download progress</a>'
            f'<form method="post" action="/parent/restore" enctype="multipart/form-data">'
            f'<input type="file" name="backup" accept="application/json" required>'
            f'<button class="btn">⬆ Restore</button></form></div></section>'
            f'</main></div>')
    return page(body)


@app.route("/parent/reset")
def parent_reset():
    if not session.get("parent_ok"):
        abort(403)
    db().execute("DELETE FROM setting WHERE k='pin'")
    db().commit()
    session["parent_ok"] = False
    return redirect("/parent")


# whitelisted progress tables/columns for backup + restore (no PIN exported)
BACKUP_COLS = {"mastery": ["profile", "topic", "mastered", "attempts", "correct", "sessions"],
               "cards": ["profile", "creature"], "timespent": ["profile", "topic", "seconds"],
               "fossils": ["profile", "fossil"]}


@app.route("/parent/backup")
def parent_backup():
    if not session.get("parent_ok"):
        abort(403)
    d = db()
    data = {"app": "dino-ages", "version": 1, "tables": {}}
    for tbl, cols in BACKUP_COLS.items():
        data["tables"][tbl] = [dict(r) for r in d.execute(f"SELECT {','.join(cols)} FROM {tbl}")]
    resp = app.response_class(json.dumps(data, indent=1), mimetype="application/json")
    resp.headers["Content-Disposition"] = "attachment; filename=dino-ages-progress.json"
    return resp


@app.route("/parent/restore", methods=["POST"])
def parent_restore():
    if not session.get("parent_ok"):
        abort(403)
    f = request.files.get("backup")
    try:
        data = json.load(f.stream)
        assert data.get("app") == "dino-ages"
    except Exception:
        return _parent_gate(msg="That backup file could not be read.")
    d = db()
    for tbl, cols in BACKUP_COLS.items():
        rows = data.get("tables", {}).get(tbl, [])
        d.execute(f"DELETE FROM {tbl}")
        for r in rows:                                   # only whitelisted columns are used
            vals = [r.get(c) for c in cols]
            d.execute(f"INSERT INTO {tbl}({','.join(cols)}) VALUES({','.join('?' * len(cols))})", vals)
    d.commit()
    return redirect("/parent")


def _parent_gate(msg="", setting=False):
    err = f'<p class="gate-err">{msg}</p>' if msg else ""
    title = "Create a PIN" if setting else "Enter your PIN"
    sub = ("Choose a 4–8 digit PIN for the grown-ups area." if setting
           else "Enter the PIN you chose.")
    btn = "Set PIN" if setting else "Enter"
    body = (f'<div class="content parent-screen" data-screen="parent">'
            f'<main class="parent gate"><div class="gatecard">'
            f'<h2>🔒 {title}</h2><p>{sub}</p>{err}'
            f'<form method="post"><input name="pin" inputmode="numeric" pattern="[0-9]*" '
            f'maxlength="8" autofocus autocomplete="off"> <button class="btn teal">{btn}</button></form>'
            f'<p><a class="back" href="/">◀ Back to Dino Ages</a></p></div></main></div>')
    return page(body)


def _lan_ip():
    """Best-effort local Wi-Fi address. Uses a disconnected UDP socket (no packet
    is actually sent), so there is no network egress."""
    import socket as _s
    try:
        s = _s.socket(_s.AF_INET, _s.SOCK_DGRAM)
        s.connect(("192.168.1.1", 1))          # just sets a default route; sends nothing
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    init_db()
    argv = sys.argv
    port = int(argv[argv.index("--port") + 1]) if "--port" in argv else 5000
    lan = "--lan" in argv
    host = "0.0.0.0" if lan else "127.0.0.1"   # default stays localhost-only
    if lan:
        ip = _lan_ip()
        print("\n  Dino Ages — home Wi-Fi mode (reachable from your tablet, not the internet):")
        print(f"      On this Mac:     http://127.0.0.1:{port}/")
        print(f"      On the tablet:   http://{ip}:{port}/   (same Wi-Fi network)")
        print("  First run, macOS may ask 'Do you want the application python to accept")
        print("  incoming network connections?' — click Allow. To lock it down again,")
        print("  just stop this (Ctrl-C) or run without --lan.\n")
    app.run(host=host, port=port, debug=False)
