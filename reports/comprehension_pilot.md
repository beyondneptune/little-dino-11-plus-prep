# Comprehension pilot — 20 items, Claude Code subagents as blind solvers

Run inside the subscription (no external API), per the Checkpoint-7 brief. Nothing
here is served.

## Method
- **20 original items** across 4 original passages (`content/comprehension_pilot/items.json`),
  each with the question, 4 options, the key, and an **evidence span** (the sentence
  that justifies the key). Mix of literal and inference.
- **3 independent blind solves:** three separate `claude` subagents, each given ONLY
  the passages + questions + options (no key, no span), returning a letter + the
  sentence they relied on.
- **1 adversarial pass:** a fourth subagent asked to list EVERY option defensible
  from the passage (to catch items where two options could both be argued).
- **Pass rule:** an item passes only if all three blind solves equal the key AND cite
  a span overlapping the authored span AND the adversarial finds exactly one
  defensible option.

## Result
| Metric | Value |
|---|---|
| Items | 20 |
| 3/3 blind solvers agreed with the key | **20 / 20** |
| Blind-solve evidence matched the authored span | 20 / 20 |
| Adversarial found a second defensible answer | **0 / 20** (no ambiguity) |
| Items that would pass the gate | **20 / 20** |

## Usage & cost (measured, this pilot)
- **4 subagent calls** for 20 items (3 blind + 1 adversarial), run in parallel.
- Subagent tokens: ~18.1k, ~18.0k, ~18.1k (blind) + ~18.4k (adversarial) ≈ **72.6k
  subagent tokens total ⇒ ~3.6k tokens per item** at the subagent level (plus the
  orchestration/authoring in the parent).
- Wall-clock: each subagent ~10–13 s (parallel); whole pilot ~128 s including setup.
- Extrapolated: at ~3.6k subagent tokens/item, a batch of 1,000 verified items is
  on the order of a few million subagent tokens — cheap enough to run offline in
  batches, with a human spot-audit on top.

## Honest findings (what the pilot EXPOSED — this is the point)
1. **Authoring bug caught.** One item (P4Q5) had a stored key that did not match any
   option. A validation step (key ∈ options, exactly one) must run before solving —
   the pilot found it, I fixed it.
2. **Positional confound in MY authoring.** I placed the correct answer at option **A
   for all 20 items**. A solver biased to "A" would also score 20/20, so the blind
   agreement alone is **not** strong evidence. Two things rescue it: every blind solve
   cited the *correct evidence sentence* (genuine reading, not position-guessing), and
   the adversarial found no second defensible answer. **But a real run must shuffle the
   key position** and include items whose answer is NOT A, or the agreement number is
   confounded.
3. **The blind solvers agreed too easily** on these deliberately-clean items. Real 11+
   inference questions are harder; the pilot should include **harder, genuinely
   ambiguous** drafts to prove the adversarial pass actually rejects them (so far it
   has only confirmed clean items).

## Recommendation
The pipeline mechanics work end-to-end on the subscription. Before trusting it to
serve, the next run must: (a) validate keys (∈ options, unique, varied position);
(b) include planted-flawed and genuinely-ambiguous drafts to measure the adversarial
catch rate (not just confirm clean items); (c) record the span-overlap automatically.
Until that measured catch rate clears 99%, **comprehension stays unserved.**
