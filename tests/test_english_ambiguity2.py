"""Real-world ambiguity in the served English types (parent Checkpoint-8, §2a).
For each named class — UK/US spelling variants, two-form plurals, collective-noun
agreement, un-vetted homophone/apostrophe items — we PLANT the flaw and show the
checker rejects it, AND confirm the served generators never produce it."""
import english_rulegen as R


def _it(kind, question, options, answer_letter, **check):
    check["kind"] = kind
    return {"question": question, "options": options, "answer": answer_letter, "_check": check}


def test_uk_us_spelling_variant_is_rejected():
    # "favourite" (UK) and "favorite" (US) are BOTH real words -> ambiguous
    it = _it("spelling", "Which word is spelt correctly?",
             ["favourite", "favorite", "favourit", "faverite"], "A", word="favourite")
    assert not R.check_spelling(it), "an item offering both UK and US spellings must be rejected"


def test_two_form_plural_is_rejected():
    it = _it("plural", "What is the plural of “fish”?",
             ["fish", "fishes", "fishs", "fishies"], "A", word="fish")
    assert not R.check_plural(it), "fish/fishes are both valid -> must be rejected"


def test_collective_noun_agreement_is_rejected():
    it = _it("agreement", "The team ___ winning.", ["is", "are", "ising", "aring"], "A",
             sentence="The team ___ winning.")
    assert not R.check_agreement(it), "a collective subject takes is OR are -> must be rejected"


def test_unvetted_homophone_sentence_is_rejected():
    it = _it("homophone", "I can ___ the answer.", ["right", "write", "rite", "wright"], "B",
             sentence="I can ___ the answer.")
    assert not R.check_homophone(it), "only vetted, one-answer sentences are accepted"


def test_served_generators_never_produce_the_ambiguity_classes():
    for it in R.generate("plural", 400, 1):
        assert it["_check"]["word"] not in R.PLURAL_ALT, "a two-form plural was served"
    for it in R.generate("spelling", 400, 1):
        real = [o for o in it["options"] if o in R.VALID_WORDS]
        assert len(real) == 1, f"a spelling item offered {len(real)} real words"
    for it in R.generate("agreement", 300, 1):
        words = it["_check"]["sentence"].lower().replace(".", "").split()
        assert not any(w in R.COLLECTIVE_NOUNS for w in words), "a collective subject was served"
