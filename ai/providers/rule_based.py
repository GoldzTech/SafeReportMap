from __future__ import annotations

import re
from datetime import datetime, timezone

from ai.contracts.triage_input import TriageInput
from ai.contracts.triage_output import TriageOutput
from ai.pipeline.classification import classify_category
from ai.pipeline.confidence import estimate_confidence
from ai.pipeline.priority import compute_priority_score
from ai.pipeline.recurrence import estimate_recurrence
from ai.pipeline.severity import classify_severity
from ai.pipeline.summarization import generate_summary
from backend.app.core.enums import IncidentCategory, SeverityLevel
from ai.providers.base import TriageProvider


class RuleBasedTriageProvider(TriageProvider):
    def triage(self, triage_input: TriageInput) -> TriageOutput:
        text = (triage_input.content_sanitized or triage_input.content_raw).strip()
        normalized = text.lower()

        category = classify_category(normalized)
        severity = classify_severity(normalized, category)
        recurrence_score = estimate_recurrence(
            normalized,
            location_text=triage_input.location_text,
            location_zone=triage_input.location_zone,
        )
        recurrence_flag = recurrence_score >= 0.6
        keywords = self._extract_keywords(normalized)
        summary = generate_summary(text)
        priority_score = compute_priority_score(
            severity=severity,
            recurrence_score=recurrence_score,
            urgency_self_reported=triage_input.urgency_self_reported,
        )
        confidence = estimate_confidence(text, keywords, severity)
        justification = self._build_justification(category, severity, recurrence_flag)

        return TriageOutput(
            report_id=triage_input.report_id,
            category=category,
            severity=severity,
            priority_score=priority_score,
            summary=summary,
            keywords=keywords,
            recurrence_flag=recurrence_flag,
            recurrence_score=recurrence_score,
            confidence=confidence,
            justification=justification,
            model_version="rule-based-v1",
            pipeline_version="triage-pipeline-v1",
            processed_at=datetime.now(timezone.utc),
        )

    def _extract_keywords(self, text: str) -> list[str]:
        candidate_keywords = [
            "ameaça",
            "assédio",
            "insulto",
            "humilhação",
            "toque",
            "mão",
            "medo",
            "intimidação",
            "discriminação",
            "exclusão",
            "recorrência",
            "perseguição",
            "violência",
            "abuso",
        ]
        found = [keyword for keyword in candidate_keywords if keyword in text]

        if found:
            return found[:10]

        words = re.findall(r"\b[\wÀ-ÿ]{5,}\b", text)
        deduped = list(dict.fromkeys(words))
        return deduped[:10]

    def _build_justification(
        self,
        category: IncidentCategory,
        severity: SeverityLevel,
        recurrence_flag: bool,
    ) -> str:
        recurrence_part = " Há indício de recorrência." if recurrence_flag else ""
        return f"O relato foi classificado como {category.value} com severidade {severity.value}.{recurrence_part}"