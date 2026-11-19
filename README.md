# Little Dino 11+ Prep

**Free, open, offline 11+ practice — so every child gets a fair shot, whatever their family can afford.**

Private 11+ tutoring and subscription practice platforms cost hundreds of pounds a
term, which quietly tilts selective-school admissions toward families who can pay.
Little Dino is a small attempt to level that playing field: a **free** practice
platform powered by an engine that generates **unlimited, original, code‑verified**
11+ questions — no subscription, no copyrighted past papers, no internet required.

> **Why "code‑verified" matters.** The hard part of auto‑generating practice questions
> isn't making them — it's trusting the answer key. Here, for Maths / Verbal Reasoning /
> Non‑Verbal Reasoning the computer **computes the answer in code** (it never "recalls"
> it), and a **separate checker re‑derives every answer by a different method**. Only
> questions that pass this gate are ever shown to a child. The whole repo is built around
> that verification discipline — see [Verification](#how-the-verification-works).

---

## What it does

- **Generates original 11+ questions** in Maths, Verbal Reasoning, English (SPaG) and
  Non‑Verbal Reasoning, calibrated to the difficulty of real 11+ papers.
- **Verifies every one** before serving it (dual‑method cross‑checks + a serve gate).
- **Serves them through a friendly platform** ("Dino Ages") with per‑child progress, a
  mastery model, lessons, and a PIN‑protected grown‑ups dashboard.
- **Runs entirely offline.** No network calls at runtime; fonts, styles, scripts and art
  are all vendored locally. Original art only.

## Quick start

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python platform/age1_app.py          # → http://127.0.0.1:5000
```

Open the address, pick a profile, tap a creature on the map, and go
**Meet → Learn → Practise → Finish**. Run `make test` to see the whole verification
suite pass.

## How the verification works

| Subject | How the answer is trusted |
|---|---|
| **Maths** | Answer computed in code; harder multi‑step items get a **second, different‑method** cross‑check (reverse‑derivation / a separate evaluator / forward simulation) via `scripts/verify2.py`, plus golden known‑answer tests. |
| **Verbal Reasoning** | Each rule type is re‑solved by independent code. |
| **English (SPaG)** | Objective types (homophones, plurals, apostrophes, affixes, spelling, agreement, punctuation…) each checked against an independent vetted list; genuinely ambiguous items (UK/US spellings, two‑form plurals, collective‑noun agreement) are detected and excluded. |
| **Non‑Verbal Reasoning** | Computable 2D items with a **uniqueness/ambiguity rejection proof** — an item is only served if exactly one option is correct. |

Nothing reaches a child unless it passes the **serve gate** (`scripts/qschema.py` →
`Question.servable()`), which is re‑checked again at serve time. The test suite
(`make test`, **167 tests**) enforces the gate and layers on metamorphic tests,
**planted‑bug mutation** tests (deliberately break a generator and prove the checker
catches it), and golden known‑answer cases.

## Honest capability & ceiling

Calibrated honesty is a feature here, not an afterthought:

- **Reliable, verified, calibrated:** Maths, Verbal Reasoning, English SPaG/vocabulary,
  and NVR series / odd‑one‑out. Generate as many as you like — each is auto‑checked, so
  quality holds at scale.
- **Deliberately *not* auto‑generated:** reading comprehension, creative writing, the
  hardest super‑selective problem‑solving, and heavy 3D NVR (hidden‑cube counting,
  paper‑folding). These need human authoring or can't be verified cheaply, so the tool
  doesn't pretend to cover them.
- Generated questions are **solid standard 11+ level, calibrated to real papers** — not
  "guaranteed perfect," and not a stand‑in for a super‑selective's very hardest items.

> Difficulty was calibrated by measuring real 11+ papers (number‑size and vocabulary
> profiles); the measurement scripts that read those copyrighted papers are **not**
> included here — only the resulting targets, which are baked into the generators.

## Repository map

```
scripts/      the generation + verification engine
  maths_gen.py · vr_gen.py · english_rulegen.py · nvr_svg.py / nvr_3d.py   # generators
  verify2.py · qschema.py · testers.py · answer_norm.py                    # verification + serve gate
  train_all.py                                                             # all generators + testers, in parallel
platform/     the "Dino Ages" Flask app (offline), mastery model, vendored fonts
content/      served-topic manifests, lessons, generated question banks, topic taxonomy
tests/        the full verification suite  (make test → 167 passing)
reports/      audit exports, harness results, mutation/catch-rate evidence
assets/ design/  original creature art + art direction & font licences
```

## Status & roadmap

Playable today: **Ages 1–3** (Cambrian / Devonian / Carboniferous) across Maths, VR,
English SPaG and NVR. The engine is the durable part; more ages, topics and an English
comprehension track (human‑authored, blind‑solver‑checked) are planned.

## Privacy

No child's data ever leaves the device: progress is a local SQLite file, and there are
no analytics or network calls at runtime. Nothing is sent to any third‑party service.

## Contributing & licence

This is built to be **given away**. If you'd like to add topics, improve calibration, or
help with a comprehension track, contributions are welcome. A licence file will be added;
the intent is a permissive open‑source licence so schools, charities and families can use
and adapt it freely. Fonts are vendored under their open licences (see `design/LICENSES.md`).

*Built with the help of [Claude Code](https://claude.com/claude-code).*
