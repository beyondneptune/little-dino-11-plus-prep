# Maths level descriptors (Levels 1–5)

Calibrated from a difficulty profile measured offline over a sample of real 11+
papers. **This is a statistical calibration, not copied content** — no past-paper
question is reproduced. Numbers in real papers are mostly 1–3 digits
(35% / 43% / 12%), ~8% involve decimals, ~3 fractions per paper; the core topics
are fractions, percentages, ratio, algebra/sequences, area/perimeter, angles,
statistics, money, time and measures, and every paper is heavily **multi-step**
and **worded**.

Levels 1–2 are the Age-1 foundation already served (single-step, small numbers).
Levels 3–5 are the 11+ standard: multi-step, mixed-operation, worded and
**trap-aware** (plausible wrong options that match a common slip).

## Level 3 — secure 11+ (two steps)
- **Steps:** exactly two operations, or one operation inside a short word problem.
- **Numbers:** 2–3 digit; simple decimals to 1 dp; unit fractions and halves/quarters.
- **Form:** some bare calculations, some one-sentence word problems.
- **Traps:** order-of-operations slips; forgetting to complete the second step.
- *Examples of the standard (patterns, not served text):* `7 × 8 − 15`;
  "6 pencils at 45p — how much change from £5?"; "¼ of 48, then add 7".

## Level 4 — strong 11+ (two–three steps, mixed operations)
- **Steps:** two or three operations, mixing +−×÷ and a fraction/percentage/ratio
  step; may require choosing which operation to use.
- **Numbers:** 2–4 digit; decimals to 2 dp (money); common fractions and %
  (10%, 25%, 50%, 75%).
- **Form:** mostly worded, multi-sentence; information must be selected.
- **Traps:** percentage of the wrong base; ratio share vs. total; mixed units.
- *Standard:* "A £60 coat is reduced by 15%, then a further £5 off — final price?";
  "Share 48 sweets in the ratio 3:5 — how many more does the larger share get?"

## Level 5 — super-selective 11+ (three+ steps, reasoning)
- **Steps:** three or more linked steps, or a step that needs reasoning/working
  backwards; multiple constraints.
- **Numbers:** up to 5–6 digits in place-value items; decimals to 2 dp; mixed
  fractions; two-step percentage/ratio.
- **Form:** dense word problems; some "work backwards from the answer"; inverse
  reasoning; rate/proportion.
- **Traps:** every distractor matches a specific believable error (one step
  skipped, wrong operation order, right number/wrong units).
- *Standard:* "A tap fills 3 litres in 4 minutes; how long to fill a 18-litre
  bucket?"; "After spending ⅓ then ¼ of what was left, £36 remains — how much at
  the start?"

## Per served-topic ladder (Age 1 foundation → 11+)
| Topic | L1–L2 (served) | L3 | L4 | L5 |
|---|---|---|---|---|
| Rounding (MA-A05) | round to 10/100 | round to 1000 / 1 dp; round then compare | round in a worded estimate (2 steps) | estimate a multi-step calculation by rounding each part |
| Mental calc (MA-B01) | single +−×÷ | two-step chains (BODMAS, no brackets) | mixed-operation with brackets | multi-step worded, work-backwards |
| Division facts (MA-B04) | table facts | division with remainder; worded sharing | two-step: divide then scale | rate/grouping over several steps |
| Compare/order (MA-A03) | largest of 4 | order 5 incl. negatives/decimals | compare results of two calculations | order fractions/decimals/percentages mixed |
| Roman numerals (MA-A07) | read to ~50 | read/compare to 1000 | add two Roman values | Roman in a worded date/clock problem |
| Missing number (MA-B06) | one inverse step | two-step inverse | missing number in a worded two-step | work backwards through 3 steps |
| Odd/even/multiples (MA-B13) | identify one | common multiples/factors | LCM/HCF of a pair | number-property reasoning (which could be X) |
| New core topics to add at L3–5 | — | money change (2-step), fraction-of, percentage-of | ratio share, area/perimeter, mixed-unit convert | multi-step %/ratio, work-backwards, rate |

**Verification rule for every L3–5 item (required):** the answer must agree
across **two independent methods** — the forward independent solver *and* a
different-method cross-check (reverse calculation or a second solver with
different logic) — see `scripts/verify2.py`. Every distractor must correspond to
a named slip so the per-option explanation can name the mistake.
