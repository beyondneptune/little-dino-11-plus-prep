# Little Dino 11+ Prep — project instructions

A **free, open, offline** 11+ practice tool. An engine generates **original,
code‑verified** 11+ questions (Maths, Verbal Reasoning, English SPaG, Non‑Verbal
Reasoning) and a small Flask platform ("Dino Ages") serves them to children with
progress tracking. The goal is a level playing field: unlimited quality practice
with no subscription and no copyrighted content.

## Invariants (do not break)

- **Verification first.** Nothing reaches a child unless it passes the serve gate
  (`scripts/qschema.py` → `Question.servable()`). For Maths/VR/NVR the answer is
  **computed in code** and re‑derived by a **different method** (`scripts/verify2.py`);
  English objective types are checked against independent vetted lists. Keep
  `make test` green at all times.
- **Original content only.** No copyrighted past‑paper text, questions, or images.
  All art is original; fonts are vendored under their open licences.
- **Offline at runtime.** The platform makes **no network requests** when running —
  fonts, CSS, JS and art are all local.
- **Privacy.** No child's data leaves the device; progress is a local SQLite file.
  Never add analytics or third‑party calls, and never commit real names or results.
- **Honest scope.** Don't overclaim. Reading comprehension, creative writing, and
  heavy 3D NVR are intentionally out of the auto‑generated set — see the README's
  "Honest capability & ceiling".

## Layout

```
scripts/    generators (maths_gen, vr_gen, english_rulegen, nvr_svg/nvr_3d) +
            verification (verify2, qschema, testers, answer_norm) + train_all.py
platform/   the Dino Ages Flask app, mastery model, vendored fonts
content/    served-topic manifests, lessons, generated banks, topic taxonomy
tests/      the full verification suite  (make test)
reports/    audit exports + harness / mutation / catch-rate evidence
```

## Run

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python platform/age1_app.py     # http://127.0.0.1:5000
make test                                  # verification suite
```
