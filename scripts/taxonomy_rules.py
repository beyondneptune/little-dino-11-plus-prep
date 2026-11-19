#!/usr/bin/env python3
"""
Shared rules for turning the master syllabus into the Dino Ages taxonomy.

Two INDEPENDENT per-topic tags (Phase 1b, stricter):

content_readiness — how a topic's QUESTIONS become safe for a child:
  V  fully computed   — the answer is derived by independent computation with no
                        judgement of language or meaning: arithmetic, sequences,
                        codes, shape/geometry models, constraint-solved logic,
                        word construction against a verified word list.
  R  authored+review  — anything that depends on judging language or meaning
                        (synonyms, antonyms, odd-one-out categories, grammar,
                        punctuation, spelling ambiguity, comprehension, cloze):
                        needs human-written text, a blind solve, and parent review.
  P  parent-marked    — open-ended / creative writing; a parent marks it.

verifier_status — whether an INDEPENDENT tester exists in scripts/testers.py
TODAY for that topic's question type (not whether a generator exists):
  built    — testers.py already re-solves/checks this type.
  to_build — no independent tester yet.

These are orthogonal: e.g. odd-one-out has a tester (built) but still judges word
meaning (R); most Maths is fully computed (V) but has no tester yet (to_build).
"""
from __future__ import annotations


def _section_letter(topic: dict) -> str | None:
    """'MA-C05' -> 'C'; 'ET-01' -> None."""
    tail = topic["id"].split("-", 1)[1]
    return tail[0] if tail[0].isalpha() else None


def content_readiness(topic: dict) -> str:
    subj = topic["subject"]
    sec = _section_letter(topic)

    if subj == "ET":
        return "P"

    if subj == "Maths":
        # Fully computed, EXCEPT statistics (needs an authored chart/table to read).
        return "R" if sec == "I" else "V"

    if subj == "English":
        # Judging language/meaning throughout; only creative writing is parent-marked.
        # (Grammar, punctuation and spelling are R: distractors turn on ambiguous
        #  language choices, so they need the blind-solve + review pipeline.)
        return "P" if sec == "H" else "R"

    if subj == "VR":
        # A = vocabulary reasoning (synonyms/antonyms/odd-one-out/analogies/
        # multiple-meaning) -> judges meaning -> R. B/C/D/E = word construction,
        # letter/number codes, constraint logic -> fully computed -> V.
        return "R" if sec == "A" else "V"

    if subj == "NVR":
        # Shape/geometry models, sequences, rotations, pattern constraints.
        return "V"

    return "R"


def verifier_status(topic: dict) -> str:
    """Derived from scripts/registry.py: a topic is 'built' iff a registered
    generator+independent solver pair covers it. Imported lazily so lightweight
    callers of content_readiness() don't pull in the generators."""
    from registry import registry_topics
    return "built" if topic["id"] in registry_topics() else "to_build"
