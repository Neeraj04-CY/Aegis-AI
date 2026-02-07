"""Deterministic Risk agent."""
from __future__ import annotations

from typing import List

from agents.base import BaseAgent
from governance.risk_tables import score_risk


class RiskAgent(BaseAgent):
    """Evaluate deterministic risks using a rubric scoring table."""

    def __init__(self, name: str = "RiskAgent", version: str = "0.2.0") -> None:
        super().__init__(name=name, version=version)

    def policies(self) -> List[str]:
        return ["RISK_RUBRIC_SCORING", "RISK_MITIGATION_REQUIRED"]

    def run(self, envelope: dict, context: dict) -> dict:
        planner_output = context.get("planner_output", {})
        analyst_output = context.get("analyst_output", {})

        top_risks = self._build_risks(planner_output, analyst_output)
        risk_score, severity = self._aggregate_risk(top_risks)

        output = {
            "risk_score": risk_score,
            "severity": severity,
            "risk_rationale": "Deterministic rubric scoring based on planner and analyst outputs.",
            "top_risks": top_risks,
            "rationale": "Risk assessment completed via deterministic rubric.",
            "confidence": 0.7,
            "provenance": {"agent": self.name, "version": self.version},
        }
        self.validate(output)
        return output

    def _build_risks(self, planner_output: dict, analyst_output: dict) -> list:
        top_risks: List[dict] = []

        objectives = planner_output.get("objectives", []) if isinstance(planner_output, dict) else []
        constraints = planner_output.get("constraints", []) if isinstance(planner_output, dict) else []
        anomalies = analyst_output.get("anomalies", []) if isinstance(analyst_output, dict) else []

        if not objectives:
            top_risks.append(
                {
                    "description": "Ambiguous mission objectives",
                    "likelihood": 4,
                    "impact": 4,
                    "mitigation": "Clarify mission scope and measurable objectives.",
                }
            )

        if anomalies:
            top_risks.append(
                {
                    "description": "Operational anomalies present",
                    "likelihood": 3,
                    "impact": 3,
                    "mitigation": "Investigate anomalies and validate data integrity.",
                }
            )

        if any("compliance" in str(c).lower() or "policy" in str(c).lower() for c in constraints):
            top_risks.append(
                {
                    "description": "Governance or compliance constraints may delay execution",
                    "likelihood": 3,
                    "impact": 4,
                    "mitigation": "Engage governance review early and document approvals.",
                }
            )

        if not top_risks:
            top_risks.append(
                {
                    "description": "Default execution uncertainty",
                    "likelihood": 2,
                    "impact": 2,
                    "mitigation": "Monitor execution signals and adjust plan if needed.",
                }
            )

        return top_risks

    def _aggregate_risk(self, top_risks: list) -> tuple[int, str]:
        scores = []
        severities = []
        for item in top_risks:
            score, severity = score_risk(item.get("likelihood", 1), item.get("impact", 1))
            scores.append(score)
            severities.append(severity)

            if severity in {"MEDIUM", "HIGH"} and not item.get("mitigation"):
                item["mitigation"] = "Mitigation required for MEDIUM/HIGH risk."

        max_score = max(scores) if scores else 0
        final_severity = (
            "HIGH" if "HIGH" in severities else "MEDIUM" if "MEDIUM" in severities else "LOW"
        )
        return max_score, final_severity
