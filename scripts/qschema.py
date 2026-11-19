#!/usr/bin/env python3
"""
Typed question record + serve gate (brief 5a; AUTONOMOUS_PROMPT section 4/5).

The serve gate is the single chokepoint that enforces the #1 rule: a child only
ever sees an item that passed every verification check. `Question.servable()` is
the gate; `serve_or_none()` is the only sanctioned way to hand an item to the UI.

No third-party dependency (stdlib dataclasses) so the app runs with the network
blocked. Every field needed to REPRODUCE an item is stored (generator + version
+ seed), per brief 5g.3.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import Enum

SCHEMA_VERSION = 1
# reading-level ceiling for the early ages (ages 7-9 readers). Items above this
# are not served to early-age children (checked by the language pipeline).
EARLY_AGE_READING_GRADE_MAX = 6.0


class Status(str, Enum):
    draft = "draft"                # just generated/authored, not yet checked
    auto_approved = "auto_approved"  # passed every verification check -> servable
    rejected = "rejected"          # failed a check -> never served
    not_served = "not_served"      # deliberately withheld (e.g. type below threshold)


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class VerificationRecord:
    method: str                    # "computable" | "language"
    verifier_version: int
    checks: list[Check] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return bool(self.checks) and all(c.passed for c in self.checks)

    def failed_checks(self) -> list[str]:
        return [c.name for c in self.checks if not c.passed]


@dataclass
class Question:
    id: str
    topic_id: str
    qtype: str
    level: int                     # 1-5
    generator: str
    generator_version: int
    seed: int
    stem: str
    options: list[str]
    answer_index: int
    explanation: str
    distractor_explanations: list[str] = field(default_factory=list)
    reading_grade: float | None = None
    status: str = Status.draft.value
    verification: VerificationRecord | None = None
    schema_version: int = SCHEMA_VERSION

    # ---- the serve gate -----------------------------------------------------
    def servable(self) -> bool:
        """True ONLY if this item is safe to show a child. Structural sanity is
        re-checked here so a tampered record can never slip through."""
        if self.status != Status.auto_approved.value:
            return False
        if self.verification is None or not self.verification.ok:
            return False
        if not (1 <= int(self.level) <= 5):
            return False
        opts = self.options
        if len(opts) < 2 or len(opts) != len(set(opts)):
            return False
        if not (0 <= self.answer_index < len(opts)):
            return False
        if len(self.distractor_explanations) not in (0, len(opts) - 1, len(opts)):
            return False
        return True

    def content_hash(self) -> str:
        payload = json.dumps([self.stem, self.options, self.answer_index],
                             ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> dict:
        d = asdict(self)
        if isinstance(self.status, Status):
            d["status"] = self.status.value
        return d


class ServeError(RuntimeError):
    pass


def serve_or_none(q: Question) -> Question | None:
    """The ONLY sanctioned path to the UI. Returns the item if servable, else None."""
    return q if q.servable() else None


def serve_strict(q: Question) -> Question:
    """Like serve_or_none but raises — used where a caller believes an item is
    verified and a non-servable item means a bug upstream."""
    if not q.servable():
        reason = "not auto_approved" if q.status != Status.auto_approved.value else (
            "verification not ok: " + ",".join(
                q.verification.failed_checks() if q.verification else ["no record"]))
        raise ServeError(f"refusing to serve {q.id}: {reason}")
    return q
