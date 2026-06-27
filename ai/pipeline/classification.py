from __future__ import annotations

from backend.app.core.enums import IncidentCategory


CATEGORY_RULES: list[tuple[IncidentCategory, list[str]]] = [
    (
        IncidentCategory.THREAT,
        ["ameaça", "ameaca", "matar", "vou pegar", "te pegar", "vou te pegar", "te matar"],
    ),
    (
        IncidentCategory.INAPPROPRIATE_PHYSICAL_CONTACT,
        ["passando a mão", "passando a mao", "encostou", "tocou", "mão", "mao", "toque", "apalp", "assédio físico", "assedio fisico"],
    ),
    (
        IncidentCategory.VERBAL_HARASSMENT,
        ["xing", "insult", "humilh", "piada", "ofens", "ridicular", "apelido"],
    ),
    (
        IncidentCategory.DISCRIMINATION,
        ["discrimin", "racism", "machism", "sexism", "preconceito", "tratamento diferente"],
    ),
    (
        IncidentCategory.INTIMIDATION,
        ["medo", "intimid", "coagir", "pressão", "pressao", "ameaça velada", "ameaca velada", "persegu"],
    ),
    (
        IncidentCategory.EXCLUSION,
        ["exclu", "ostrac", "isolad", "boicot", "ninguém fala comigo", "ninguem fala comigo"],
    ),
]


def classify_category(text: str) -> IncidentCategory:
    normalized = text.lower()
    for category, keywords in CATEGORY_RULES:
        if any(keyword in normalized for keyword in keywords):
            return category
    return IncidentCategory.OTHER