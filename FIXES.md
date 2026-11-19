# Question generators — review fixes (14 Nov 2026)

An independent audit found answer-key errors that the original testers passed
as "100% verified". All are fixed below, and the testers were rewritten so the
same class of error is now caught automatically.

## Wrong answers fixed

| Area | Fault | Fix |
|---|---|---|
| NVR cube nets | ~half of "correct" answers were the cube's **mirror image** (impossible to fold). The renderer also drew every cube mirrored. | Correct folding convention (net = outside of cube); correct left/right in the drawing; answer is a real view of the folded cube; distractors include mirror-image traps. |
| NVR cube rotation | Options could show faces not visible on the reference cube, so a child could not work out the answer. | Options now use only the three reference faces: one genuine rotation + three mirror images. |
| Maths rounding | Python's `round()` rounds halves to even: "Round 5305 to the nearest 10" was marked 5300. | Halves round up (the school rule). |
| Maths percentages | "Find 10% of 24" was marked 2 (decimal dropped). | Numbers chosen so the answer is always whole. |
| Maths money | "Pay £7.05 with a £5 note" → negative change, and the generator froze. | The note always covers the cost. |
| English grammar | "The dog ___ every day": *barks* and *barked* both correct. | Distractors are always ungrammatical; added 11 authored tense/agreement items. |
| English spelling | "defiantly" (a real word) offered as a misspelling. | Removed; every misspelling hand-checked; bank grown from 12 to 33 words (incl. Y5–6 statutory list). |
| Synonyms / antonyms / VR analogies | A distractor could also be correct (e.g. *big* and *massive*). | Meaning clusters in `vocab.py`; distractors from the same cluster are excluded. |
| VR odd-one-out | Words in two categories (silver = metal and colour; plum = fruit and colour). | Categories rebuilt with no overlaps. |
| VR letters-for-numbers | Letters A–E in the question clashed with answer labels A–D. | Uses letters L–Z. |

## Testers rewritten (`scripts/testers.py`)

- **Maths:** reads the question text and solves it from scratch; exactly one option may match, and it must be the marked one. Unknown question formats fail rather than pass. (Previously it only checked there were 4 options.)
- **NVR:** folds nets with separate 3D geometry and judges each option with an orientation test, so mirror images are rejected. Rotation options must be solvable from the picture.
- **VR:** rule types re-derived from the question; word types checked for a second valid answer.
- **English:** checks the key plus the known ways a second answer can sneak in. A strong filter, not a proof — spot-check new authored items by hand.

Proof the testers work: run against the **original** code they reject 88/3000 Maths, 700/3000 English and 211/400 cube-net questions. Against the fixed code: 0 failures across 60,000 Maths, 12,000 VR, 12,000 English and 6,000 NVR questions.

## Still true (not fixed here)

- Maths questions are all single-step; selective papers need multi-step problems.
- English bank is small (33 spelling words, 15 cloze, 21 grammar sentences) — repeats will appear.
- Coverage of the syllabus is thin (roughly Maths 15/128 topics, English 5/119, VR 6/45, NVR 5/48).
- NVR symbols are treated as orientation-free.
