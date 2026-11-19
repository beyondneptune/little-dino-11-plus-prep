# Maths Levels 3–5 rollout status

Each served maths topic, and whether it now ladders L1→L5. Every L3–5 item is
dual-verified (forward solver + a different-method cross-check), with metamorphic,
planted-bug mutation, and golden known-answer tests (`tests/test_l35_*`).

| Topic | Title | Ladders | L3–5 generator(s) | Notes |
|---|---|---|---|---|
| MA-B01 | Mental calculations | **L1→L5** | two/three-step BODMAS | brackets + ÷× order |
| MA-A05 | Rounding | **L1→L5** | estimate-by-rounding (sum L3, product L4, bracketed L5) | multi-step estimation |
| MA-B04 | Division facts | **L1→L5** | worded division (share L3, remainder L4, two-step L5) | |
| MA-B06 | Missing numbers | **L1→L5** | two-step inverse (L3–4) + work-backwards (L5) | |
| MA-A03 | Comparing numbers | **L1→L4** | compare-after-calculating (L3-4) | multi-step: work out both, then compare |
| MA-A07 | Roman numerals | L1–L2 only | — | *number-notation knowledge, not multi-step reasoning; L3 "read to 1000" possible, no L4–5* |
| MA-B13 | Odd/even & multiples | **L1→L4** | lowest-common-multiple / highest-common-factor (L3-4) | multi-step reasoning |

**4 of 7 served maths topics ladder the full L1→L5.** The three that stop at L1–L2
are number-knowledge topics that do not make natural multi-step 11+ word problems;
each is flagged with how far it *could* extend (L3) if wanted.

**Other verified multi-step types** available in the library (`maths_l35.py`) but
mapped to later-age topic ids, so not attached to an Age-1 creature yet:
money-change, fraction-then, percentage-then-reduction. They are fully tested and
ready to wire when those topics open.
