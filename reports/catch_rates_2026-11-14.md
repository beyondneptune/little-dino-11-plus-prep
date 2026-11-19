# Catch rates — planted-bug corpus (2026-11-14)

Deterministic verifiers (testers.py). Catch rate = fraction of planted
flawed items REJECTED. Control = genuine items wrongly rejected (want 0).
Threshold for these deterministic checks = 100%.

| Subject | Flaw | planted | caught | catch rate |
|---|---|---|---|---|
| english | ambiguous_grammar | 250 | 250 | 100.0% |
| english | control_false_reject | 250 | 0 | 0.0% |
| english | duplicate_option | 250 | 250 | 100.0% |
| english | realword_misspelling | 250 | 250 | 100.0% |
| english | synonym_distractor | 250 | 250 | 100.0% |
| english | wrong_key | 250 | 250 | 100.0% |
| maths | control_false_reject | 250 | 0 | 0.0% |
| maths | duplicate_option | 250 | 250 | 100.0% |
| maths | wrong_key | 250 | 250 | 100.0% |
| nvr | control_false_reject | 250 | 0 | 0.0% |
| nvr | wrong_key | 250 | 250 | 100.0% |
| vr | control_false_reject | 250 | 0 | 0.0% |
| vr | duplicate_option | 250 | 250 | 100.0% |
| vr | wrong_key | 250 | 250 | 100.0% |

## Pending (need the blind-solve/adversarial language pipeline)
- two-defensible-answer on comprehension/cloze, off-level reading, factual
  errors on authored passages. Those R types stay `not_served` until the
  pipeline is built and its catch rate is measured here.
