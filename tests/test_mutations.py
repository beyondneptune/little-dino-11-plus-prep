"""
Mutation tests: plant each bug the independent review found (FIXES.md) and prove
the matching tester REJECTS it — with a control showing a clean item still passes
(so the tester is not trivially always-false). A tester that can't catch a
planted bug is broken.
"""
import itertools

import nvr_3d as NVR
import testers as T
import vocab


def _letter(opts, value):
    return chr(65 + opts.index(value))


# ---- 1. Maths: banker's rounding (round() rounds halves to even) ----
def test_catches_bankers_rounding():
    opts = ["5300", "5310", "5290", "5320"]        # 5305 -> 5310 (half up); banker's = 5300
    bad = {"question": "Round 5305 to the nearest 10.", "options": opts, "answer": _letter(opts, "5300")}
    assert T.check_maths_item(bad)[0] is False
    good = {"question": "Round 5305 to the nearest 10.", "options": opts, "answer": _letter(opts, "5310")}
    assert T.check_maths_item(good)[0] is True


# ---- 2. Maths: integer-division percentage (10% of 24 = 2.4, bug drops it to 2) ----
def test_catches_integer_division_percent():
    opts = ["2", "3", "4", "5"]
    bad = {"question": "Find 10% of 24.", "options": opts, "answer": _letter(opts, "2")}
    assert T.check_maths_item(bad)[0] is False     # true answer 2.4 is not even an option
    opts2 = ["3", "6", "2", "9"]
    good = {"question": "Find 10% of 30.", "options": opts2, "answer": _letter(opts2, "3")}
    assert T.check_maths_item(good)[0] is True


# ---- 3. Maths: negative change (pay less than the cost) ----
def test_catches_negative_change():
    opts = ["£-2.05", "£2.05", "£3.05", "£1.05"]
    bad = {"question": "A book costs £7.05. You pay with a £5 note. How much change?",
           "options": opts, "answer": _letter(opts, "£-2.05")}
    assert T.check_maths_item(bad)[0] is False
    opts2 = ["£0.95", "£1.05", "£0.85", "£0.90"]
    good = {"question": "A book costs £4.05. You pay with a £5 note. How much change?",
            "options": opts2, "answer": _letter(opts2, "£0.95")}
    assert T.check_maths_item(good)[0] is True


# ---- 4. English: two-correct grammar (an -ed past form is also grammatical) ----
def test_catches_two_correct_grammar():
    chk = {"kind": "grammar_agree", "correct": "barks", "plural": False, "sv": "barks", "pv": "bark"}
    q = "Choose the correct word(s): The dog ___ every day."
    opts = ["barks", "barked", "barking", "bark"]
    bad = {"_check": chk, "question": q, "options": opts, "answer": _letter(opts, "barks")}
    assert T.check_english_item(bad) is False
    opts2 = ["barks", "barking", "bark", "barkin"]
    good = {"_check": chk, "question": q, "options": opts2, "answer": _letter(opts2, "barks")}
    assert T.check_english_item(good) is True


# ---- 5. English: a real word offered as a misspelling ("defiantly") ----
def test_catches_real_word_misspelling():
    chk = {"kind": "spelling", "correct": "definitely"}
    q = "Which word is spelt correctly?"
    opts = ["definitely", "defiantly", "definately", "definitly"]
    bad = {"_check": chk, "question": q, "options": opts, "answer": _letter(opts, "definitely")}
    assert T.check_english_item(bad) is False
    opts2 = ["definitely", "definately", "definitly", "definatly"]
    good = {"_check": chk, "question": q, "options": opts2, "answer": _letter(opts2, "definitely")}
    assert T.check_english_item(good) is True


# ---- 6. VR / vocab: a distractor that also means the same (big ~ huge) ----
def test_catches_same_meaning_distractor():
    chk = {"kind": "word_analogy", "pair": ["big", "large"], "rel": "syn"}
    q = "small is to little as big is to …?"
    opts = ["large", "huge", "tiger", "oak"]        # both large AND huge mean big
    bad = {"_check": chk, "question": q, "options": opts, "answer": _letter(opts, "large")}
    assert T.check_vr_item(bad) is False
    opts2 = ["large", "tiger", "oak", "iron"]
    good = {"_check": chk, "question": q, "options": opts2, "answer": _letter(opts2, "large")}
    assert T.check_vr_item(good) is True


# ---- 7. NVR: a mirror-image cube marked as the correct folding ----
def _views(net_name="cross"):
    cells = list(NVR.NETS[net_name])
    syms = ["o", "s", "D", "P", "*", "X"]
    assign = T.fold_net_outside(cells, syms)
    normal_of = {s: n for n, s in assign.items()}
    real = [v for v in itertools.permutations(syms, 3) if T.is_real_view(v, normal_of)]
    V = real[0]
    M = (V[0], V[2], V[1])                           # swap left/right = mirror image
    assert not T.is_real_view(M, normal_of)
    non = [v for v in itertools.permutations(syms, 3)
           if not T.is_real_view(v, normal_of) and v != M][:2]
    return cells, syms, V, M, non


def test_catches_mirror_cube_net():
    cells, syms, V, M, non = _views()
    bad = {"_check": {"kind": "cube_net", "cells": cells, "syms": syms,
                      "opts": [M, V, non[0], non[1]], "idx": 0}}      # marked the mirror
    assert T.check_nvr_item(bad) is False
    good = {"_check": {"kind": "cube_net", "cells": cells, "syms": syms,
                       "opts": [V, M, non[0], non[1]], "idx": 0}}     # marked the real view
    assert T.check_nvr_item(good) is True


# ---- 8. VR: an odd-one-out word that belongs to two categories (silver = metal AND colour) ----
def test_catches_odd_word_in_two_categories(monkeypatch):
    cats = {k: list(v) for k, v in vocab.CATS.items()}
    cats["metal"].append("silver"); cats["colour"].append("silver")   # now in two categories
    monkeypatch.setattr(vocab, "CATS", cats)
    opts = ["silver", cats["metal"][0], cats["metal"][1], cats["colour"][0]]
    bad = {"_check": {"kind": "odd_word"}, "question": "Which word is the odd one out?",
           "options": opts, "answer": "D"}
    assert T.check_vr_item(bad) is False
    clean = [cats["animal"][0], cats["animal"][1], cats["animal"][2], cats["fruit"][0]]
    good = {"_check": {"kind": "odd_word"}, "options": clean, "answer": "D"}
    assert T.check_vr_item(good) is True


# ---- 9. VR: letters-for-numbers using A-D (clashes with the A-D answer labels) ----
def test_catches_letters_for_numbers_label_clash():
    opts = ["6", "7", "5", "8"]
    bad = {"_check": {"kind": "letters_for_numbers"},
           "question": "If A=2, B=4, C=6, D=8, E=10, work out A + B.",
           "options": opts, "answer": "A"}                           # letters A-D clash
    assert T.check_vr_item(bad) is False
    good = {"_check": {"kind": "letters_for_numbers"},
            "question": "If L=2, M=4, N=6, P=8, R=10, work out L + M.",
            "options": opts, "answer": "A"}                          # letters L-R, no clash
    assert T.check_vr_item(good) is True


# ---- 10. NVR: a cube-rotation option showing a face NOT visible on the reference cube ----
def test_catches_rotation_hidden_face():
    assign, ref, opts, idx = NVR.make_rotation_question_full(123)
    outside = next(iter(set(assign.values()) - set(ref)))            # a hidden face
    j = (idx + 1) % 4                                                # mutate a wrong option
    opts_bad = list(opts); opts_bad[j] = (ref[0], ref[1], outside)   # shows a hidden face
    bad = {"_check": {"kind": "cube_rotation", "assign": assign, "ref": ref,
                      "opts": opts_bad, "idx": idx}}
    assert T.check_nvr_item(bad) is False
    good = {"_check": {"kind": "cube_rotation", "assign": assign, "ref": ref,
                       "opts": list(opts), "idx": idx}}
    assert T.check_nvr_item(good) is True
