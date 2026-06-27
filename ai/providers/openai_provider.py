from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

from ai.contracts.triage_input import TriageInput
from ai.contracts.triage_output import TriageOutput
from ai.providers.base import TriageProvider
from backend.app.core.config import settings
from backend.app.core.enums import IncidentCategory, SeverityLevel

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"
SYSTEM_PROMPT_PATH = PROMPTS_DIR / "triage_system_prompt.md"
USER_PROMPT_PATH = PROMPTS_DIR / "triage_user_prompt.md"


class OpenAITriageResponse(BaseModel):
    category: IncidentCategory
    severity: SeverityLevel
    priority_score: float = Field(ge=0.0, le=1.0)
    summary: str
    keywords: list[str] = Field(default_factory=list)
    recurrence_flag: bool
    recurrence_score: float | None = Field(default=None, ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    justification: str


def _schema_for_openai() -> dict:
    return {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": [item.value for item in IncidentCategory],
            },
            "severity": {
                "type": "string",
                "enum": [item.value for item in SeverityLevel],
            },
            "priority_score": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
            },
            "summary": {
                "type": "string",
            },
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 10,
            },
            "recurrence_flag": {
                "type": "boolean",
            },
            "recurrence_score": {
                "anyOf": [
                    {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    {"type": "null"},
                ]
            },
            "confidence": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
            },
            "justification": {
                "type": "string",
            },
        },
        "required": [
            "category",
            "severity",
            "priority_score",
            "summary",
            "keywords",
            "recurrence_flag",
            "recurrence_score",
            "confidence",
            "justification",
        ],
        "additionalProperties": False,
    }


def _load_prompt(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def _build_user_prompt(triage_input: TriageInput) -> str:
    template = _load_prompt(USER_PROMPT_PATH)
    return template.format(
        report_id=triage_input.report_id,
        content_raw=triage_input.content_raw,
        content_sanitized=triage_input.content_sanitized,
        incident_date=triage_input.incident_date.isoformat() if triage_input.incident_date else None,
        location_text=triage_input.location_text,
        location_zone=triage_input.location_zone,
        urgency_self_reported=triage_input.urgency_self_reported,
        cluster_id=triage_input.cluster_id,
        submitted_from_demo=triage_input.submitted_from_demo,
    )


def _explicit_physical_contact(text: str) -> bool:
    normalized = text.lower()
    explicit_terms = [
        "tocou",
        "tocada",
        "tocado",
        "encostou",
        "encostada",
        "encostado",
        "passou a mão",
        "passando a mão",
        "apalp",
        "agarr",
        "segurou",
        "puxou",
        "empurrou",
        "bateu",
        "golpeou",
        "beijou",
        "beijo forçado",
        "tentou me tocar",
        "tentou tocar",
    ]
    return any(term in normalized for term in explicit_terms)


def _downgrade_if_overconfident_physical_contact(
    category: IncidentCategory,
    severity: SeverityLevel,
    text: str,
    confidence: float,
) -> tuple[IncidentCategory, SeverityLevel, float]:
    if category != IncidentCategory.INAPPROPRIATE_PHYSICAL_CONTACT:
        return category, severity, confidence

    if _explicit_physical_contact(text):
        return category, severity, confidence

    normalized = text.lower()

    vague_verbal_terms = [
        "deu em cima",
        "cantou",
        "insinu",
        "flert",
        "foi inconveniente",
        "olhou estranho",
        "olhou de forma estranha",
        "foi estranho",
    ]

    if any(term in normalized for term in vague_verbal_terms):
        return IncidentCategory.VERBAL_HARASSMENT, SeverityLevel.MEDIUM, min(confidence, 0.62)

    return IncidentCategory.OTHER, SeverityLevel.LOW, min(confidence, 0.55)


def _filter_keywords(keywords: list[str], source_text: str) -> list[str]:
    normalized_source = source_text.lower()
    filtered: list[str] = []

    for keyword in keywords:
        kw = keyword.strip().lower()
        if not kw:
            continue

        if kw in normalized_source:
            filtered.append(keyword)
            continue

        if len(kw) >= 5 and any(part in normalized_source for part in kw.split()):
            filtered.append(keyword)

    deduped = list(dict.fromkeys(filtered))
    return deduped[:8]


class OpenAITriageProvider(TriageProvider):
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.OPENAI_MODEL

    def triage(self, triage_input: TriageInput) -> TriageOutput:
        system_prompt = _load_prompt(SYSTEM_PROMPT_PATH)
        user_prompt = _build_user_prompt(triage_input)

        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "safereport_triage",
                    "schema": _schema_for_openai(),
                    "strict": True,
                }
            },
        )

        raw_text = (response.output_text or "").strip()
        if not raw_text:
            raise RuntimeError("OpenAI returned an empty response.")

        try:
            parsed = OpenAITriageResponse.model_validate_json(raw_text)
        except ValidationError as exc:
            logger.exception("OpenAI triage response validation failed.")
            raise RuntimeError("OpenAI triage response was invalid.") from exc

        text_for_validation = f"{triage_input.content_raw}\n{triage_input.content_sanitized}"
        category, severity, confidence = _downgrade_if_overconfident_physical_contact(
            parsed.category,
            parsed.severity,
            text_for_validation,
            parsed.confidence,
        )

        keywords = _filter_keywords(parsed.keywords, text_for_validation)
        if not keywords:
            keywords = parsed.keywords[:5]

        return TriageOutput(
            report_id=triage_input.report_id,
            category=category,
            severity=severity,
            priority_score=parsed.priority_score,
            summary=parsed.summary,
            keywords=keywords,
            recurrence_flag=parsed.recurrence_flag,
            recurrence_score=parsed.recurrence_score,
            confidence=confidence,
            justification=parsed.justification,
            model_version=self.model,
            pipeline_version="openai-triage-v2",
            processed_at=datetime.now(timezone.utc),
        )