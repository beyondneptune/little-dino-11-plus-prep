"""Zero-rejection regression: over a LARGE sample (5000 per subject = 20,000
questions) the fixed generators must have ZERO rejections from their independent
testers. A single rejection means a new bug. (Against the OLD code the review
found 88/3000 Maths, 700/3000 English and 211/400 cube-net failures.)"""
import random

import english_gen as E
import maths_gen as M
import nvr_3d as NVR
import testers as T
import vr_gen as V


def _maths_items(n, seed):
    rng = random.Random(seed); items = []
    for i in range(n):
        if i % 15 == 14:
            topic, q, opts, idx, expl = M.g_primes(rng)
        else:
            topic, q, ans, wrongs, expl = rng.choice(M.GENS)(rng)
            opts, idx = M.mcq(ans, wrongs, rng)
        items.append({"question": q, "options": opts, "answer": chr(65 + idx)})
    return items


def _nvr_items(n, seed):
    rng = random.Random(seed); items = []
    names = [x for x in NVR.NETS if NVR.fold_face_ids(NVR.NETS[x])]
    for i in range(n):
        if i % 2 == 0:
            name = rng.choice(names)
            syms, opts, idx = NVR.make_net_question(NVR.NETS[name], seed * 97 + i)
            items.append({"_check": {"kind": "cube_net", "cells": NVR.NETS[name],
                                     "syms": syms, "opts": opts, "idx": idx}})
        else:
            assign, ref, opts, idx = NVR.make_rotation_question_full(seed * 97 + i)
            items.append({"_check": {"kind": "cube_rotation", "assign": assign,
                                     "ref": ref, "opts": opts, "idx": idx}})
    return items


def test_maths_all_pass():
    ok, tot = T.test_maths(_maths_items(5000, 1))
    assert ok == tot, f"{tot - ok} Maths items failed their tester"


def test_vr_all_pass():
    ok, tot = T.test_vr(V.generate(5000, 1))
    assert ok == tot, f"{tot - ok} VR items failed their tester"


def test_english_all_pass():
    ok, tot = T.test_english(E.generate(5000, 1))
    assert ok == tot, f"{tot - ok} English items failed their tester"


def test_nvr_all_pass():
    ok, tot = T.test_nvr(_nvr_items(5000, 1))
    assert ok == tot, f"{tot - ok} NVR items failed their tester"
