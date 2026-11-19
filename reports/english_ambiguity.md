# English / VR — AMBIGUITY catch rates (separate from structural)

Structural flaws (wrong key, duplicate answer) are caught 100% — that is NOT evidence the items are sound. These are the harder, realistic flaws: a genuine second correct answer, or a 'wrong' option that is actually valid. **Language stays unserved until these also clear the 99% bar with the evidence recorded.**

| Type | Ambiguity flaw | Planted | Catch rate | Note |
|---|---|---|---|---|
| word_analogy | second_correct_synonym | 99 | 26.3% |  |
| odd_word | second_odd_one | 200 | 100.0% |  |
| spelling | valid_variant | 0 | n/a | no planted items (word list too small to build this flaw) |

## Reading
- Where the word list KNOWS the alternative, the checker's uniqueness logic catches it. Where it does NOT (a real synonym/variant outside the curated list), the item passes undetected — so the true limit is **word-list completeness**, not the checker.
- This is why language is not served: a 100% structural score hides an incomplete lexicon. The fix is bigger, sense-tagged, hand-audited word lists + a confusable/variant blocklist, then re-run this harness.
