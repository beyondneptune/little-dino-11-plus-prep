# DECISIONS — autonomous mode

Every assumption/decision with its reason. Append-only; newest at the bottom.

## Autonomous-mode defaults adopted (from AUTONOMOUS_PROMPT.md section 2), 2026-11-14

- **D1 — Preview status: APPROVED, implement it.** Topics above a child's school
  level that sit in Ages 1-3 are tagged `preview: true`: introduced gently,
  tracked as "previewed", do NOT require mastery before the next age opens, and
  must be mastered by their spiral return visit. *Reason:* the prompt sets this
  default; it resolves the Phase-1 finding (28 above-level topics in Ages 1-3)
  without forcing early mastery or leaving gaps.
- **D2 — Thinly-sourced creatures (Pulmonoscorpius, Petrolacosaurus,
  Pholiderpeton): KEPT under the fallback clause.** The prompt says replace with
  a same-age creature having two good independent sources "if one exists,
  otherwise keep it only if two independent sources agree on the displayed fact."
  Each of the three already has two independent reputable sources (Nature/PMC +
  museum/encyclopedia) that agree on the simple displayed fact, and no clearly
  better-sourced same-age replacement was found that fits the subject slot.
  *Reason:* swapping risks a worse-fitting creature; the two-source-agreement
  bar is met. Re-evaluate if a better source/replacement surfaces.
- **D3 — Fact cards: gated on two independent agreeing sources, no parent tick.**
  `fact_card.verified` is repurposed to mean "passed the two-source gate" (not
  "parent approved"). A card is servable only when it has two distinct
  non-Wikipedia sources whose content supports the displayed fact. The printable
  approval sheet remains as an optional audit, never a gate. *Reason:* prompt
  section 2 removes parent approval; section 5e keeps the two-source rule.
  (Implementation of the flip + the serve-side gate is tracked in STATE queue;
  until the card UI exists, no card is shown to a child anyway.)
- **D4 — Target schools stored per child; until a child's list is set, both share
  the family list in content/target_schools.md.** Exam formats stay UNVERIFIED
  until confirmed from official pages (recorded later in content/exam_formats.md).
  *Reason:* prompt default; parent has not yet assigned schools per child.
- **D5 — Devices: laptop + tablet both. Time budget: as content/pacing_scenarios.md
  (~3 hrs/week per child).** *Reason:* prompt default + parent's stated budget.
- **D6 — No stop-and-wait.** Parent checkpoints become reports under reports/ and
  work continues. *Reason:* prompt section 2.
- **D7 — Resume memory = STATE.md + DECISIONS.md + HEALTH.md; overnight.sh is the
  cross-limit watchdog.** Not using in-session scheduling or .claude/jobs for this
  work. *Reason:* prompt is the governing spec for these runs.

## Mode change, 2026-11-15

- **D11 — Autonomous/overnight mode CANCELLED; regular interactive mode.**
  `AUTONOMOUS_PROMPT.md`, `overnight.sh` and `MORNING_REPORT.md` retired to
  `_trash/` (not deleted, per spec hard-rule 2); must not be run or recreated.
  Two standing-rule files govern all work: `VERIFICATION_AND_QUALITY_SPEC.md`
  (hard rules, verification system 5a-5g, 11+ standard, release gate) and
  `DESIGN_SPEC.md` (visual/interactive experience + visual QA). CLAUDE_CODE_BRIEF.md
  updated (v3) to point to them. KEPT: automated verification replaces parent
  approval of individual questions/lessons/fact cards; the serve gate; preview
  status; and D1-D10. Checkpoints: stop only at the parent's named checkpoints or
  for a genuinely new decision with real consequences. *Reason:* parent instruction.

## Phase 2 decisions, 2026-11-14

- **D8 — Catch-rate threshold for the DETERMINISTIC verifiers = 100%.** The
  planted-bug corpus (scripts/planted_corpus.py) measures maths/VR/NVR/English
  deterministic checks: every planted flaw (wrong key, duplicate option, synonym
  distractor, real-word misspelling, ambiguous grammar) is caught 100%, with 0
  false rejects on genuine items (report: reports/catch_rates_2026-11-14.md;
  guarded by tests/test_catch_rates.py — a drop fails the build). *Reason:* these
  verifiers are exact re-derivations, so anything below 100% is a verifier bug,
  not a tuning choice. LLM-based language verifiers (below) will get a lower,
  defended threshold once built.
- **D9 — NVR served answer is tied to the solver.** verify_computable adds an
  `answer_matches_solved` check so a wrong NVR key (letter disagreeing with the
  geometrically-real view index) is rejected, closing a gap where the NVR solver
  ignored the served letter.
- **D10 — Language R types that need judgement stay `not_served` until the
  blind-solve/adversarial pipeline exists and is measured.** The deterministic
  English checks (synonym/antonym/spelling/grammar-agreement key+ambiguity) are
  measured and pass; but comprehension, cloze, vocabulary-in-context and
  literary-technique items need the 3+ independent blind solves + adversarial
  pass (brief 5b). Those are PENDING (usage cost to be measured and logged before
  enabling); their topics are not served until then. *Reason:* priority 1 —
  never serve an unverified judgement item to a child.
