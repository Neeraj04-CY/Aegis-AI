"""Deterministic Planner agent."""
from __future__ import annotations

from typing import Dict, List

from agents.base import BaseAgent


class PlannerAgent(BaseAgent):
    """Translate mission input into structured objectives and constraints."""

    def __init__(self, name: str = "PlannerAgent", version: str = "0.2.0") -> None:
        super().__init__(name=name, version=version)

    def policies(self) -> List[str]:
        return ["PLANNER_SCOPE_CLARITY", "PLANNER_MEASURABILITY"]

    def run(self, envelope: dict, context: dict) -> dict:
        mission_input = context.get("mission_input", {})
        mission = mission_input.get("mission", "")

        memory_store = context.get("memory_store")
        similar = []
        if memory_store and hasattr(memory_store, "read"):
            similar = memory_store.read({"mission": mission, "top_k": 3})

        objectives, constraints, success_criteria, assumptions = self._plan(mission)
        objectives, constraints = self._apply_memory_adjustments(
            objectives, constraints, similar
        )

        ambiguous = not objectives
        rationale = (
            "Mission is ambiguous or underspecified; objectives could not be derived."
            if ambiguous
            else "Objectives and constraints derived deterministically from mission."
        )

        if similar:
            rationale += " Memory review applied to adjust objectives and constraints."

        confidence = 0.7 if ambiguous else 0.85

        output = {
            "objectives": objectives,
            "constraints": constraints,
            "success_criteria": success_criteria,
            "assumptions": assumptions,
            "rationale": rationale,
            "confidence": confidence,
            "provenance": {"agent": self.name, "version": self.version},
        }
        self.validate(output)
        return output

    def _plan(self, mission: str) -> tuple[list, list, list, list]:
        if not isinstance(mission, str) or len(mission.strip()) < 12:
            return [], [], [], []

        lowered = mission.lower()

        objectives: List[str] = [
            f"Produce a structured plan for '{mission.strip()}' with 3 measurable milestones.",
        ]

        if any(token in lowered for token in ["deliver", "launch", "build", "deploy"]):
            objectives.append("Define delivery timeline with start/end dates and owners.")
        else:
            objectives.append("Define scope, deliverables, and acceptance criteria.")

        objectives = objectives[:3]

        constraints: List[str] = []
        if any(token in lowered for token in ["budget", "cost", "spend"]):
            constraints.append("Budget must be explicitly bounded and approved.")
        if any(token in lowered for token in ["deadline", "by ", "due", "timeline"]):
            constraints.append("Timeline must be explicitly defined and feasible.")
        if any(token in lowered for token in ["privacy", "compliance", "regulation", "policy"]):
            constraints.append("Must comply with applicable governance and privacy policies.")

        if not constraints:
            constraints.append("Operate deterministically and comply with governance policies.")

        success_criteria = [
            "Objectives are specific, measurable, and feasible.",
            "Constraints and assumptions are documented and accepted.",
            "Risk review and challenge review are completed.",
        ]

        assumptions = [
            "Stakeholder objectives are stable during execution.",
            "Required resources and data access will be available.",
        ]

        return objectives, constraints, success_criteria, assumptions

    def _apply_memory_adjustments(
        self, objectives: list, constraints: list, similar_records: list
    ) -> tuple[list, list]:
        if not similar_records:
            return objectives, constraints

        lessons = " ".join(str(item.get("lessons_learned", "")) for item in similar_records)
        errors = " ".join(str(item.get("errors", "")) for item in similar_records)

        if "ambiguous" in errors.lower():
            objectives = objectives + [
                "Clarify mission scope with explicit stakeholder confirmation."
            ]
        if "compliance" in lessons.lower() or "policy" in lessons.lower():
            constraints = constraints + [
                "Add governance checkpoint prior to execution approval."
            ]
        if "risk" in lessons.lower():
            constraints = constraints + [
                "Require mitigation review for MEDIUM/HIGH risks before approval."
            ]
        if "anomaly" in lessons.lower():
            constraints = constraints + [
                "Add anomaly review checkpoint before execution approval."
            ]

        return objectives[:3], list(dict.fromkeys(constraints))