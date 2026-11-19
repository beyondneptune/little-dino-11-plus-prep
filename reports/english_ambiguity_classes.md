# English SPaG — ambiguity-class evidence (per served type)

For each served type, the real-world ambiguity classes that could give an item
**two acceptable answers**, and exactly how each is handled: **excluded** from the
served generator, and **caught** by the checker (proved in
`tests/test_english_ambiguity2.py`). This replaces the earlier "n/a, unique by
design" with concrete evidence.

The common mechanism: each checker holds the full set of **valid** answers for the
prompt (including variants). An item that offers more than one valid answer fails
`_unique_correct`, so it can never be served; and the generators draw only from
pools with these classes removed.

| Type | Ambiguity class | How handled |
|---|---|---|
| **spelling** | UK/US & -ise/-ize variants (colour/color, realise/realize, favourite/favorite) | `VALID_WORDS` includes the US variants, so an item offering both a UK and US spelling is **caught** (two real words). Served items use only attested *misspellings* as distractors — **excluded**. |
| **plural** | words with two valid plurals (fish/fishes, hoof/hooves, index/indexes-indices) | `PLURAL_ALT` lists both forms; the checker accepts **either**, so an item offering two of them is **caught**. The generator pool removes every `PLURAL_ALT` word — **excluded**. |
| **agreement** | collective nouns (team/family/class…) take singular OR plural in British English | `check_agreement` rejects any sentence whose subject is a collective noun — **excluded + caught**. The served templates contain none. |
| **homophone** | a sentence where two homophones both fit | Only **vetted, one-answer** sentences are accepted; any un-vetted sentence is **rejected** by the lookup, so a two-fit sentence can never slip in. |
| **contraction** | — | one standard contraction per phrase (don't, it's…); vetted list, checker rejects anything else. |
| **affix** | — | each prompt maps to exactly one vetted word; distractors are other vetted words (wrong meaning). |

## Tests (planted flaws, all caught)
`tests/test_english_ambiguity2.py`:
- UK/US spelling variant item → rejected.
- fish/fishes plural item → rejected.
- "The team is/are…" collective agreement → rejected.
- un-vetted homophone sentence → rejected.
- the served generators never emit any of these classes (400–300 item sweeps).

## Typed answers
Spelling is **MCQ only** ("which is spelt correctly?" has no typed form). Plurals
are **typed** and, because every two-form word is excluded, each served plural has
exactly one correct typed answer (case-insensitive). Where a word genuinely has two
forms it is not served, so there is no "accept one, reject the other equivalent".
