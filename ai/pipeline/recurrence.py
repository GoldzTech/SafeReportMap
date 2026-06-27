from __future__ import annotations


def estimate_recurrence(text: str, location_text: str | None = None, location_zone: str | None = None) -> float:
    normalized = text.lower()
    score = 0.0

    recurrence_markers = [
        "novamente",
        "sempre",
        "várias vezes",
        "varias vezes",
        "frequente",
        "repet",
        "de novo",
        "todo dia",
        "toda semana",
        "mesmo lugar",
        "mesma sala",
        "mesmo local",
    ]

    if any(marker in normalized for marker in recurrence_markers):
        score += 0.4

    if location_text:
        loc = location_text.lower()
        if any(marker in loc for marker in ["corredor", "banheiro", "sala", "laboratório", "laboratorio", "pátio", "patio"]):
            score += 0.1

    if location_zone:
        zone = location_zone.lower()
        if any(marker in zone for marker in ["bloco", "andar", "ala", "pavilhão", "pavilhao"]):
            score += 0.1

    return round(min(score, 1.0), 2)