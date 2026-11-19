"""Mastery state model — shared by the engine and the UI so the Parent
dashboard, the map rings and the finish screen all agree.

A topic's state is derived from accumulated performance. **"Mastered" is
deliberately hard**: it needs sustained high accuracy on unseen questions across
MULTIPLE sessions — never from a single good session. Bands (parent spec):

    Not started            — nothing attempted
    Learning     (< 60%)
    Developing   (60–74%)
    Secure       (75–84%)
    Strong       (85–89%, and any single 90%+ session until mastery is earned)
    Mastered     (90%+ across >= 2 sessions on enough unseen questions)
"""
from __future__ import annotations

# weakest -> strongest
STATES = ["Not started", "Learning", "Developing", "Secure", "Strong", "Mastered"]

# UI colours live with the model so the legend, heatmap cells and rings match.
STATE_COLOUR = {
    "Not started": "#5a6b73",
    "Learning":    "#ff7a5c",
    "Developing":  "#ffb24a",
    "Secure":      "#ffe06a",
    "Strong":      "#8fd36a",
    "Mastered":    "#36c26a",
}

# cross-session Mastered rule
MASTER_MIN_SESSIONS = 2
MASTER_MIN_ATTEMPTS = 10
MASTER_MIN_PCT = 90.0


def pct(correct: int, attempts: int) -> float:
    return (100.0 * correct / attempts) if attempts else 0.0


def is_mastered(attempts: int, correct: int, sessions: int) -> bool:
    """True only for 90%+ accuracy sustained across >= 2 sessions on >= 10 items."""
    return (sessions >= MASTER_MIN_SESSIONS
            and attempts >= MASTER_MIN_ATTEMPTS
            and pct(correct, attempts) >= MASTER_MIN_PCT)


def mastery_state(attempts: int, correct: int, sessions: int = 0) -> str:
    """Return one of STATES. 90%+ in a single session caps at 'Strong'."""
    attempts = max(0, int(attempts))
    correct = max(0, min(int(correct), attempts))
    sessions = max(0, int(sessions))
    if attempts == 0:
        return "Not started"
    if is_mastered(attempts, correct, sessions):
        return "Mastered"
    p = pct(correct, attempts)
    if p < 60:
        return "Learning"
    if p < 75:
        return "Developing"
    if p < 85:
        return "Secure"
    return "Strong"
