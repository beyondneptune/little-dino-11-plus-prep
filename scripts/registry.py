#!/usr/bin/env python3
"""
Generator+solver REGISTRY (parent STEP 1c). Each entry ties:
  - a topic id,
  - the subject whose INDEPENDENT solver (scripts/testers.py) checks it,
  - the difficulty levels the generator can actually produce,
  - a make(rng, level) -> item,
  - and a stem regex (maths) or a _check kind (vr/nvr/english) that links the
    question TEMPLATE to the topic it genuinely teaches.

verifier_status is DERIVED from this registry (not a hand-maintained set). The
build fails (tests/test_registry.py) if any entry's generator and solver disagree,
or a generated stem/kind does not match the topic it is registered under — which
is exactly how the earlier MA-B01 mislabel (a x b +- c order-of-operations served
under "mental arithmetic") is now caught.
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass, field

import age1_gen as A1
import age1_more as A1M
import english_gen as E
import maths_gen as M
import train_all as TA  # gen_nvr
import verify_computable as VC
import vr_gen as V


@dataclass
class Entry:
    topic: str
    subject: str                 # maths | vr | nvr | english
    qtype: str
    levels: list                 # difficulty levels the generator can produce
    make: object                 # (rng, level) -> item dict or None
    stem_re: str = None          # maths: question must fullmatch this
    kind: str = None             # vr/nvr/english: item['_check']['kind'] must equal this


# ---- make() wrappers --------------------------------------------------------
def _maths_fixed(g):
    def make(rng, level):
        _, q, ans, wrongs, expl = g(rng)
        try:
            opts, idx = M.mcq(ans, wrongs, rng)
        except ValueError:
            return None
        return {"question": q, "options": opts, "answer": chr(65 + idx),
                "explanation": expl, "_check": {"kind": "maths"}}
    return make


def _maths_leveled(g):
    def make(rng, level):
        q, ans, wrongs, expl = g(rng, level)
        try:
            opts, idx = M.mcq(ans, wrongs, rng)
        except ValueError:
            return None
        return {"question": q, "options": opts, "answer": chr(65 + idx),
                "explanation": expl, "_check": {"kind": "maths"}}
    return make


def _maths_primes():
    def make(rng, level):
        _, q, opts, idx, expl = M.g_primes(rng)
        return {"question": q, "options": opts, "answer": chr(65 + idx),
                "explanation": expl, "_check": {"kind": "maths"}}
    return make


def _kind_maker(batch, kind):
    def make(rng, level):
        for it in batch(rng.randint(1, 10 ** 9)):
            if it.get("_check", {}).get("kind") == kind:
                return it
        return None
    return make


_vr = lambda kind: _kind_maker(lambda s: V.generate(40, s), kind)
_en = lambda kind: _kind_maker(lambda s: E.generate(40, s), kind)
_nvr = lambda kind: _kind_maker(lambda s: TA.gen_nvr(20, s), kind)


# ---- the registry -----------------------------------------------------------
REGISTRY: list[Entry] = [
    # Maths — Age 1 foundation (level-aware, levels 1-2 single-step)
    Entry("MA-B01", "maths", "mental_single", [1, 2], _maths_leveled(A1.g_mental_single),
          stem_re=r"Work out \d+ [+\-−×÷] \d+"),
    Entry("MA-A05", "maths", "rounding", [1, 2], _maths_leveled(A1.g_round),
          stem_re=r"Round \d+ to the nearest (10|100)\."),
    Entry("MA-B04", "maths", "division_fact", [1, 2], _maths_leveled(A1.g_div_fact),
          stem_re=r"Work out \d+ ÷ \d+"),
    # Maths — Age 1 expansion (new computable generators + independent solvers)
    Entry("MA-A03", "maths", "compare_int", [1, 2], _maths_leveled(A1M.g_compare),
          stem_re=r"Which of these numbers is the (largest|smallest)\?"),
    Entry("MA-B13", "maths", "number_property", [1, 2], _maths_leveled(A1M.g_parity),
          stem_re=r"Which of these is an? .+\?"),
    Entry("MA-A07", "maths", "roman", [1, 2], _maths_leveled(A1M.g_roman),
          stem_re=r"What number does the Roman numeral [IVXLCDM]+ represent\?"),
    Entry("MA-B06", "maths", "missing_number", [1, 2], _maths_leveled(A1M.g_missing),
          stem_re=r"What number goes in the box\? \d+ [+×÷] \? = \d+"),
    # Maths — later-age templates (generator+solver exist; levels coarse = [3])
    Entry("MA-B05", "maths", "order_of_ops", [3], _maths_fixed(M.g_arithmetic),
          stem_re=r"Work out \d+ × \d+ [+−] \d+"),
    Entry("MA-B03", "maths", "long_mult", [3], _maths_fixed(M.g_long_mult),
          stem_re=r"Use long multiplication to work out \d+ × \d+\."),
    Entry("MA-B08", "maths", "primes", [3], _maths_primes(),
          stem_re=r"Which of these is a prime number\?"),
    Entry("MA-C08", "maths", "fraction_of", [3], _maths_fixed(M.g_fraction_of),
          stem_re=r"What is \d+/\d+ of \d+\?"),
    Entry("MA-C05", "maths", "fraction_add", [3], _maths_fixed(M.g_fraction_add),
          stem_re=r"Work out \d+/\d+ \+ \d+/\d+\. Give your answer in its simplest form\."),
    Entry("MA-D05", "maths", "percent_of", [3], _maths_fixed(M.g_percent_of),
          stem_re=r"Find \d+% of \d+\."),
    Entry("MA-D06", "maths", "percent_change", [3], _maths_fixed(M.g_percent_change),
          stem_re=r"A £\d+ item is reduced by \d+% in a sale\. What is the new price\?"),
    Entry("MA-D10", "maths", "ratio", [3], _maths_fixed(M.g_ratio),
          stem_re=r"£\d+ is shared in the ratio \d+:\d+\. What is the larger share\?"),
    Entry("MA-F07", "maths", "perimeter", [3], _maths_fixed(M.g_area_rect),
          stem_re=r"A rectangle is \d+ cm by \d+ cm\. What is its (area|perimeter)\?"),
    Entry("MA-F08", "maths", "area", [3], _maths_fixed(M.g_area_rect),
          stem_re=r"A rectangle is \d+ cm by \d+ cm\. What is its (area|perimeter)\?"),
    Entry("MA-F02", "maths", "convert_len", [3], _maths_fixed(M.g_convert),
          stem_re=r"Convert \d+(?:\.\d+)? metres into centimetres\."),
    Entry("MA-F11", "maths", "money_change", [3], _maths_fixed(M.g_money_change),
          stem_re=r"A book costs £\d+\.\d\d\. You pay with a £\d+ note\. How much change\?"),
    Entry("MA-G05", "maths", "triangle_angle", [3], _maths_fixed(M.g_triangle_angle),
          stem_re=r"Two angles in a triangle are \d+° and \d+°\. What is the third angle\?"),
    Entry("MA-E08", "maths", "sequence", [3], _maths_fixed(M.g_sequence),
          stem_re=r"What is the next term: [\d, ]+, …\?"),
    Entry("MA-I09", "maths", "mean", [3], _maths_fixed(M.g_mean),
          stem_re=r"Find the mean of: [\d, ]+\."),
    # VR — rule-based (kind links to topic)
    Entry("VR-C02", "vr", "letter_series", [2], _vr("letter_series"), kind="letter_series"),
    Entry("VR-D01", "vr", "number_series", [2], _vr("number_series"), kind="number_series"),
    Entry("VR-D05", "vr", "letters_for_numbers", [2], _vr("letters_for_numbers"), kind="letters_for_numbers"),
    Entry("VR-C06", "vr", "letter_code", [2], _vr("letter_code"), kind="letter_code"),
    Entry("VR-A05", "vr", "odd_word", [2], _vr("odd_word"), kind="odd_word"),
    Entry("VR-A07", "vr", "word_analogy", [2], _vr("word_analogy"), kind="word_analogy"),
    # NVR — cube nets + rotation
    Entry("NV-F01", "nvr", "cube_net", [2], _nvr("cube_net"), kind="cube_net"),
    Entry("NV-F04", "nvr", "cube_rotation", [2], _nvr("cube_rotation"), kind="cube_rotation"),
    # English — deterministic vocab/grammar/spelling (R: not auto-served, but a tester exists)
    Entry("EN-B01", "english", "synonym", [2], _en("synonym"), kind="synonym"),
    Entry("EN-B01", "english", "antonym", [2], _en("antonym"), kind="antonym"),
    Entry("EN-D07", "english", "grammar_agree", [2], _en("grammar_agree"), kind="grammar_agree"),
    Entry("EN-F02", "english", "spelling", [2], _en("spelling"), kind="spelling"),
]


def registry_topics() -> set:
    return {e.topic for e in REGISTRY}


def entries_for(topic: str) -> list:
    return [e for e in REGISTRY if e.topic == topic]


def levels_for(topic: str) -> list:
    return sorted({lvl for e in entries_for(topic) for lvl in e.levels})


def validate(per_level: int = 12) -> list[str]:
    """Generate items for every entry/level and prove generator+solver agree and
    the stem/kind matches the topic. Returns a list of problems (empty == healthy)."""
    issues = []
    for e in REGISTRY:
        for lvl in e.levels:
            rng = random.Random(hash((e.topic, e.qtype, lvl)) & 0xFFFFFFFF)
            got = tries = 0
            while got < per_level and tries < per_level * 80:
                tries += 1
                it = e.make(rng, lvl)
                if it is None:
                    continue
                got += 1
                q = VC.make_question(e.subject, it, e.topic, e.qtype, lvl,
                                     f"reg:{e.qtype}", 1, tries)
                if not q.servable():
                    issues.append(f"{e.topic}/{e.qtype} L{lvl}: not servable "
                                  f"({q.verification.failed_checks()})")
                    break
                if e.stem_re and not re.fullmatch(e.stem_re, it.get("question", "")):
                    issues.append(f"{e.topic}/{e.qtype} L{lvl}: stem "
                                  f"{it.get('question')!r} != /{e.stem_re}/")
                    break
                if e.kind and it.get("_check", {}).get("kind") != e.kind:
                    issues.append(f"{e.topic}/{e.qtype} L{lvl}: kind "
                                  f"{it.get('_check', {}).get('kind')!r} != {e.kind!r}")
                    break
            if got < per_level:
                issues.append(f"{e.topic}/{e.qtype} L{lvl}: only {got}/{per_level} produced")
    return issues


if __name__ == "__main__":
    probs = validate()
    print(f"registry: {len(REGISTRY)} entries, {len(registry_topics())} topics")
    print("ISSUES:", len(probs))
    for p in probs:
        print("  -", p)
