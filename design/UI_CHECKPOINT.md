# Checkpoint 4 (checkpoint4 branch)

Everything after the approved Checkpoint 3. `make test` green (**78**). Self-hosted
only, no runtime network. Sections 0–3 below; **honest weak-list at the end**.

Branches: Section 0 (Checkpoint 3 + section-1 fixes) is **committed and merged to
`main`**. Sections 2–3 are on **`checkpoint4`** (unmerged, for your review).

---

## 0. Commit & merge — done
- `6078fb3` on `ui-overhaul` (Checkpoint 3 + section-1 fixes), merged `68b2c3e`
  into `main` with `make test` green (72 at the time). **Not pushed.**
- Sections 2–3 continued on `checkpoint4` so `main` stays at the approved state
  until you review.

## 1. Quick UI fixes — all done (verified in v3 shots)
- **Mastery states.** New shared model `platform/mastery.py`: *Not started /
  Learning (<60) / Developing (60–74) / Secure (75–84) / Strong (85–89) /
  Mastered*. **Mastered needs 90%+ across ≥2 sessions on ≥10 unseen items — never
  one session** (`tests/test_mastery_state.py`, 5 tests; verified: one perfect
  session = "Strong", a second = "Mastered"). Parent heatmap + legend, map rings
  and the finish state-pill all use it (`v3_parent_1024x768`: "Rounding ·
  Mastered · 100%", "Division facts · Secure · 83%"; `v3_finish_1024x768`: session
  stars separate from the "Mastered · 90%" pill).
- **Explanations.** The wrong-answer box now shows **one** clear reason
  (`v3_practise_wrong_390x844`).
- **Phone Home.** The blocking "Sound on?" prompt is gone; audio starts on the
  first tap; toasts are non-blocking (`v3_home_390x844`).
- **Fossil Dig.** `user-select:none` + `touch-action:none` while brushing; "See
  the Museum" is a real button and the ⚙ is clear (`v3_dig_found_390x844`).
- **Parent PIN.** No default shipped — the grown-up **sets their own PIN on first
  use** ("Create a PIN"), with a "Change PIN" link.
- **Trail.** One continuous journey per session; **milestones == questions**
  (SESSION_N = 6); the buddy steps each question (`v3_practise_390x844`).
- **Home-Wi-Fi mode.** `python platform/age1_app.py --lan` serves to a tablet on
  the same Wi-Fi (prints the `http://192.168.x.x:5000/` address + the macOS
  "Allow incoming connections" note). Default stays localhost (`HOW_TO_RUN.md`).

## 2. Reusable scaling kit — done (demonstrated, Jurassic)
- **Theme system** (`themes.js`): each age is **data** — palette, sky,
  declarative parallax layers, ambient particles, swimmers/flyers, sounds.
  `scene.buildTheme(theme)` + `scene.themeParticles()` render any theme from
  config (layer primitives: spires/rays/haze/reef/caustics/floor/foreground;
  flora = kelp **or** ferns; ambient = bubbles **or** pollen; swimmers = fish
  **or** flyers). Cambrian + Jurassic defined.
- **Creature template system** (`creature_templates.js`): parametric,
  rig-compatible body plans — **biped, longneck, armoured, quadruped, flyer,
  swimmer, arthropod, mammal** — with colour/size/horns/plates/spikes/crest/tail/
  face params. A new creature is a config entry; a generated hero image still
  overrides via `assets/art/<id>/`.
- **Demo:** `/kit` renders a Jurassic theme with **3 template dinosaurs** (biped
  Rella, longneck Nessa, armoured Stego). Screenshots:
  `v3_kit_jurassic_390x844`, `_768x1024`, `_1440x900` (0 console errors).

## 3. Content & mastery (engine) — mastery done; expansion partial
- **Mastery logic** in the engine + DB (`sessions` column, cross-session rule),
  with tests (see §1). Backup-safe.
- **Topic expansion: 4 → 8 verified topics.** Four new computable Age-1 Maths
  topics, each a **generator + an INDEPENDENT solver** the registry cross-checks:
  **MA-A03** compare/order, **MA-B13** odd/even/multiples, **MA-A07** Roman
  numerals, **MA-B06** missing numbers (inverse ops). Each: **150 verified items
  per level (L1 + L2)**, a **Year 4–5 lesson**, and **per-option wrong-answer
  reasons**. Served set is now Trilobite ×4, Anomalocaris ×3, Pikaia ×1.
- **Golden known-answer tests** (`tests/test_golden_answers.py`, 6): fixed cases
  checked by the independent solver + a re-verification sweep of every served
  Maths bank.
- **Content report** (`scripts/content_report.py` → `content/age1/content_report.md`):
  **8 topics, 2250 verified questions** (Maths 2100, VR 150), with the
  verification evidence per topic.
- **Backup & restore** on the Parent dashboard (`/parent/backup` download,
  `/parent/restore` upload; whitelisted tables/columns; the PIN is **not**
  exported). Smoke-tested round-trip.
- **Language rule respected:** English and word-meaning VR topics are
  **intentionally not served** — the blind-solve + adversarial pipeline is not
  built yet.

## QA
`design/VISUAL_QA.md`: **68 captures across 4 sizes, 0 flags** (0 console / 0
overflow / 0 sub-44px), **61 fps** under 4× CPU throttle, plus the Jurassic kit at
three sizes and a full flow video.

---

## Honest list of what is still weak / not done
1. **Topic count: 8 of ~15.** I reached 8 fully-verified Age-1 topics, not 15.
   The registry has ~16 more computable generators, but they are mapped to
   **later-age creatures** (age 2–9) — serving them in Age 1 would mean building
   other ages, which you asked me not to do. The remaining *Age-1* computable
   topics (more Maths for Trilobite/Anomalocaris, VR-C01 alphabet positions, and
   Wiwaxia's NVR) still need generators.
2. **Levels 3–5 not built for Age 1.** Served content is **L1–L2 foundation**.
   The level-3 Maths generators exist but belong to later ages; multi-step 11+
   (levels 3–5) for Age-1 topics is **not** done.
3. **NVR for Wiwaxia (next-figure, shading, odd-one-out) is image-based** and has
   no generator yet — needs an SVG renderer + an independent visual solver (the
   existing NVR engine covers cube nets/rotation, which are later-age topics).
4. **Language blind-solve / adversarial pipeline not built**, so Opabinia and
   Hallucigenia (English) and the word-meaning VR topics stay dark. This is the
   biggest content gap and the right next investment for English.
5. **Per-option explanations are UI-layer**, derived from the stem, for the
   computable qtypes — not yet stored in the bank's `distractor_explanations`.
6. **Creature templates:** 3 plans (biped/longneck/armoured) are refined; the
   other 5 are basic parametric drafts. The Age-1 scene still uses its hand path
   (`cambrian()`); switching it onto `buildTheme` is a ~1-line change I left out
   to avoid any regression on the approved build.

**STOP — Checkpoint 4. Awaiting your review.** I have not built any other age.
Suggested next steps for your steer: (a) more Age-1 computable topics + levels
3–5; (b) the NVR image generator for Wiwaxia; (c) the English blind-solve/
adversarial pipeline; (d) migrate Age-1's scene onto the theme engine.
