from __future__ import annotations

import pytest

from app.schemas.report import ReviewStatus as S
from app.services.status import InvalidTransition, allowed_next_statuses, validate_transition


def test_new_reports_can_move_to_review_or_be_confirmed_or_disputed() -> None:
    for target in (S.under_review, S.confirmed, S.disputed):
        validate_transition(S.unverified, target)


def test_unverified_cannot_jump_straight_to_resolved() -> None:
    with pytest.raises(InvalidTransition):
        validate_transition(S.unverified, S.resolved)


def test_resolved_can_only_be_reopened_for_review() -> None:
    assert allowed_next_statuses(S.resolved) == frozenset({S.under_review})
    with pytest.raises(InvalidTransition):
        validate_transition(S.resolved, S.confirmed)


def test_same_status_is_rejected() -> None:
    with pytest.raises(InvalidTransition):
        validate_transition(S.disputed, S.disputed)


def test_every_status_has_a_transition_entry() -> None:
    from app.services.status import ALLOWED_TRANSITIONS

    assert set(ALLOWED_TRANSITIONS) == set(S)
