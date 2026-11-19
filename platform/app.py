#!/usr/bin/env python3
"""
11+ practice platform — MVP.

A local web app that serves ORIGINAL, code-verified questions from the project's
generators (Maths / VR / English / NVR), marks them instantly, shows the worked
explanation, and tracks per-topic mastery (the "ages" progress idea). Progress
is stored in a local SQLite file. Every question shown is original and generated;
it drills unlimited auto-checked questions on screen.

Run:  .venv/bin/python platform/app.py    then open http://127.0.0.1:5000
"""
import datetime
import json
import random
import shutil
import sqlite3
import sys
import uuid
from pathlib import Path

from flask import Flask, g, redirect, render_template_string, request, session, url_for

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import maths_gen                     # noqa: E402
import vr_gen                        # noqa: E402
import english_gen                   # noqa: E402
import nvr_3d as NVR                 # noqa: E402
from testers import (check_maths_item, check_vr_item,   # noqa: E402
                     check_nvr_item, check_english_item)

STATIC = Path(__file__).resolve().parent / "static"
STATIC.mkdir(exist_ok=True)
DB = Path(__file__).resolve().parent / "progress.db"
REJECT_LOG = Path(__file__).resolve().parent / "rejected.log"
BACKUPS = Path(__file__).resolve().parent / "backups"


def backup_db():
    """Keep a dated copy of the progress database (one per day). Never lose a
    child's progress. Runs on startup and after each answer; cheap when today's
    backup already exists."""
    try:
        if not DB.exists():
            return
        BACKUPS.mkdir(exist_ok=True)
        dst = BACKUPS / f"progress-{datetime.date.today().isoformat()}.db"
        if not dst.exists():
            shutil.copy2(DB, dst)
    except Exception:
        pass

# A question may ONLY be served if its matching tester passes it (section 2 of
# the brief: nothing unverified reaches a child). Failures are logged, never shown.
CHECKERS = {"maths": lambda it: check_maths_item(it)[0], "vr": check_vr_item,
            "english": check_english_item, "nvr": check_nvr_item}

app = Flask(__name__, static_folder=str(STATIC))
app.secret_key = "local-11plus-mvp"
SUBJECTS = {"maths": "Maths", "vr": "Verbal Reasoning", "english": "English", "nvr": "Non-Verbal Reasoning"}


# ---------------- database ----------------
def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def _close(_):
    if (d := g.pop("db", None)):
        d.close()


def init_db():
    c = sqlite3.connect(DB)
    c.executescript("""
        CREATE TABLE IF NOT EXISTS attempts(
            id INTEGER PRIMARY KEY, student TEXT, subject TEXT, topic TEXT,
            correct INTEGER, ts DATETIME DEFAULT CURRENT_TIMESTAMP);
    """)
    c.commit(); c.close()
    backup_db()


# ---------------- question source (gated: nothing unverified is served) ----------------
def _candidate(subject, rng):
    """Build a raw candidate INCLUDING the data its tester needs (_check)."""
    if subject == "maths":
        topic, q, ans, wrongs, expl = rng.choice(maths_gen.GENS)(rng)
        opts, idx = maths_gen.mcq(ans, wrongs, rng)
        return {"subject": subject, "topic": topic, "question": q, "options": opts,
                "answer": chr(65 + idx), "explanation": expl, "image": None}
    if subject in ("vr", "english"):
        mod = vr_gen if subject == "vr" else english_gen
        it = mod.generate(1, seed=rng.randint(0, 10 ** 9))[0]
        it.update(subject=subject, topic=it["type"], image=None)
        return it
    # nvr: build the structured net question (cheap); only render if it passes
    name = rng.choice([x for x in NVR.NETS if NVR.fold_face_ids(NVR.NETS[x])])
    syms, opts, idx = NVR.make_net_question(NVR.NETS[name], rng.randint(0, 10 ** 9))
    return {"subject": subject, "topic": "cube_net", "question": None, "image": None,
            "options": ["A", "B", "C", "D"], "answer": chr(65 + idx),
            "explanation": "On a cube, opposite faces can never meet at a corner.",
            "_check": {"kind": "cube_net", "cells": NVR.NETS[name], "syms": syms,
                       "opts": opts, "idx": idx}, "_render": (name, syms, opts, idx)}


def _log_reject(subject, cand, reason):
    with REJECT_LOG.open("a") as f:
        f.write(json.dumps({"subject": subject, "reason": reason,
                            "topic": cand.get("topic"), "question": cand.get("question"),
                            "options": cand.get("options"), "answer": cand.get("answer")}) + "\n")


def make_question(subject):
    """Return a question ONLY if its tester passes it; else None (never a bad one)."""
    rng = random.Random()
    for _ in range(50):
        try:
            cand = _candidate(subject, rng)
        except Exception as e:                       # e.g. generator could not build options
            _log_reject(subject, {}, f"generator error: {e}")
            continue
        try:
            passed = bool(CHECKERS[subject](cand))
        except Exception as e:
            passed = False; reason = f"tester error: {e}"
        else:
            reason = "tester rejected"
        if not passed:
            _log_reject(subject, cand, reason)
            continue
        if subject == "nvr":                         # only render verified NVR items
            name, syms, opts, idx = cand.pop("_render")
            fn = f"q_{uuid.uuid4().hex[:10]}.png"
            NVR.render("Which cube folds from the net?", opts, idx, STATIC / fn, NVR.NETS[name], syms)
            cand["image"] = fn
        cand.pop("_check", None); cand.pop("_render", None)
        return cand
    return None                                      # all attempts failed verification


# ---------------- templates ----------------
BASE = """
<!doctype html><title>11+ Practice</title>
<style>
 body{font-family:system-ui,Arial;max-width:760px;margin:24px auto;padding:0 16px;color:#1f2937}
 .card{border:1px solid #e5e7eb;border-radius:12px;padding:20px;margin:16px 0;box-shadow:0 1px 3px #0001}
 a.btn,button{display:inline-block;background:#4f46e5;color:#fff;border:0;border-radius:8px;
   padding:10px 16px;margin:4px;font-size:16px;cursor:pointer;text-decoration:none}
 a.sub{background:#eef2ff;color:#3730a3}
 .opt{display:block;width:100%;text-align:left;background:#f8fafc;color:#111;border:1px solid #cbd5e1;margin:6px 0}
 .right{color:#166534;font-weight:700}.wrong{color:#b91c1c;font-weight:700}
 .bar{background:#eef2ff;border-radius:6px;height:14px}.fill{background:#4f46e5;height:14px;border-radius:6px}
 small{color:#6b7280}
</style>
<h2>🎓 11+ Practice — {{ who }}</h2>
{{ body|safe }}
<p><a href="{{ url_for('home') }}">Home</a> ·
   <a href="{{ url_for('progress') }}">My progress</a></p>
"""


def _reject_banner():
    """A rejection means a possible NEW bug — make it loudly visible, not just logged."""
    try:
        n = sum(1 for _ in REJECT_LOG.open()) if REJECT_LOG.exists() else 0
    except Exception:
        n = 0
    if not n:
        return ""
    return ('<div style="background:#fef2f2;border:2px solid #b91c1c;color:#991b1b;'
            'padding:12px;border-radius:8px;margin:10px 0;font-weight:600">'
            f'⚠️ {n} question(s) were rejected by the quality gate. A rejection means a '
            'possible NEW bug — please tell the developer (details in rejected.log).</div>')


def page(body):
    return render_template_string(BASE, body=_reject_banner() + body,
                                  who=session.get("student", "guest"))


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        session["student"] = (request.form.get("name") or "guest").strip()[:30]
        return redirect(url_for("home"))
    subs = "".join(f'<a class="btn sub" href="{url_for("quiz", subject=s)}">{n}</a> '
                   for s, n in SUBJECTS.items())
    body = f"""
    <div class="card"><form method="post">Who's practising?
      <input name="name" value="{session.get('student','')}" placeholder="name">
      <button>Set</button></form></div>
    <div class="card"><b>Choose a subject to drill:</b><br><br>{subs}</div>
    <p><small>Original, auto-checked questions — generated and verified in code.</small></p>"""
    return page(body)


@app.route("/quiz/<subject>")
def quiz(subject):
    if subject not in SUBJECTS:
        return redirect(url_for("home"))
    q = make_question(subject)
    if q is None:                       # nothing passed verification — never show a bad one
        return page('<div class="card">Hmm, we couldn\'t prepare a verified question just now. '
                    'Please try again or pick another subject.</div>')
    session["q"] = {k: q[k] for k in ("subject", "topic", "answer", "explanation")}
    stem = f'<p style="font-size:18px">{q["question"]}</p>' if q["question"] else \
           f'<img src="/static/{q["image"]}" style="max-width:100%">'
    opts = "".join(
        f'<form method="post" action="{url_for("answer")}">'
        f'<input type="hidden" name="choice" value="{chr(65+i)}">'
        f'<button class="opt">{chr(65+i)}. {o}</button></form>'
        for i, o in enumerate(q["options"]))
    return page(f'<div class="card"><small>{SUBJECTS[subject]} · {q["topic"]}</small>{stem}{opts}</div>')


@app.route("/answer", methods=["POST"])
def answer():
    q = session.get("q")
    if not q:
        return redirect(url_for("home"))
    choice = request.form.get("choice")
    correct = choice == q["answer"]
    d = db()
    d.execute("INSERT INTO attempts(student,subject,topic,correct) VALUES(?,?,?,?)",
              (session.get("student", "guest"), q["subject"], q["topic"], int(correct)))
    d.commit()
    backup_db()
    verdict = ('<span class="right">✓ Correct!</span>' if correct
               else f'<span class="wrong">✗ Not quite — the answer was {q["answer"]}.</span>')
    body = f"""<div class="card"><p style="font-size:18px">{verdict}</p>
      <p><b>Why:</b> {q["explanation"]}</p>
      <a class="btn" href="{url_for('quiz', subject=q['subject'])}">Next question →</a>
      <a class="btn sub" href="{url_for('progress')}">See progress</a></div>"""
    return page(body)


@app.route("/progress")
def progress():
    rows = db().execute(
        "SELECT subject,topic,COUNT(*) seen,SUM(correct) ok FROM attempts "
        "WHERE student=? GROUP BY subject,topic ORDER BY subject,topic",
        (session.get("student", "guest"),)).fetchall()
    if not rows:
        return page('<div class="card">No practice yet — pick a subject from Home.</div>')
    html, cur = "", None
    for r in rows:
        if r["subject"] != cur:
            cur = r["subject"]; html += f'<h3>{SUBJECTS.get(cur,cur)}</h3>'
        pct = round(100 * (r["ok"] or 0) / r["seen"])
        html += (f'<div style="margin:8px 0">{r["topic"]} '
                 f'<small>({r["ok"] or 0}/{r["seen"]})</small>'
                 f'<div class="bar"><div class="fill" style="width:{pct}%"></div></div></div>')
    return page(f'<div class="card">{html}</div>')


if __name__ == "__main__":
    init_db()
    app.run(debug=False, port=5000)
