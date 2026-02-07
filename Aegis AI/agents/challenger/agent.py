"""Deterministic Challenger agent."""
from __future__ import annotations

from typing import List

from agents.base import BaseAgent


class ChallengerAgent(BaseAgent):
    """Generate objections and alternative hypotheses deterministically."""

    def __init__(self, name: str = "ChallengerAgent", version: str = "0.2.0") -> None:
        super().__init__(name=name, version=version)

    def policies(self) -> List[str]:
        return ["CHALLENGER_CONTRADICTION_CHECK", "CHALLENGER_CONFIDENCE_ONLY_DECREASE"]

    def run(self, envelope: dict, context: dict) -> dict:
        planner_output = context.get("planner_output", {})
        analyst_output = context.get("analyst_output", {})
        risk_output = context.get("risk_output", {})

        memory_store = context.get("memory_store")
        mission_input = context.get("mission_input", {})
        mission = mission_input.get("mission", "") if isinstance(mission_input, dict) else ""
        similar = []
        if memory_store and hasattr(memory_store, "read"):
            similar = memory_store.read({"mission": mission, "top_k": 3})

        objections = self._generate_objections(planner_output, analyst_output, risk_output)
        objections = self._strengthen_from_memory(objections, similar)
        alternative_hypotheses = self._generate_alternatives(analyst_output)

        original_confidence = self._base_confidence(planner_output, analyst_output, risk_output)
        adjustment = -0.15 if objections else 0.0
        adjusted_confidence = max(0.0, min(1.0, original_confidence + adjustment))

        output = {
            "objections": objections,
            "alternative_hypotheses": alternative_hypotheses,
            "confidence_adjustment": {
                "original_confidence": original_confidence,
                "adjusted_confidence": adjusted_confidence,
                "delta": adjustment,
            },
            "rationale": "Deterministic challenge generated from planner, analyst, and risk outputs.",
            "confidence": 0.6,
            "provenance": {"agent": self.name, "version": self.version},
        }
        self.validate(output)
        return output

    def _generate_objections(self, planner: dict, analyst: dict, risk: dict) -> list:
        objections: List[dict] = []

        objectives = planner.get("objectives", []) if isinstance(planner, dict) else []
        if not objectives:
            objections.append(
                {
                    "target": "planner",
                    "argument": "Objectives are missing or ambiguous; plan may be invalid.",
                    "evidence_refs": ["planner.objectives"],
                    "severity": "HIGH",
                }
            )

        anomalies = analyst.get("anomalies", []) if isinstance(analyst, dict) else []
        if anomalies:
            objections.append(
                {
                    "target": "analyst",
                    "argument": "Anomalies detected that are not addressed in the plan.",
                    "evidence_refs": ["analyst.anomalies"],
                    "severity": "MEDIUM",
                }
            )

        if risk.get("severity") == "HIGH":
            objections.append(
                {
                    "target": "risk",
                    "argument": "High risk severity suggests plan requires revision before execution.",
                    "evidence_refs": ["risk.severity"],
                    "severity": "HIGH",
                }
            )

        return objections

    def _generate_alternatives(self, analyst: dict) -> list:
        alternatives: List[str] = []
        trends = analyst.get("trend_analysis", {}) if isinstance(analyst, dict) else {}
        if trends:
            direction = trends.get("direction", "unknown")
            alternatives.append(f"Assume trend reverses or stabilizes instead of {direction}.")
        if not alternatives:
            alternatives.append("Assume baseline stability; no material change expected.")
        return alternatives

    def _strengthen_from_memory(self, objections: list, similar_records: list) -> list:
        if not similar_records:
            return objections

        lessons = " ".join(str(item.get("lessons_learned", "")) for item in similar_records)
        errors = " ".join(str(item.get("errors", "")) for item in similar_records)

        if "policy" in lessons.lower() or "compliance" in lessons.lower():
            objections.append(
                {
                    "target": "governance",
                    "argument": "Prior incidents indicate governance gaps; require explicit policy checks.",
                    "evidence_refs": ["memory.lessons_learned"],
                    "severity": "MEDIUM",
                }
            )

        if "anomaly" in lessons.lower():
            objections.append(
                {
                    "target": "analysis",
                    "argument": "Historical anomaly lessons require explicit anomaly mitigation plan.",
                    "evidence_refs": ["memory.lessons_learned"],
                    "severity": "MEDIUM",
                }
            )

        if "failure" in errors.lower() or "error" in errors.lower():
            objections.append(
                {
                    "target": "execution",
                    "argument": "Past execution incidents suggest the plan needs stronger safeguards.",
                    "evidence_refs": ["memory.errors"],
                    "severity": "MEDIUM",
                }
            )

        return objections

    def _base_confidence(self, planner: dict, analyst: dict, risk: dict) -> float:
        confidences = []
        for item in (planner, analyst, risk):
            if isinstance(item, dict) and isinstance(item.get("confidence"), (int, float)):
                confidences.append(float(item["confidence"]))
        if not confidences:
            return 0.6
        return sum(confidences) / len(confidences)
