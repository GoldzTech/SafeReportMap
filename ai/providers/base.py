from __future__ import annotations

from abc import ABC, abstractmethod

from ai.contracts.triage_input import TriageInput
from ai.contracts.triage_output import TriageOutput


class TriageProvider(ABC):
    @abstractmethod
    def triage(self, triage_input: TriageInput) -> TriageOutput:
        raise NotImplementedError