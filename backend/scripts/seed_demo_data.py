from __future__ import annotations

from backend.app.core.enums import ClusterType, SeverityLevel
from backend.app.db.session import SessionLocal
from backend.app.models.cluster import Cluster
from backend.app.models.institution_area import InstitutionArea


INSTITUTION_AREAS = [
    {"name": "Entrada Principal", "code": "ENTRADA", "area_type": "access"},
    {"name": "Corredor Central", "code": "CORREDOR_CENTRAL", "area_type": "circulation"},
    {"name": "Pátio", "code": "PATIO", "area_type": "common_area"},
    {"name": "Banheiro Feminino", "code": "BANHEIRO_F", "area_type": "restroom"},
    {"name": "Banheiro Masculino", "code": "BANHEIRO_M", "area_type": "restroom"},
    {"name": "Sala 01", "code": "SALA_01", "area_type": "classroom"},
    {"name": "Sala 02", "code": "SALA_02", "area_type": "classroom"},
    {"name": "Sala 03", "code": "SALA_03", "area_type": "classroom"},
    {"name": "Laboratório de Informática", "code": "LAB_INFO", "area_type": "lab"},
    {"name": "Biblioteca", "code": "BIBLIOTECA", "area_type": "study"},
    {"name": "Quadra", "code": "QUADRA", "area_type": "sports"},
    {"name": "Coordenação", "code": "COORDENACAO", "area_type": "administration"},
]

CLUSTERS = [
    {
        "cluster_type": ClusterType.SPATIAL,
        "label": "Corredor Central - Ocorrências recorrentes",
        "severity_level": SeverityLevel.HIGH,
        "recurrence_count": 4,
        "zone_reference": "Corredor Central",
        "description": "Relatos recorrentes em área de circulação principal.",
    },
    {
        "cluster_type": ClusterType.SPATIAL,
        "label": "Pátio - Interações hostis",
        "severity_level": SeverityLevel.MEDIUM,
        "recurrence_count": 3,
        "zone_reference": "Pátio",
        "description": "Ocorrências concentradas em intervalo de recreio/intervalo.",
    },
    {
        "cluster_type": ClusterType.TEXTUAL,
        "label": "Insinuações e abordagens verbais",
        "severity_level": SeverityLevel.MEDIUM,
        "recurrence_count": 5,
        "zone_reference": None,
        "description": "Grupo de relatos com linguagem semelhante de assédio verbal.",
    },
    {
        "cluster_type": ClusterType.HYBRID,
        "label": "Laboratório - Conduta inadequada",
        "severity_level": SeverityLevel.CRITICAL,
        "recurrence_count": 2,
        "zone_reference": "Laboratório de Informática",
        "description": "Casos críticos com potencial contato físico ou intimidação.",
    },
]


def seed_institution_areas(session) -> None:
    existing_codes = {
        code for (code,) in session.query(InstitutionArea.code).all() if code is not None
    }

    created = 0
    for item in INSTITUTION_AREAS:
        if item["code"] in existing_codes:
            continue

        session.add(
            InstitutionArea(
                name=item["name"],
                code=item["code"],
                area_type=item["area_type"],
                description=None,
                active=True,
            )
        )
        created += 1

    session.commit()
    print(f"[seed] institution_areas: {created} created")


def seed_clusters(session) -> None:
    existing_labels = {label for (label,) in session.query(Cluster.label).all() if label is not None}

    created = 0
    for item in CLUSTERS:
        if item["label"] in existing_labels:
            continue

        session.add(
            Cluster(
                cluster_type=item["cluster_type"],
                label=item["label"],
                severity_level=item["severity_level"],
                recurrence_count=item["recurrence_count"],
                zone_reference=item["zone_reference"],
                description=item["description"],
                is_active=True,
            )
        )
        created += 1

    session.commit()
    print(f"[seed] clusters: {created} created")


def main() -> None:
    session = SessionLocal()
    try:
        seed_institution_areas(session)
        seed_clusters(session)
    finally:
        session.close()


if __name__ == "__main__":
    main()