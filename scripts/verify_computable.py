#!/usr/bin/env python3
"""
Computable-item verification (brief 5a): turn a generated item into a Question
whose status is auto_approved ONLY if an INDEPENDENT solver (scripts/testers.py,
separate logic from the generators) agrees and the structure is sane.

The solver works from the rendered item, not the generator's internals. A failed
check leaves the item `rejected`, so the serve gate (qschema) will never show it.
"""
from __future__ import annotations

import testers as T
from qschema import Check, Question, Status, VerificationRecord

VERIFIER_VERSION = 1

# subject -> independent checker returning (ok: bool, reason: str)
def _solve(subject: str, it: dict) -> tuple[bool, str]:
    if subject == "maths":
        ok, reason = T.check_maths_item(it)
        return bool(ok), str(reason)
    if subject == "vr":
        return bool(T.check_vr_item(it)), ""
    if subject == "nvr":
        return bool(T.check_nvr_item(it)), ""
    if subject == "english":
        return bool(T.check_english_item(it)), ""
    return False, f"unknown subject {subject!r}"


def _options(it: dict) -> list:
    """Display options: text items use it['options']; visual items (NVR) use the
    view tuples under it['_check']['opts']."""
    if it.get("options") is not None:
        return list(it["options"])
    return list(it.get("_check", {}).get("opts", []))


def verify(subject: str, it: dict) -> VerificationRecord:
    opts = _options(it)
    checks = [
        Check("options_distinct",
              len(opts) >= 2 and len({str(o).strip() for o in opts}) == len(opts)),
        Check("answer_label_valid",
              isinstance(it.get("answer"), str) and len(it["answer"]) == 1
              and 0 <= ord(it["answer"]) - 65 < len(opts)),
    ]
    ok, reason = _solve(subject, it)
    checks.append(Check("independent_solver", ok, reason))
    # NVR's solver validates _check['idx'] (the geometrically real view) but does
    # not read the served answer letter; tie them so a wrong served key is caught.
    if subject == "nvr":
        marked = (ord(it["answer"]) - 65) if isinstance(it.get("answer"), str) \
            and len(it["answer"]) == 1 else -1
        idx = it.get("_check", {}).get("idx")
        checks.append(Check("answer_matches_solved", marked == idx,
                            f"marked {marked} vs solved {idx}"))
    return VerificationRecord(method="computable", verifier_version=VERIFIER_VERSION,
                             checks=checks)


def make_question(subject: str, it: dict, topic_id: str, qtype: str, level: int,
                  generator: str, generator_version: int, seed: int) -> Question:
    rec = verify(subject, it)
    idx = (ord(it["answer"]) - 65) if isinstance(it.get("answer"), str) \
        and len(it["answer"]) == 1 else -1
    q = Question(
        id="pending",
        topic_id=topic_id,
        qtype=qtype,
        level=level,
        generator=generator,
        generator_version=generator_version,
        seed=seed,
        stem=it.get("question", ""),
        options=[str(o) for o in _options(it)],
        answer_index=idx,
        explanation=it.get("explanation", ""),
        distractor_explanations=it.get("distractor_explanations", []),
        reading_grade=it.get("reading_grade"),
        status=(Status.auto_approved.value if rec.ok else Status.rejected.value),
        verification=rec,
    )
    q.id = f"{generator}:{seed}:{q.content_hash()}"
    return q
