#!/usr/bin/env python3
"""Flesch-Kincaid grade level — a rough readability check for lesson/question text
(spec section 6: write for ages 7-9 in the early ages). Not exact, but good enough
to flag text that is too hard for the age band."""
import re

_VOWELS = re.compile(r"[aeiouy]+")
_WORD = re.compile(r"[A-Za-z']+")


def _syllables(word: str) -> int:
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    n = len(_VOWELS.findall(w))
    if w.endswith("e") and n > 1:
        n -= 1
    return max(1, n)


def fk_grade(text: str) -> float:
    text = re.sub(r"[*#`_>|\-]", " ", text)          # drop markdown
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    words = _WORD.findall(text)
    if not sentences or not words:
        return 0.0
    syl = sum(_syllables(w) for w in words)
    return 0.39 * (len(words) / len(sentences)) + 11.8 * (syl / len(words)) - 15.59
