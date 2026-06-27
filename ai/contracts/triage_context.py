from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class TriageContext:
    report_id: UUID
    cluster_id: UUID | None = None
    locale: str = "pt-BR"
    timezone: str = "America/Sao_Paulo"
    submitted_from_demo: bool = False
    created_at: datetime | None = None