#!/usr/bin/env python3
"""
English (SPaG + vocabulary) generator. Original authored banks. Honest note:
English answers cannot be proven by code. The tester checks the key AND
checks for the known ways a second answer could also be right (same-meaning
distractors, real-word misspellings, alternative tenses). That catches the
common faults but is not a proof, so a parent spot-check is still advised.
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vocab                               # noqa: E402  graded 11+ vocabulary

# correct spelling -> common misspellings (authored). Every misspelling has
# been checked by hand to make sure it is NOT itself a real English word
# (e.g. "defiantly" and "surprize" were removed for that reason).
SPELL = {
    "necessary": ["neccessary", "necesary", "nessecary"],
    "separate": ["seperate", "seperete", "sepparate"],
    "definitely": ["definately", "definitly", "definatly"],
    "beautiful": ["beutiful", "beautifull", "beatiful"],
    "friend": ["freind", "frend", "friendt"],
    "believe": ["beleive", "belive", "believ"],
    "address": ["adress", "addres", "adddress"],
    "tomorrow": ["tommorow", "tomorow", "tommorrow"],
    "because": ["becuase", "becasue", "becouse"],
    "surprise": ["suprise", "suprize", "surpise"],
    "embarrass": ["embaras", "embarass", "embarres"],
    "rhythm": ["rythm", "rhythem", "rhytm"],
    # Year 5-6 statutory word list
    "accommodate": ["accomodate", "acommodate", "accommadate"],
    "achieve": ["acheive", "achive", "acheeve"],
    "aggressive": ["agressive", "aggresive", "agresive"],
    "amateur": ["amatuer", "amature", "ammateur"],
    "ancient": ["anceint", "ancent", "anshent"],
    "apparent": ["apparant", "aparent", "apparrent"],
    "conscience": ["concience", "consciense", "conshience"],
    "environment": ["enviroment", "environmint", "envirnoment"],
    "exaggerate": ["exagerate", "exaggarate", "exxagerate"],
    "government": ["goverment", "govenment", "governmant"],
    "immediately": ["immediatly", "imediately", "immediatley"],
    "interrupt": ["interupt", "interrup", "intterupt"],
    "parliament": ["parliment", "parlament", "parlaiment"],
    "privilege": ["priviledge", "privelege", "privilige"],
    "recommend": ["reccomend", "recomend", "reccommend"],
    "sincerely": ["sincerly", "sincerley", "sinserely"],
    "vehicle": ["vehical", "vehicel", "veicle"],
    "yacht": ["yaht", "yatch", "yaght"],
    "sufficient": ["sufficent", "suficient", "sufficiant"],
    "guarantee": ["garantee", "guarentee", "guarrantee"],
    "thorough": ["thurough", "thorogh", "thourough"],
}
SYN = dict(vocab.SYN)
ANT = dict(vocab.ANT)
ALLWORDS = sorted(set(SYN.values()) | set(ANT.values()) | set(SYN) | set(ANT))
# cloze: (sentence with ___, correct, distractors). Distractors chosen so that
# none of them also makes sense in the sentence.
CLOZE = [
    ("The sun was so bright that she had to ___ her eyes.", "shield", ["shed", "shelf", "shout"]),
    ("He ran quickly ___ he was late for school.", "because", ["although", "unless", "despite"]),
    ("The ancient castle stood on top of a steep ___.", "hill", ["bill", "mill", "pill"]),
    ("She spoke in a ___ voice so no one could hear.", "whisper", ["shout", "roar", "bellow"]),
    ("The recipe needs a ___ of salt.", "pinch", ["punch", "bench", "branch"]),
    ("After the long walk, the hikers were ___ and sat down to rest.", "exhausted", ["energetic", "lively", "speedy"]),
    ("The library was so ___ that you could hear a pin drop.", "silent", ["noisy", "crowded", "busy"]),
    ("She was ___ of spiders, so she screamed when she saw one.", "terrified", ["fond", "proud", "careless"]),
    ("The detective ___ the clues carefully before solving the mystery.", "examined", ["ignored", "forgot", "lost"]),
    ("The ___ of the mountain was covered in snow.", "summit", ["harbour", "basement", "pavement"]),
    ("Tom felt ___ when he won first prize.", "delighted", ["disappointed", "ashamed", "bored"]),
    ("The ancient vase was so ___ that we handled it with great care.", "fragile", ["sturdy", "durable", "cheap"]),
    ("We could not see the road ___ the thick fog.", "through", ["across", "beside", "after"]),
    ("The children waited ___ for the show to begin.", "eagerly", ["eager", "eagerness", "eagered"]),
    ("Neither the teacher ___ the pupils knew the answer.", "nor", ["or", "and", "but"]),
]
# grammar: (sentence with ___, correct, distractors). Each distractor is
# ungrammatical in the sentence (no alternative tenses that would also fit).
GRAMMAR = [
    ("The box of pencils ___ on the desk.", "is", ["are", "were", "be"]),
    ("Each of the children ___ a packed lunch.", "has", ["have", "having", "are having"]),
    ("My brother and I ___ going to the park.", "are", ["is", "am", "was"]),
    ("The flowers in the garden ___ beautiful.", "look", ["looks", "looking", "has looked"]),
    ("One of my friends ___ a pet snake.", "has", ["have", "having", "are having"]),
    ("Yesterday, the children ___ to the museum.", "went", ["go", "goes", "going"]),
    ("By the time we arrived, the film ___ already started.", "had", ["has", "have", "having"]),
    ("She ___ her bike to school every day.", "rides", ["ride", "riding", "ridden"]),
    ("Last summer we ___ in a tent by the lake.", "slept", ["sleep", "sleeps", "sleeping"]),
    ("Tomorrow, the class ___ visit the castle.", "will", ["did", "has", "was"]),
    ("The cakes that Mum baked ___ delicious.", "were", ["was", "is", "be"]),
]
# simple subject-verb agreement: (noun, singular_verb, plural_verb)
VERBS = [("dog", "barks", "bark"), ("child", "plays", "play"), ("bird", "sings", "sing"),
         ("teacher", "helps", "help"), ("clock", "ticks", "tick")]
PLURAL = {"dog": "dogs", "child": "children", "bird": "birds", "teacher": "teachers", "clock": "clocks"}


def mcq(correct, wrongs, rng):
    opts = [correct] + [w for w in wrongs if w != correct][:3]
    while len(opts) < 4:
        opts.append(correct + "_" * len(opts))
    opts = opts[:4]; rng.shuffle(opts)
    return opts, chr(65 + opts.index(correct))


def g_spelling(rng):
    word = rng.choice(list(SPELL))
    opts, a = mcq(word, SPELL[word], rng)
    return {"type": "spelling", "question": "Which word is spelt correctly?",
            "options": opts, "answer": a, "explanation": f"The correct spelling is '{word}'.",
            "_check": {"kind": "spelling", "correct": word}}


def g_synonym(rng):
    w = rng.choice(list(SYN)); ans = SYN[w]
    pool = [x for x in ALLWORDS if x != w and not vocab.same_meaning(x, w)
            and not vocab.same_meaning(x, ans)]
    opts, a = mcq(ans, rng.sample(pool, 3), rng)
    return {"type": "synonym", "question": f"Which word means the SAME as '{w}'?",
            "options": opts, "answer": a, "explanation": f"'{w}' means '{ans}'.",
            "_check": {"kind": "synonym", "w": w, "ans": ans}}


def g_antonym(rng):
    w = rng.choice(list(ANT)); ans = ANT[w]
    pool = [x for x in ALLWORDS if x != w and not vocab.same_meaning(x, ans)
            and not vocab.opposite_of(w, x)]
    opts, a = mcq(ans, rng.sample(pool, 3), rng)
    return {"type": "antonym", "question": f"Which word is the OPPOSITE of '{w}'?",
            "options": opts, "answer": a, "explanation": f"The opposite of '{w}' is '{ans}'.",
            "_check": {"kind": "antonym", "w": w, "ans": ans}}


def g_cloze(rng):
    s, ans, wrongs = rng.choice(CLOZE)
    opts, a = mcq(ans, list(wrongs), rng)
    return {"type": "cloze", "question": f"Choose the best word: {s}",
            "options": opts, "answer": a, "explanation": f"'{ans}' fits the sentence's meaning.",
            "_check": {"kind": "cloze", "ans": ans}}


def g_grammar(rng):
    if rng.random() < 0.5:                      # authored tense/agreement items
        sent, correct, wrongs = rng.choice(GRAMMAR)
        opts, a = mcq(correct, list(wrongs), rng)
        return {"type": "grammar", "question": f"Choose the correct word(s): {sent}",
                "options": opts, "answer": a,
                "explanation": f"'{correct}' is the only option that is grammatically correct here.",
                "_check": {"kind": "grammar", "correct": correct, "sentence": sent}}
    noun, sv, pv = rng.choice(VERBS)            # simple agreement, present tense
    plural = rng.random() < 0.5
    subj = f"The {PLURAL[noun]}" if plural else f"The {noun}"
    correct = pv if plural else sv
    wrong_aux = "is" if plural else "are"       # "The dogs is barking" / "The dog are barking"
    wrongs = [sv if plural else pv, pv + "ing" if not pv.endswith("e") else pv[:-1] + "ing",
              f"{wrong_aux} {pv}ing"]
    sent = f"{subj} ___ every day."
    opts, a = mcq(correct, wrongs, rng)
    return {"type": "grammar", "question": f"Choose the correct word(s): {sent}",
            "options": opts, "answer": a, "explanation": f"'{subj}' takes '{correct}'.",
            "_check": {"kind": "grammar_agree", "correct": correct, "plural": plural,
                       "sv": sv, "pv": pv}}


GENS = [g_spelling, g_synonym, g_antonym, g_cloze, g_grammar]


def generate(n=60, seed=13):
    rng = random.Random(seed)
    return [rng.choice(GENS)(rng) for _ in range(n)]


if __name__ == "__main__":
    for it in generate(6):
        print(it["type"], "|", it["question"], "|", it["options"], "->", it["answer"])
