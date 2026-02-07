"""Consensus contract."""
from dataclasses import dataclass
from typing import List

@dataclass
class PolicyCheck:
    id: str
    result: str
    rationale: str

@dataclass
class ConsensusOutput:
    final_decision: str          # APPROVE | REJECT | REVISE
    adjusted_confidence: float
    governance_log: List[PolicyCheck]
    resolution_notes: str