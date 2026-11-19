# Reading-comprehension: design + cost (proposal — not built, not served)

Comprehension is the one Age-1 English strand that cannot be made safe by word
lists or rules; it needs a language model, used **offline in batch** before any
item is published (the app has no runtime network). This document proposes the
design and a cost model so you can decide whether to proceed. **Nothing here is
served.**

## Design: evidence-anchored items with blind-solve + adversarial verification

1. **Original passage.** Generate a short original passage (~180–260 words) at a
   Year-4–5 reading level, on a neutral topic, with no copyrighted source. Store
   it with a stable token/sentence index.
2. **Authoring with evidence spans.** For each question, the author step must emit:
   the question, 4 options, the key, and an **evidence span** — the exact
   sentence/character range in the passage that justifies the answer. A literal
   item's span must *contain* the answer; an inference item's span must *entail*
   it. An item with no span is rejected automatically.
3. **Blind solve ×K (independent).** Give K=3 fresh model instances ONLY the
   passage + question + options (no key, no span, no author rationale) and ask
   each to pick the answer and cite its own span. Accept only if **all K agree
   with the key AND cite a span overlapping the author's span.** Disagreement →
   reject.
4. **Adversarial second-answer search.** A separate adversarial pass is told "find
   a DIFFERENT option that could also be defended from the passage, with a span."
   If it finds a defensible second answer, the item is **ambiguous → rejected.**
   This is the language analogue of the maths cross-check and the NVR uniqueness
   proof.
5. **Readability + safety gate.** Reading-grade ≤ 6 (reuse `lesson_check`), banned-
   topic filter, no proper nouns that could be a real person. Only items passing
   every stage are written to the bank with their evidence spans retained for audit.
6. **Human spot-audit.** Even after the above, a sample is exported (like
   `audit_sample.json`) for your independent review before a topic goes live.

**Serve bar (same as everything else):** on a planted-flaw harness (wrong key,
two-defensible-answers, off-passage answer, ambiguous wording) the pipeline must
**catch ≥ 99%**, measured and recorded, before any comprehension topic is served.

## Cost model (estimate — a live pilot needs an LLM API wired in)

This environment has no runtime model API, so the numbers below are a **modelled
estimate**, not a measured pilot. Assumptions per item:

| Stage | Calls | Input tokens | Output tokens |
|---|---|---|---|
| Authoring (passage shared across ~6 Qs) | 1 / 6 Qs | ~1.4k (shared) | ~0.4k |
| Blind solve ×K | 3 | ~0.6k each | ~0.1k each |
| Adversarial 2nd-answer | 1 | ~0.7k | ~0.2k |
| Readability/safety (local) | 0 | — | — |

Per **verified** item (allowing for a ~40% rejection rate, so ~1.7 attempts/kept):
- tokens ≈ (3×0.7k + 1×0.9k + authoring share 0.3k) × 1.7 ≈ **~5.6k tokens/item**.
- At indicative batch pricing of ~$3/M input + ~$15/M output (mix ≈ $5/M blended),
  that is **≈ $0.03 per verified item** — roughly **$30 for 1,000 items**, plus a
  one-off human audit of a sample.
- Time: batchable; at ~2 s/call, ~5 calls/item ⇒ ~10 s/item of model time,
  parallelisable offline.

**Recommendation.** Run a real **20-item pilot** once an LLM API is available to
replace these estimates with measured numbers, then decide. Until then,
comprehension stays on the real papers and is not served. The pilot harness and
the planted-flaw classes already exist (`english_measure.py`,
`english_ambiguity.py`) and would be extended with the "off-passage answer" and
"two-defensible-answers" classes above.
