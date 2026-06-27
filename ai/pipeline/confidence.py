from __future__ import annotations

from backend.app.core.enums import SeverityLevel


def estimate_confidence(text: str, keywords: list[str], severity: SeverityLevel) -> float:
    confidence = 0.45

    if len(text) > 120:
        confidence += 0.1

    confidence += min(len(keywords), 5) * 0.08

    if severity in {SeverityLevel.HIGH, SeverityLevel.CRITICAL}:
        confidence += 0.1

    return round(min(confidence, 0.98), 2)