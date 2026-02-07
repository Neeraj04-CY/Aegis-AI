"""Analyst schema stub."""
from dataclasses import dataclass
from typing import List, Any

@dataclass
class Pattern:
    pattern: str
    evidence_refs: List[Any]
    significance: str

@dataclass
class Anomaly:
    item: str
    deviation: str
    impact: str
    evidence_refs: List[Any]

@dataclass
class AnalystOutput:
    key_patterns: List[Pattern]
    trend_analysis: dict
    anomalies: List[Anomaly]
    rationale: str