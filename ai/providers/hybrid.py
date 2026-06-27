from __future__ import annotations

import logging

from ai.contracts.triage_input import TriageInput
from ai.contracts.triage_output import TriageOutput
from ai.providers.base import TriageProvider
from ai.providers.openai_provider import OpenAITriageProvider
from ai.providers.rule_based import RuleBasedTriageProvider
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class HybridTriageProvider(TriageProvider):
    def __init__(self) -> None:
        self.fallback_provider = RuleBasedTriageProvider()

        if settings.AI_PROVIDER == "rule_based":
            self.primary_provider = self.fallback_provider
            return

        if settings.AI_PROVIDER == "openai":
            self.primary_provider = OpenAITriageProvider()
            return

        try:
            self.primary_provider = OpenAITriageProvider()
        except Exception:
            logger.exception("OpenAI provider unavailable, falling back to rule-based provider.")
            self.primary_provider = self.fallback_provider

    def triage(self, triage_input: TriageInput) -> TriageOutput:
        try:
            return self.primary_provider.triage(triage_input)
        except Exception:
            logger.exception("Primary triage provider failed, falling back to rule-based provider.")
            return self.fallback_provider.triage(triage_input)