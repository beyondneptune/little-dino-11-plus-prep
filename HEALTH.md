# HEALTH — rewritten every working session

- **Date:** 2026-11-15 (regular interactive mode; autonomous cancelled)
- **Tests:** `make test` green (see latest run).
- **Standing rules:** VERIFICATION_AND_QUALITY_SPEC.md + DESIGN_SPEC.md.

## STEP 1 correctness fixes — done
- **1a audit / MA-B01 fix:** MA-B01 is now true single-operation mental arithmetic
  (`age1_gen.g_mental_single` + extended independent solver); the old a×b±c
  order-of-operations template is homed under MA-B05; a test guards the mislabel.
- **1b per-level:** generators declare their levels; banks + served-status are
  per (topic, level); a level with no verified content is never served.
- **1c registry:** `scripts/registry.py` is the single source; verifier_status is
  derived from it (hand-set removed); the build fails on any generator/solver
  disagreement or template↔topic mismatch. **29 topics have a verifier.**
- **1d mutation testing:** generator/solver/checker bugs each caught 1.00; the
  shared generator+solver convention bug is the honest blind spot (caught 0.00),
  pinned by a test. reports/mutation_2026-11-15.md.
- **1e lesson verification:** worked examples re-computed by the solver; a planted
  wrong example fails; reading-grade check (lessons read at grade 2.2-5.3 ≤ 6.0).
- **1f honest labels:** served content is **foundation (levels 1-2, single-step)**
  only; 11+ (levels 3-5, multi-step) not built or claimed; guarded by a test.

## Served content (Age 1)
- **4 of 35 topics served, foundation only:** MA-A05, MA-B01, MA-B04 at L1-L2;
  VR-C02 at L2. Each has a verified bank (150/level) and a lesson.
- Everything else `not_served` with a reason (reports/age1_served_status.md).

## Verification machinery
- Serve gate (qschema): nothing unverified reaches a child (tested).
- Computable pipeline: generator → independent solver → gate.
- Catch rates: planted-bug corpus 100% caught, 0 false-reject
  (reports/catch_rates_2026-11-14.md); plus code mutation testing (1d).
- Hang guard active (2s/call).

## Not built yet / open
- No child-facing app (Phase/STEP 2 next): playable Age-1 slice + visual QA.
- Language (R) topics not served until the blind-solve pipeline is built+measured
  (STEP 4 / CHECKPOINT 2).
- 11+ multi-step levels (3-5) for Age-1 topics not built.
- Backups daily (Phase 0); restore test still TODO.
