"""Planner schema stub."""
from dataclasses import dataclass
from typing import List

@dataclass
class Objective:
    id: str
    description: str
    priority: str
    owner_hint: str

@dataclass
class PlannerOutput:
    objectives: List[Objective]
    constraints: List[str]
    success_criteria: List[str]
    assumptions: List[str]
    rationale: str