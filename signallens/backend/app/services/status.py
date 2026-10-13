"""Review-status transitions. Every change must be an explicit reviewer action.

A high model score never changes status. Only a valid transition below does.
"""

from __future__ import annotations

from app.schemas.report import ReviewStatus as S


class InvalidTransition(ValueError):
    """The requested review-status change is not allowed."""


ALLOWED_TRANSITIONS: dict[S, frozenset[S]] = {
    S.unverified: frozenset({S.under_review, S.confirmed, S.disputed}),
    S.under_review: frozenset({S.unverified, S.confirmed, S.disputed}),
    S.confirmed: frozenset({S.under_review, S.disputed, S.resolved}),
    S.disputed: frozenset({S.under_review, S.confirmed, S.resolved}),
    S.resolved: frozenset({S.under_review}),
}


def allowed_next_statuses(current: S) -> frozenset[S]:
    return ALLOWED_TRANSITIONS[current]


def validate_transition(current: S, target: S) -> None:
    if target == current:
        raise InvalidTransition(f"The report is already '{current.value}'.")
    if target not in ALLOWED_TRANSITIONS[current]:
        raise InvalidTransition(f"A report cannot move from '{current.value}' to '{target.value}'.")
