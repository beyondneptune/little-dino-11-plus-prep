#!/usr/bin/env python3
"""
Verbal Reasoning generator (original items). Rule-based types carry structured
params in `_check` so the tester can INDEPENDENTLY re-derive the answer (a
different code path from the generator), plus an original vocabulary bank for
word types. Every item: type, question, 4 options, answer letter, explanation.
"""
import random
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vocab import CATS, SYN, ANT, same_meaning, opposite_of  # noqa: E402

AL = string.ascii_uppercase
ALLWORDS = [w for ws in CATS.values() for w in ws] + \
           [w for p in SYN + ANT for w in p]


def mcq(correct, wrongs, rng):
    opts = [str(correct)]
    for w in wrongs:
        s = str(w)
        if s != str(correct) and s not in opts:
            opts.append(s)
    while len(opts) < 4:
        opts.append(str(correct) + "_" * len(opts))
    opts = opts[:4]
    rng.shuffle(opts)
    return opts, chr(65 + opts.index(str(correct)))


def g_letter_series(rng):
    step = rng.choice([1, 2, 3, 4, -1, -2]); start = rng.randint(2, 15)
    seq = [AL[(start + step * i) % 26] for i in range(4)]
    ans = AL[(start + step * 4) % 26]
    opts, a = mcq(ans, [AL[(start + step * 4 + d) % 26] for d in (1, -1, 2)], rng)
    return {"type": "letter_series", "question": f"Find the next letter: {' '.join(seq)} ?",
            "options": opts, "answer": a, "explanation": f"Each letter moves {step:+d}.",
            "_check": {"kind": "letter_series", "seq": seq, "ans": ans}}


def g_number_series(rng):
    start = rng.randint(1, 9); step = rng.choice([2, 3, 4, 5, 6])
    seq = [start + step * i for i in range(4)]; ans = start + step * 4
    opts, a = mcq(ans, [ans + step, ans - 1, ans + 1], rng)
    return {"type": "number_series", "question": f"Find the next number: {', '.join(map(str,seq))}, ?",
            "options": opts, "answer": a, "explanation": f"Add {step} each time.",
            "_check": {"kind": "number_series", "seq": seq, "ans": ans}}


def g_letters_for_numbers(rng):
    # Use letters from later in the alphabet so they never clash with the
    # answer labels A-D.
    letters = sorted(rng.sample("LMNPRSTVWXYZ", 5))
    vals = sorted(rng.sample(range(2, 13), 5)); amap = dict(zip(letters, vals))
    x, y = rng.sample(letters, 2)
    if rng.random() < 0.5:
        res, op = amap[x] + amap[y], "+"
    else:
        if amap[x] < amap[y]:
            x, y = y, x
        res, op = amap[x] - amap[y], "−"
    code = ", ".join(f"{k}={v}" for k, v in amap.items())
    opts, a = mcq(res, [w for w in (res + 1, res - 1, res + 2) if w > 0] or [res + 3], rng)
    return {"type": "letters_for_numbers", "question": f"If {code}, work out {x} {op} {y}.",
            "options": opts, "answer": a, "explanation": f"{x}{op}{y} = {amap[x]}{op}{amap[y]} = {res}.",
            "_check": {"kind": "letters_for_numbers", "amap": amap, "x": x, "y": y, "op": op, "ans": res}}


def g_letter_code(rng):
    shift = rng.choice([1, 2, 3, -1, -2])
    w1 = rng.choice(["CAT", "DOG", "SUN", "BOX", "PEN", "CUP", "MAP", "BUS"])
    sample = rng.choice([w for w in ["LAMP", "FROG", "STAR", "DESK", "RING", "FISH"] if w != w1])

    def enc(w):
        return "".join(AL[(AL.index(c) + shift) % 26] for c in w)

    ans = enc(sample)
    opts, a = mcq(ans, [enc(sample).replace(ans[0], AL[(AL.index(ans[0]) + 1) % 26], 1),
                        enc(sample[::-1]), ans[:-1] + AL[(AL.index(ans[-1]) + 1) % 26]], rng)
    return {"type": "letter_code", "question": f"If {w1} is coded as {enc(w1)}, how is {sample} coded?",
            "options": opts, "answer": a, "explanation": f"Each letter shifts {shift:+d}.",
            "_check": {"kind": "letter_code", "w1": w1, "c1": enc(w1), "sample": sample, "ans": ans}}


def g_odd_word(rng):
    c1, c2 = rng.sample(list(CATS), 2)
    three = rng.sample(CATS[c1], 3); odd = rng.choice(CATS[c2])
    opts, a = mcq(odd, three, rng)
    return {"type": "odd_word", "question": "Which word is the odd one out?",
            "options": opts, "answer": a, "explanation": f"'{odd}' is a {c2}; the rest are {c1}s.",
            "_check": {"kind": "odd_word", "odd": odd, "c1": c1, "c2": c2, "three": three}}


def g_word_analogy(rng):
    kind = rng.choice(["syn", "ant"]); pairs = SYN if kind == "syn" else ANT
    (a1, b1), (c1, d1) = rng.sample(pairs, 2)
    if kind == "syn":       # no distractor may also mean the same as c1
        pool = [w for w in ALLWORDS if not same_meaning(w, c1) and not same_meaning(w, d1)]
    else:                   # no distractor may also be an opposite of c1
        pool = [w for w in ALLWORDS if w != c1 and not same_meaning(w, d1)
                and not opposite_of(c1, w)]
    distract = rng.sample(sorted(set(pool)), 3)
    opts, a = mcq(d1, distract, rng)
    return {"type": "word_analogy", "question": f"{a1} is to {b1} as {c1} is to …?",
            "options": opts, "answer": a,
            "explanation": f"{a1}/{b1} are {'synonyms' if kind=='syn' else 'antonyms'}; so are {c1}/{d1}.",
            "_check": {"kind": "word_analogy", "pair": [c1, d1], "rel": kind}}


GENS = [g_letter_series, g_number_series, g_letters_for_numbers, g_letter_code,
        g_odd_word, g_word_analogy]
# Real VR papers are vocabulary-heavy, so weight the word-based types higher.
WEIGHTS = [1, 1, 1, 1, 3, 3]


def generate(n=60, seed=11):
    rng = random.Random(seed)
    return [rng.choices(GENS, weights=WEIGHTS, k=1)[0](rng) for _ in range(n)]


if __name__ == "__main__":
    for it in generate(6):
        print(it["type"], "|", it["question"], "|", it["options"], "->", it["answer"])
