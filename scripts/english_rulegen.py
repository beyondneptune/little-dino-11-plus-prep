#!/usr/bin/env python3
"""Rule/data-based English generators with INDEPENDENT checkers (parent
Checkpoint-7, section 2). These are the English types with OBJECTIVELY-CORRECT
answers, so no language-model judgement is needed:

    homophones · plurals · contractions (apostrophes) · prefixes/suffixes ·
    spelling (from a verified word list) · subject-verb agreement · past tense ·
    end punctuation

Each item is built from a curated, hand-vetted list; the checker re-derives the
answer from that authoritative data (not from the generator's stored key) and
confirms exactly one option is correct and the distractors are vetted-wrong. The
measurement harness (scripts/english_harness.py) runs the structural AND ambiguity
flaw classes per type; only types that clear 99% on BOTH are served.
"""
from __future__ import annotations

import copy
import random

# =========================================================================
# KNOWN AMBIGUITY CLASSES — words/sentences with MORE THAN ONE valid answer.
# These are EXCLUDED from the served generators and used to PROVE the checkers
# catch them (tests/test_english_ambiguity2.py). The checker's `valid` set
# includes every acceptable form, so any item offering two of them is rejected.
# =========================================================================
SPELLING_VARIANTS = {"favourite": "favorite", "colour": "color", "grey": "gray",
                     "realise": "realize", "organise": "organize", "theatre": "theater",
                     "metre": "meter", "centre": "center", "practise": "practice",
                     "traveller": "traveler"}
PLURAL_ALT = {"fish": {"fish", "fishes"}, "hoof": {"hoofs", "hooves"},
              "index": {"indexes", "indices"}, "cactus": {"cactuses", "cacti"},
              "appendix": {"appendixes", "appendices"}, "dwarf": {"dwarfs", "dwarves"},
              "formula": {"formulas", "formulae"}}
COLLECTIVE_NOUNS = {"team", "family", "class", "group", "crowd", "herd", "committee",
                    "government", "staff", "audience"}  # British English allows is OR are

# =========================================================================
# 1) HOMOPHONES — a homophone in a FIXED sentence; exactly one is grammatical
# =========================================================================
HOMOPHONES = [
    ("I put the cups over ___ on the shelf.", "there", ["their", "they're"]),
    ("The children lost ___ coats in the park.", "their", ["there", "they're"]),
    ("I think ___ going to be late today.", "they're", ["their", "there"]),
    ("We ate ___ much cake at the party.", "too", ["to", "two"]),
    ("She walked ___ the shop to buy milk.", "to", ["too", "two"]),
    ("He keeps ___ pet rabbits at home.", "two", ["to", "too"]),
    ("Please write ___ name at the top of the page.", "your", ["you're"]),
    ("I think ___ right about the answer.", "you're", ["your"]),
    ("The dog wagged ___ tail happily.", "its", ["it's"]),
    ("I am sure ___ going to rain later.", "it's", ["its"]),
    ("Can you ___ the music from here?", "hear", ["here"]),
    ("Come over ___ and sit down.", "here", ["hear"]),
    ("We walked along the sandy ___.", "beach", ["beech"]),
    ("The brave knight rode a white ___.", "horse", ["hoarse"]),
    ("After shouting all day his voice felt ___.", "hoarse", ["horse"]),
    ("She tied a ___ in the rope.", "knot", ["not"]),
    ("I would like a ___ of bread, please.", "piece", ["peace"]),
    ("The soldiers hoped for ___ after the war.", "peace", ["piece"]),
    ("The wind ___ through the trees all night.", "blew", ["blue"]),
    ("She painted the door a bright ___.", "blue", ["blew"]),
    ("We could not ___ the heavy box up the stairs.", "bear", ["bare"]),
    ("The ___ feet of the children slapped the floor.", "bare", ["bear"]),
    ("Turn ___ at the end of the road.", "right", ["write"]),
    ("Please ___ your answer in the box.", "write", ["right"]),
    ("Be careful not to ___ the glass.", "break", ["brake"]),
    ("Press the ___ to stop the bike.", "brake", ["break"]),
    ("We need some ___ to bake the cake.", "flour", ["flower"]),
    ("She picked a yellow ___ from the garden.", "flower", ["flour"]),
    ("The ___ of the roses filled the room.", "scent", ["sent"]),
    ("I ___ a card to my cousin.", "sent", ["scent"]),
    ("Which road should we take, this one ___ that one?", "or", ["oar", "ore"]),
    ("He rowed the boat with a single ___.", "oar", ["or", "ore"]),
    ("The knight wore a shining suit of ___.", "mail", ["male"]),
    ("Each ___ lion has a thick mane.", "male", ["mail"]),
    ("A bee landed on the sweet ___.", "flower", ["flour"]),
    ("I need a new ___ of shoes.", "pair", ["pear"]),
    ("She ate a juicy ___ for lunch.", "pear", ["pair"]),
    ("Our team ___ the match on Saturday.", "won", ["one"]),
    ("I only have ___ pencil left.", "one", ["won"]),
]
_HOMO_CORRECT = {t[0]: t[1] for t in HOMOPHONES}
_DECOYS = ["where", "wear", "break", "brake", "flour", "flower", "weather", "whether"]


def gen_homophone(rng, level=None):
    sent, correct, wrongs = rng.choice(HOMOPHONES)
    opts = [correct] + list(wrongs)
    pool = [d for d in _DECOYS if d not in opts]
    while len(opts) < 4 and pool:
        opts.append(pool.pop(rng.randrange(len(pool))))
    opts = opts[:4]
    rng.shuffle(opts)
    return _mcq(sent, opts, correct, f"In this sentence the correct word is “{correct}”.",
                "homophone", sentence=sent)


def check_homophone(it):
    correct = _HOMO_CORRECT.get(it["_check"]["sentence"])
    return _unique_correct(it, correct, valid={correct})


# =========================================================================
# 2) PLURALS — regular rules + irregular list
# =========================================================================
IRREGULAR_PLURAL = {"child": "children", "foot": "feet", "tooth": "teeth", "mouse": "mice",
                    "man": "men", "woman": "women", "person": "people", "goose": "geese",
                    "sheep": "sheep", "fish": "fish", "deer": "deer", "leaf": "leaves",
                    "knife": "knives", "wife": "wives", "life": "lives", "half": "halves"}
REGULAR_SINGULARS = ["cat", "dog", "box", "bus", "dish", "watch", "fox", "glass", "bush",
                     "baby", "lady", "city", "party", "story", "fly", "berry", "book",
                     "tree", "car", "star", "house", "table", "church", "brush"]


def _plural_of(word):
    if word in IRREGULAR_PLURAL:
        return IRREGULAR_PLURAL[word]
    if word.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"
    if word.endswith("y") and word[-2] not in "aeiou":
        return word[:-1] + "ies"
    return word + "s"


def _plural_pool():
    # exclude words with two valid plural forms (fish/fishes, hoofs/hooves, …)
    return [w for w in REGULAR_SINGULARS + list(IRREGULAR_PLURAL) if w not in PLURAL_ALT]


def gen_plural(rng, level=None):
    word = rng.choice(_plural_pool())
    correct = _plural_of(word)
    wrong = {word + "s", word + "es", word[:-1] + "ies" if len(word) > 1 else word + "s", word}
    wrong.discard(correct)
    distractors = [w for w in wrong if w != correct][:3]
    while len(distractors) < 3:
        distractors.append(correct + rng.choice(["es", "s", "s"]))   # harmless over-forms
    opts = [correct] + list(dict.fromkeys(distractors))[:3]
    if len(set(opts)) < 4:
        return None
    rng.shuffle(opts)
    return _mcq(f"What is the plural of “{word}”?", opts, correct,
                f"The plural of “{word}” is “{correct}”.", "plural", word=word)


def check_plural(it):
    word = it["_check"]["word"]
    valid = PLURAL_ALT.get(word, {_plural_of(word)})     # accept EVERY valid plural form
    correct = _plural_of(word)
    return _unique_correct(it, correct, valid=valid)


# =========================================================================
# 3) CONTRACTIONS (apostrophes) — vetted list
# =========================================================================
CONTRACTIONS = {"do not": "don't", "did not": "didn't", "cannot": "can't", "will not": "won't",
                "is not": "isn't", "are not": "aren't", "I am": "I'm", "they are": "they're",
                "we are": "we're", "you are": "you're", "it is": "it's", "that is": "that's",
                "could not": "couldn't", "should not": "shouldn't", "have not": "haven't",
                "was not": "wasn't", "were not": "weren't", "he is": "he's", "she is": "she's",
                "would not": "wouldn't", "has not": "hasn't", "had not": "hadn't",
                "I will": "I'll", "we will": "we'll", "you will": "you'll", "they will": "they'll",
                "I have": "I've", "we have": "we've", "you have": "you've", "they have": "they've",
                "I would": "I'd", "she will": "she'll", "he will": "he'll", "who is": "who's",
                "there is": "there's", "let us": "let's", "must not": "mustn't", "need not": "needn't"}


def _bad_apostrophes(full, correct):
    plain = correct.replace("'", "")
    mid = plain
    if "'" in correct:
        i = correct.index("'")
        mid = correct[:i] + correct[i + 1:]              # drop apostrophe
    # a misplaced apostrophe
    j = max(1, len(plain) - 2)
    misplaced = plain[:j] + "'" + plain[j:]
    return [plain, misplaced, full.replace(" ", "")]


def gen_contraction(rng, level=None):
    full = rng.choice(list(CONTRACTIONS))
    correct = CONTRACTIONS[full]
    distractors = [w for w in dict.fromkeys(_bad_apostrophes(full, correct)) if w != correct][:3]
    if len(distractors) < 3:
        return None
    opts = [correct] + distractors
    rng.shuffle(opts)
    return _mcq(f"What is the correct short form (contraction) of “{full}”?", opts, correct,
                f"“{full}” shortens to “{correct}”.", "contraction", full=full)


def check_contraction(it):
    correct = CONTRACTIONS.get(it["_check"]["full"])
    return _unique_correct(it, correct, valid={correct})


# =========================================================================
# 4) PREFIXES / SUFFIXES — vetted word-building
# =========================================================================
AFFIX = [("not kind", "unkind"), ("not happy", "unhappy"), ("not fair", "unfair"),
         ("not able", "unable"), ("not tidy", "untidy"), ("not real", "unreal"),
         ("not lucky", "unlucky"), ("not usual", "unusual"), ("not safe", "unsafe"),
         ("do again", "redo"), ("heat again", "reheat"), ("build again", "rebuild"),
         ("fill again", "refill"), ("play again", "replay"), ("write again", "rewrite"),
         ("full of hope", "hopeful"), ("full of help", "helpful"), ("full of care", "careful"),
         ("full of colour", "colourful"), ("full of power", "powerful"), ("full of joy", "joyful"),
         ("without hope", "hopeless"), ("without care", "careless"), ("without use", "useless"),
         ("without end", "endless"), ("without fear", "fearless"), ("without pain", "painless"),
         ("able to be read", "readable"), ("able to be washed", "washable"),
         ("able to be enjoyed", "enjoyable"), ("done in a quick way", "quickly"),
         ("done in a slow way", "slowly"), ("done in a kind way", "kindly"),
         ("the state of being dark", "darkness"), ("the state of being kind", "kindness"),
         ("the state of being ill", "illness"), ("before noon (before)", "preview"),
         ("the opposite action of 'appear'", "disappear"), ("the opposite of 'agree'", "disagree"),
         ("the opposite of 'obey'", "disobey"), ("not possible", "impossible"),
         ("not patient", "impatient"), ("not correct", "incorrect"), ("not visible", "invisible")]
_AFFIX_CORRECT = {a[0]: a[1] for a in AFFIX}
_AFFIX_ALL = {a[1] for a in AFFIX}


def gen_affix(rng, level=None):
    meaning, correct = rng.choice(AFFIX)
    others = [w for w in _AFFIX_ALL if w != correct]
    rng.shuffle(others)
    opts = [correct] + others[:3]
    if len(set(opts)) < 4:
        return None
    rng.shuffle(opts)
    return _mcq(f"Which word means “{meaning}”?", opts, correct,
                f"“{meaning}” is written as “{correct}”.", "affix", meaning=meaning)


def check_affix(it):
    correct = _AFFIX_CORRECT.get(it["_check"]["meaning"])
    # valid = ONLY the word whose vetted meaning matches this prompt
    return _unique_correct(it, correct, valid={correct})


# =========================================================================
# 5) SPELLING — correct word vs attested misspellings; checker uses a word list
# =========================================================================
SPELLING = {
    # L3 / Year 3-4 statutory-list words
    "because": ["becuase", "becouse", "becauze"], "friend": ["freind", "frend", "friynd"],
    "beautiful": ["beutiful", "beautifull", "butiful"], "different": ["diffrent", "diferent", "differant"],
    "favourite": ["favourit", "faverite", "favrite"], "February": ["Febuary", "Feburary", "Februrary"],
    "address": ["adress", "addres", "adres"], "believe": ["beleive", "belive", "beleeve"],
    "island": ["iland", "islnd", "ilsand"], "caught": ["cawght", "caut", "coght"],
    "centre": ["centr", "sentre", "senter"], "early": ["erly", "earley", "earlie"],
    "enough": ["enuff", "enogh", "enouph"], "eight": ["eght", "aight", "eigt"],
    "famous": ["fameous", "famus", "famos"], "grammar": ["grammer", "gramar", "gramma"],
    "heart": ["hart", "hert", "heort"], "height": ["hight", "heighth", "heigt"],
    "learn": ["lern", "larn", "leorn"], "material": ["materiel", "matirial", "materal"],
    "natural": ["naturel", "natrual", "naturral"], "ordinary": ["ordinry", "ordanary", "ordinery"],
    "possess": ["posess", "posses", "poses"], "promise": ["promis", "promiss", "promus"],
    "quarter": ["quater", "quartar", "qarter"], "straight": ["striaght", "straght", "strait"],
    "strength": ["strenght", "strengh", "strenth"], "woman": ["womin", "wuman", "womun"],
    # L5 / Year 5-6 statutory-list words (harder)
    "separate": ["seperate", "seperite", "separat"], "necessary": ["neccessary", "necesary", "nessecary"],
    "tomorrow": ["tommorow", "tomorow", "tommorrow"], "business": ["buisness", "bussiness", "busness"],
    "surprise": ["suprise", "surprize", "suprize"], "weird": ["wierd", "weerd", "wiered"],
    "rhythm": ["rythm", "rhythem", "rythem"], "accommodate": ["acommodate", "accomodate", "acomodate"],
    "conscience": ["conscence", "concience", "consciense"], "conscious": ["concious", "conscous", "conshus"],
    "definite": ["definate", "definit", "defenite"], "embarrass": ["embarass", "embaras", "embarras"],
    "environment": ["enviroment", "envirnoment", "enviornment"], "exaggerate": ["exagerate", "exaggrate", "exagurate"],
    "immediately": ["immediatly", "imediately", "imediatly"], "occurrence": ["occurence", "occurance", "ocurrence"],
    "parliament": ["parliment", "parlaiment", "parlement"], "privilege": ["priviledge", "privelege", "privalege"],
    "recommend": ["recomend", "reccomend", "reccommend"], "rhyme": ["rhym", "rime", "ryme"],
    "sincerely": ["sincerly", "sincerley", "sinserely"], "vehicle": ["vehical", "veicle", "vehcile"],
    "committee": ["commitee", "comittee", "committe"], "mischievous": ["mischievious", "mischevous", "mischivous"],
    "nuisance": ["nuisanse", "nusiance", "nuisence"], "sufficient": ["sufficiant", "suficient", "sufficent"]}
# difficulty: L3 (Year 3-4) vs L5 (Year 5-6)
SPELLING_L5 = {"separate", "necessary", "tomorrow", "business", "surprise", "weird", "rhythm",
               "accommodate", "conscience", "conscious", "definite", "embarrass", "environment",
               "exaggerate", "immediately", "occurrence", "parliament", "privilege", "recommend",
               "rhyme", "sincerely", "vehicle", "committee", "mischievous", "nuisance", "sufficient"}
# the authoritative "real words": the correct spellings AND their US/UK variants, so
# an item that offers both a UK and a US spelling is caught as having two valid answers.
VALID_WORDS = set(SPELLING) | set(SPELLING_VARIANTS) | set(SPELLING_VARIANTS.values())


def gen_spelling(rng, level=None):
    if level and level >= 3:
        pool = [w for w in SPELLING if w in SPELLING_L5]       # Year 5-6 harder words
    elif level == 2:
        pool = [w for w in SPELLING if w not in SPELLING_L5]   # Year 3-4 words
    else:
        pool = list(SPELLING)
    correct = rng.choice(pool)
    opts = [correct] + list(SPELLING[correct])[:3]
    rng.shuffle(opts)
    return _mcq("Which word is spelt correctly?", opts, correct,
                f"The correct spelling is “{correct}”.", "spelling", word=correct)


def check_spelling(it):
    # independent: exactly one option is a real (vetted) word, and it is the marked one
    valid = [o for o in it["options"] if o.strip() in VALID_WORDS]
    marked = it["options"][ord(it["answer"]) - 65] if len(it["answer"]) == 1 else None
    return len(set(it["options"])) == 4 and valid == [marked]


# =========================================================================
# 6) SUBJECT-VERB AGREEMENT — fixed sentences
# =========================================================================
# (sentence, correct verb, [three real distractor forms: wrong number, past, continuous])
AGREEMENT = [
    ("The dog ___ in the garden.", "runs", ["run", "ran", "running"]),
    ("The dogs ___ in the garden.", "run", ["runs", "ran", "running"]),
    ("She ___ to school every day.", "walks", ["walk", "walked", "walking"]),
    ("They ___ to school every day.", "walk", ["walks", "walked", "walking"]),
    ("The bird ___ in the tree.", "sings", ["sing", "sang", "singing"]),
    ("The birds ___ in the tree.", "sing", ["sings", "sang", "singing"]),
    ("My brother ___ football.", "likes", ["like", "liked", "liking"]),
    ("My brothers ___ football.", "like", ["likes", "liked", "liking"]),
    ("The baby ___ loudly.", "cries", ["cry", "cried", "crying"]),
    ("The babies ___ loudly.", "cry", ["cries", "cried", "crying"]),
    ("He ___ a big house.", "has", ["have", "had", "having"]),
    ("We ___ a big house.", "have", ["has", "had", "having"]),
    ("The child ___ happy.", "is", ["are", "was", "being"]),
    ("The children ___ happy.", "are", ["is", "was", "being"]),
    ("The cat ___ on the mat.", "sits", ["sit", "sat", "sitting"]),
    ("The cats ___ on the mat.", "sit", ["sits", "sat", "sitting"]),
    ("My sister ___ the piano.", "plays", ["play", "played", "playing"]),
    ("My sisters ___ the piano.", "play", ["plays", "played", "playing"]),
    ("The teacher ___ at the board.", "points", ["point", "pointed", "pointing"]),
    ("The teachers ___ at the board.", "point", ["points", "pointed", "pointing"]),
    ("That boy ___ very fast.", "swims", ["swim", "swam", "swimming"]),
    ("Those boys ___ very fast.", "swim", ["swims", "swam", "swimming"]),
    ("The flower ___ in the sun.", "grows", ["grow", "grew", "growing"]),
    ("The flowers ___ in the sun.", "grow", ["grows", "grew", "growing"]),
]
_AGREE = {a[0]: a[1] for a in AGREEMENT}
_AGREE_DISTRACT = {a[0]: a[2] for a in AGREEMENT}


def gen_agreement(rng, level=None):
    sent, correct, distract = rng.choice(AGREEMENT)
    opts = [correct] + list(distract)[:3]
    if len(set(opts)) != 4:
        return None
    rng.shuffle(opts)
    return _mcq(sent, opts, correct, f"The correct verb here is “{correct}”.",
                "agreement", sentence=sent)


def check_agreement(it):
    sent = it["_check"]["sentence"]
    # collective-noun subjects take a singular OR plural verb (British English) -> no
    # single answer, so such items are excluded (never served).
    if any(w in COLLECTIVE_NOUNS for w in sent.lower().replace(".", "").split()):
        return False
    correct = _AGREE.get(sent)
    return _unique_correct(it, correct, valid={correct} if correct else set())


# =========================================================================
# 7) PAST TENSE — regular rules + irregular list
# =========================================================================
IRREGULAR_PAST = {"go": "went", "run": "ran", "eat": "ate", "see": "saw", "take": "took",
                  "make": "made", "come": "came", "give": "gave", "find": "found",
                  "think": "thought", "buy": "bought", "catch": "caught", "teach": "taught",
                  "swim": "swam", "sing": "sang", "write": "wrote", "ride": "rode", "fly": "flew"}
REGULAR_VERBS = ["walk", "jump", "play", "talk", "look", "open", "clean", "help", "call",
                 "paint", "wash", "cook", "watch", "want", "need", "start", "finish"]


def _past_of(v):
    if v in IRREGULAR_PAST:
        return IRREGULAR_PAST[v]
    if v.endswith("e"):
        return v + "d"
    if v.endswith("y") and v[-2] not in "aeiou":
        return v[:-1] + "ied"
    return v + "ed"


def gen_tense(rng, level=None):
    v = rng.choice(REGULAR_VERBS + list(IRREGULAR_PAST))
    correct = _past_of(v)
    wrong = {v + "ed", v + "d", v, v + "t"}
    wrong.discard(correct)
    opts = [correct] + list(wrong)[:3]
    opts = list(dict.fromkeys(opts))[:4]
    if len(opts) < 4:
        return None
    rng.shuffle(opts)
    return _mcq(f"Yesterday, I ___ . (choose the past tense of “{v}”)", opts, correct,
                f"The past tense of “{v}” is “{correct}”.", "tense", verb=v)


def check_tense(it):
    correct = _past_of(it["_check"]["verb"])
    return _unique_correct(it, correct, valid={correct})


# =========================================================================
# 8) END PUNCTUATION — statement/question/exclamation
# =========================================================================
PUNCT = [("What time is it", "?"), ("Where are you going", "?"), ("How old are you", "?"),
         ("I like apples", "."), ("The sky is blue", "."), ("We went to the park", "."),
         ("Watch out", "!"), ("What a lovely day", "!"), ("Be careful", "!"),
         ("Is it raining", "?"), ("She has a cat", "."), ("Help me", "!"),
         ("Why is the dog barking", "?"), ("Who left the door open", "?"), ("Can you swim", "?"),
         ("My name is Sam", "."), ("The cake is in the oven", "."), ("Birds can fly", "."),
         ("Look at that", "!"), ("Stop right now", "!"), ("How wonderful", "!"),
         ("Do you like reading", "?"), ("What is your favourite colour", "?"),
         ("We are having pizza tonight", "."), ("The train leaves at noon", "."),
         ("Hurry up", "!"), ("That was amazing", "!"), ("Which way do we go", "?")]
_PUNCT = {p[0]: p[1] for p in PUNCT}


def gen_punct(rng, level=None):
    sent, correct = rng.choice(PUNCT)
    opts = [".", "?", "!", ","]
    rng.shuffle(opts)
    return _mcq(f"Which punctuation mark should end this sentence?  “{sent}”", opts, correct,
                f"This sentence should end with “{correct}”.", "punct", sentence=sent)


def check_punct(it):
    correct = _PUNCT.get(it["_check"]["sentence"])
    return _unique_correct(it, correct, valid={correct})


# =========================================================================
# shared helpers + registry
# =========================================================================
def _mcq(question, opts, correct, expl, kind, **check):
    check["kind"] = kind
    return {"question": question, "options": opts, "answer": chr(65 + opts.index(correct)),
            "explanation": expl, "_check": check}


def _unique_correct(it, correct, valid):
    """True iff options are 4 distinct, the marked one equals `correct`, and no OTHER
    option is in the `valid` set (no second correct answer)."""
    opts = it["options"]
    if correct is None or len(set(opts)) != len(opts) or len(opts) < 2:
        return False
    if correct not in opts:
        return False
    marked = opts[ord(it["answer"]) - 65] if len(it["answer"]) == 1 else None
    if marked != correct:
        return False
    return [o for o in opts if o in valid] == [correct]


TYPES = {
    "homophone": (gen_homophone, check_homophone),
    "plural": (gen_plural, check_plural),
    "contraction": (gen_contraction, check_contraction),
    "affix": (gen_affix, check_affix),
    "spelling": (gen_spelling, check_spelling),
    "agreement": (gen_agreement, check_agreement),
    "tense": (gen_tense, check_tense),
    "punct": (gen_punct, check_punct),
}


def generate(kind, n, seed, level=None):
    rng = random.Random(seed)
    gen, _ = TYPES[kind]
    out, guard = [], 0
    while len(out) < n and guard < n * 50:
        guard += 1
        it = gen(rng, level)
        if it is not None:
            out.append(it)
    return out


if __name__ == "__main__":
    for kind in TYPES:
        items = generate(kind, 200, 1)
        _, check = TYPES[kind]
        clean = sum(check(it) for it in items)
        print(f"{kind:12} built {len(items):3}  clean {clean}/{len(items)}")
