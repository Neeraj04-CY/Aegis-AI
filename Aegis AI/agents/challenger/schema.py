"""Challenger schema stub."""
from dataclasses import dataclass
from typing import List, Any

@dataclass
class Objection:
    target: str
    argument: str
    evidence_refs: List[Any]
    severity: str

@dataclass
class ChallengerOutput:
    objections: List[Objection]
    alternative_hypotheses: List[str]
    confidence_adjustment: dict