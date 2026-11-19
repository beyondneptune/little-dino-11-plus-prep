branch: ui-overhaul (not merged — gate in UI_OVERHAUL_PROMPT.md section 8)
mode: regular interactive
done:
  - phase0, phase1, phase1b (taxonomy, verification core)
  - STEP 1 correctness fixes a-f (registry, MA-B01 fix, mutation testing, lesson
    verification, honest foundation-only levels) — on main and inherited here
  - UI overhaul: design foundations (self-hosted Fredoka/Nunito, tokens, chunky
    components, Web-Audio synth, canvas particles, markdown renderer, motion) +
    the VERTICAL SLICE (Home, Age-1 Cambrian map with all 6 stations + Fossil Dig,
    Trilobite station: meet/learn+number-line/practise/finish, buddy dino)
current: AWAITING PARENT at the UI checkpoint (design/UI_CHECKPOINT.md). Do NOT
  build other ages/screens until approved.
tests: make test green (67). Engine/verifiers/serve gate untouched by the UI.
honest_art_note: Trilobite = good stylised vector; the other 5 Age-1 creatures are
  basic silhouettes. A drop-in art pipeline (assets/art/<creature>/ layered parts
  re-using the rig) is OFFERED but NOT built — ask to add it. No weak art shipped
  as "final".
queue_after_approval:
  - wire drop-in art pipeline if the parent wants richer creatures
  - rebuild Anomalocaris + Pikaia stations, Fossil Dig interaction, Museum hall,
    Parent redesign on the new system (fix their section-1 bugs fully)
  - then the other nine ages, each its own scene/palette/creatures, QA at 3 sizes
  - STEP 3 (content): more verified Age-1 topics; STEP 4 language checker (needs
    cost measurement) — both are engine work, separate from the UI branch
notes:
  - No runtime network; all fonts/art/sound self-hosted (design/LICENSES.md).
  - Do NOT touch generators/testers/serve gate/mastery logic in the UI pass.
