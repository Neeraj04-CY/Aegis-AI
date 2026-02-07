"""Risk schema stub."""
from dataclasses import dataclass
from typing import List

@dataclass
class RiskItem:
    description: str
    likelihood: float
    impact: float
    mitigation: str

@dataclass
class RiskOutput:
    risk_score: float
    severity: str  # LOW | MEDIUM | HIGH
    risk_rationale: str
    top_risks: List[RiskItem]