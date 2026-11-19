# Verification, quality and safety spec (standing rules)

These rules apply to ALL work on the Dino Ages platform, in regular interactive
mode. They were saved from the earlier autonomous prompt, which has been
cancelled. The parent does NOT approve individual questions, lessons or fact
cards: automated verification below replaces that. Renumbered headings keep
their old section numbers for cross-reference.

## 3. Hard rules: never do these

1. Never serve a question to a child that has not passed every gate in
   section 5. This is enforced in code at serve time, not by convention.
2. Never delete files. Move anything you no longer need to `_trash/`. Never
   delete or overwrite the parent's papers (PDF folders), any `progress.db`,
   backups, backups.
3. Never run `git push`, never contact any service with children's data, never
   add analytics, trackers, adverts or external fonts/CDNs. The app must work
   with the network blocked.
4. Never copy content, characters, art, music or names from other publishers
   or franchises (no Jurassic Park, Disney, Land Before Time, Flintstones,
   Pokémon and so on). Use original art, or freely licensed assets with the
   licence recorded in `assets/LICENSES.md`.
5. Never claim something is verified without a check that **can fail**. Every
   new check gets a planted-bug test showing it fails.
6. Never leave a session with failing tests, uncommitted work, or a half-finished
   change. If a change is going badly, revert to the last green commit, record
   what happened in `STATE.md`, and move to other work.
7. Never kill processes you did not start. Never start a server or job without
   a timeout, and stop whatever you started.
8. Never put dinosaur or era facts in the app that are not checked (section 5).

---

## 5. Verification and failsafes (the heart of the project)

### 5a. Computable items (Maths, number VR, NVR and so on)
Generator and solver are **separate code with separate logic.** The solver
works from the rendered question, exactly one option may be correct, results
must be sensible, thousands of seeds are property-tested, and every tester has
planted-bug (mutation) tests. Every bug ever found becomes a permanent
regression test. Unknown formats are rejected, never passed.

### 5b. Language and judgement items (synonyms, grammar, punctuation,
### spelling, comprehension, cloze, vocabulary in context)
An item is served only if ALL of these pass:
1. **Data-based generation where possible:** open lexicon (e.g. WordNet),
   rule-based grammar generation, verified word lists, so answers come from
   data rather than one model's opinion.
2. **Three or more independent blind solves** that never see the answer key
   must all agree with it. Tell me in `DECISIONS.md` how they are run and what
   they cost in usage. Prefer methods that differ from each other.
3. **Adversarial pass:** a separate pass tries to find a second defensible
   answer. Any success rejects the item.
4. Automated checks: reading level for the child's age band, duplicates,
   banned content, distractor quality (each wrong option reflects a plausible
   misconception and has its own explanation).

### 5c. Measure the checker
For each language question type, build a corpus of **at least 200 planted
flawed items** (wrong key, two defensible answers, synonym as distractor,
ambiguous grammar, off-level reading, duplicates, factual errors) and report
the catch rate. A type may auto-serve only if its catch rate is high enough
that you can defend it; record the number and your chosen threshold in
`DECISIONS.md`. **Types below the threshold are not served.** Re-run the
planted corpus whenever a verifier changes; a drop in catch rate fails the
build.

### 5d. Live safety net
- Per-item statistics from the children's answers; anomalies (much harder or
  easier than the level predicts, an oddly popular wrong option, strong
  performers failing it) withdraw the item automatically.
- A "this looks wrong" button on every question withdraws the item instantly.
- A rejected item at serve time raises a visible warning in the parent area.

### 5e. Fact cards and era facts
Every displayed fact needs two independent reliable sources that agree
(museum or scientific source plus one other). Disagreement means drop or
replace the fact. Dinosaurs only in Ages 5-8; pterosaurs, marine reptiles,
synapsids, fish and mammals are not dinosaurs; creatures from different ages
never appear to meet. Where science is uncertain (colour, feathers, behaviour),
say "scientists think".

### 5f. Creative writing and open-ended answers
Give rubric feedback, never use it to gate progress, and say so in the UI.

### 5g. Engineering failsafes (all must exist and be tested)
1. `make test` green before every commit; auto-revert on regression.
2. Per-call 2-second hang guard over thousands of generator/tester calls.
3. Deterministic reproduction: any question a child saw can be rebuilt from
   its stored seed and versions.
4. Exposure control: a child does not see the same question again within 14
   days unless it is a deliberate review.
5. Database migrations, a backup before every migration, a daily automatic
   backup, a restore test. Never lose a child's progress.
6. No dead ends: a station with too little verified content is hidden and
   skipped, and never blocks progress. The child never sees an empty station,
   a blank screen, a stack trace or a raw error; they see a friendly message
   and the error is logged.
7. Parent area behind a PIN so children cannot wander into settings.
8. `HEALTH.md` rewritten every working session: tests, counts of served/not_served topics,
   rejection counts, catch rates, backup status, open problems.

---

## 6. 11+ quality standard

- Follow brief section 4. Levels 1-5 per topic with a written definition
  (steps, number size, distractor subtlety, vocabulary tier). Levels 3-5 Maths
  must be multi-step: unnecessary information, working backwards, combined
  ratio/fraction/percentage, averages with missing values, timetables,
  multi-condition puzzles.
- Study the real papers in the project **read-only** for format, wording
  style, number of options, timing and difficulty statistics; never copy.
- Distractors come from a per-topic table of real misconceptions, and each
  wrong option has its own explanation.
- Writing for ages 7-9 in the early ages (check reading level), rising later.
- Dinosaur-themed word problems must keep their numbers honest (use "about"
  for estimates) and must not weaken the mathematics.
- The game layer is a skin over verified questions. It must never change what
  a question asks or how it is marked.

---

## 9. Release gate (an age is visible to children only when ALL are true)

1. Its topics are either served with enough verified content (section 4,
   Phase 3 targets) or `not_served` and hidden without blocking progress.
2. `make test` passes, including serve-gate, hang-guard, planted-bug and
   regression tests.
3. Measured catch rates for its language item types meet your recorded
   threshold.
4. Facts on its creatures are two-source verified.
5. Visual QA passes and the simulated-child end-to-end test passes.
6. Backups and the restore test pass.
Otherwise the age stays hidden and the reason is written to
the next checkpoint report.

---
