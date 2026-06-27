from __future__ import annotations

from ai.contracts.triage_input import TriageInput
from ai.contracts.triage_output import TriageOutput
from ai.providers.base import TriageProvider
from ai.providers.hybrid import HybridTriageProvider


class TriageOrchestrator:
    def __init__(self, provider: TriageProvider | None = None):
        self.provider = provider or HybridTriageProvider()

    def triage(self, triage_input: TriageInput) -> TriageOutput:
        return self.provider.triage(triage_input)