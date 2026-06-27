from __future__ import annotations

from backend.app.core.enums import IncidentCategory, SeverityLevel


def classify_severity(text: str, category: IncidentCategory) -> SeverityLevel:
    normalized = text.lower()

    critical_terms = [
        "matar",
        "vou te pegar",
        "passando a mão",
        "passando a mao",
        "tocou",
        "encostou",
        "estupro",
        "agredir",
        "ameaça direta",
        "ameaca direta",
    ]
    high_terms = ["ameaça", "ameaca", "perseg", "medo", "intimid", "repet", "recorr", "assedi", "abus"]
    medium_terms = ["desconfort", "humilh", "piada", "xing", "ofens", "hostil"]
    low_terms = ["chato", "estranho", "incômodo", "incomodo", "pontual"]

    if any(term in normalized for term in critical_terms):
        return SeverityLevel.CRITICAL

    if any(term in normalized for term in high_terms):
        return SeverityLevel.HIGH

    if any(term in normalized for term in medium_terms):
        return SeverityLevel.MEDIUM

    if any(term in normalized for term in low_terms):
        return SeverityLevel.LOW

    if category in {IncidentCategory.THREAT, IncidentCategory.INAPPROPRIATE_PHYSICAL_CONTACT}:
        return SeverityLevel.HIGH

    if category in {IncidentCategory.DISCRIMINATION, IncidentCategory.INTIMIDATION}:
        return SeverityLevel.MEDIUM

    return SeverityLevel.LOW