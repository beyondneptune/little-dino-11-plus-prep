# English / VR verification — measurement report

Harness: 200 items per type; each flaw planted on every item; the data-based checker's **catch rate** (% of flawed items rejected) is shown. No language-model judgement is used, and **nothing here is served**.

A type is *guardable today* only if it catches **>= 99%** of every applicable flaw. Clean items should pass ~100%.

| Type | Subject | Clean pass | wrong_key | two_correct | bad_spelling | ambiguous | grammar | Guardable? |
|---|---|---|---|---|---|---|---|---|
| synonym | english | 100% | 100.0% | 100.0% | 97.5% | n/a | n/a | ❌ no |
| antonym | english | 100% | 100.0% | 100.0% | 100.0% | n/a | n/a | ✅ yes |
| grammar_agree | english | 100% | 100.0% | 100.0% | 100.0% | n/a | 100.0% | ✅ yes |
| spelling | english | 100% | 100.0% | 100.0% | 86.0% | n/a | n/a | ❌ no |
| odd_word | vr | 100% | 100.0% | 100.0% | 97.5% | 100.0% | n/a | ❌ no |
| word_analogy | vr | 100% | 100.0% | 100.0% | 97.5% | n/a | n/a | ❌ no |
| letter_series | vr | 100% | 100.0% | 100.0% | n/a | n/a | n/a | ✅ yes |
| number_series | vr | 100% | 100.0% | 100.0% | n/a | n/a | n/a | ✅ yes |

## Cost per item (data-based checker, no tokens)
| Type | seconds/item |
|---|---|
| synonym | 0.001 ms |
| antonym | 0.008 ms |
| grammar_agree | 0.001 ms |
| spelling | 0.006 ms |
| odd_word | 0.003 ms |
| word_analogy | 0.005 ms |
| letter_series | 0.001 ms |
| number_series | 0.001 ms |

## Verdict
- **Reach >= 99% on all applicable flaws:** antonym, grammar_agree, letter_series, number_series.
- **Not yet guardable:** synonym, spelling, odd_word, word_analogy.

## Proposed data-based generators (no language-model judgement) to close gaps
- **Synonym/antonym:** generate ONLY from a curated thesaurus with explicit sense tags and a hand-checked 'confusable' blocklist, so a distractor can never be a second correct answer; verify both directions against the word list.
- **Spelling:** draw from a fixed misspelling list (one correct, three attested misspellings) so 'bad_spelling' is the item, not a flaw — checker confirms exactly one dictionary word.
- **Grammar agreement:** rule-based subject/verb and determiner agreement over a closed template set; the checker re-derives the only grammatical option.
- **Comprehension / inference:** NOT data-based — needs the blind-solve + adversarial LLM pipeline; stays unserved until that is built and measured here.
