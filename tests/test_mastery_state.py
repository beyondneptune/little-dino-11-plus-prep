"""The mastery state function must match the parent-approved bands and must
NEVER report 'Mastered' from a single session."""
import mastery as M


def test_not_started():
    assert M.mastery_state(0, 0, 0) == "Not started"
    assert M.mastery_state(0, 0, 9) == "Not started"


def test_bands_by_percentage():
    # Learning < 60
    assert M.mastery_state(10, 5, 1) == "Learning"        # 50%
    assert M.mastery_state(10, 0, 1) == "Learning"
    # Developing 60-74
    assert M.mastery_state(10, 6, 1) == "Developing"      # 60%
    assert M.mastery_state(100, 74, 1) == "Developing"    # 74%
    # Secure 75-84
    assert M.mastery_state(100, 75, 1) == "Secure"
    assert M.mastery_state(100, 84, 1) == "Secure"
    # Strong 85-89
    assert M.mastery_state(100, 85, 1) == "Strong"
    assert M.mastery_state(100, 89, 1) == "Strong"


def test_single_session_never_mastered():
    # a perfect single session must cap at 'Strong', not 'Mastered'
    assert M.mastery_state(20, 20, 1) == "Strong"
    assert M.mastery_state(20, 19, 1) == "Strong"         # 95% but 1 session


def test_mastered_requires_cross_session_sustained_accuracy():
    # 90%+ across >= 2 sessions on >= 10 items
    assert M.mastery_state(20, 18, 2) == "Mastered"       # 90%, 2 sessions
    assert M.mastery_state(30, 28, 3) == "Mastered"       # 93%, 3 sessions
    # too few attempts even across sessions -> not yet
    assert M.mastery_state(8, 8, 3) == "Strong"
    # high accuracy, enough attempts, but only 1 session -> not yet
    assert M.mastery_state(20, 20, 1) == "Strong"
    # enough sessions + attempts but below 90% -> not mastered
    assert M.mastery_state(20, 17, 3) == "Strong"         # 85%


def test_states_and_colours_cover_all():
    assert set(M.STATE_COLOUR) == set(M.STATES)
    assert M.STATES[0] == "Not started" and M.STATES[-1] == "Mastered"
