from __future__ import annotations

from backend.app.core.enums import SeverityLevel


def compute_priority_score(
    severity: SeverityLevel,
    recurrence_score: float = 0.0,
    urgency_self_reported: int | None = None,
) -> float:
    base = {
        SeverityLevel.LOW: 0.25,
        SeverityLevel.MEDIUM: 0.50,
        SeverityLevel.HIGH: 0.75,
        SeverityLevel.CRITICAL: 0.95,
    }[severity]

    urgency_bonus = 0.0
    if urgency_self_reported is not None:
        urgency_bonus = max(0.0, min((urgency_self_reported - 1) / 4, 1.0)) * 0.15

    score = base + (recurrence_score * 0.1) + urgency_bonus
    return round(min(score, 1.0), 2)