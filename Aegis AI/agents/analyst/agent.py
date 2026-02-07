"""Deterministic Analyst agent."""
from __future__ import annotations

from statistics import median
from typing import Dict, List

from agents.base import BaseAgent


class AnalystAgent(BaseAgent):
    """Extract patterns, trends, and anomalies using rule-based logic."""

    def __init__(self, name: str = "AnalystAgent", version: str = "0.2.0") -> None:
        super().__init__(name=name, version=version)

    def policies(self) -> List[str]:
        return ["ANALYST_EVIDENCE_TRACEABILITY", "ANALYST_DETERMINISM"]

    def run(self, envelope: dict, context: dict) -> dict:
        planner_output = context.get("planner_output", {})
        operational_data = context.get("operational_data", [])

        key_patterns, trend_analysis, anomalies = self._analyze(operational_data)

        rationale = (
            "Patterns and anomalies derived deterministically from operational data."
            if operational_data
            else "No operational data provided; analysis limited to defaults."
        )

        confidence = 0.6 if not operational_data else 0.75

        output = {
            "key_patterns": key_patterns,
            "trend_analysis": trend_analysis,
            "anomalies": anomalies,
            "evidence_refs": ["planner_objectives"] if planner_output else [],
            "rationale": rationale,
            "confidence": confidence,
            "provenance": {"agent": self.name, "version": self.version},
        }
        self.validate(output)
        return output

    def _analyze(self, operational_data: object) -> tuple[list, dict, list]:
        key_patterns: List[dict] = []
        trend_analysis: Dict[str, object] = {}
        anomalies: List[dict] = []

        if isinstance(operational_data, list) and operational_data:
            numeric_series = [item for item in operational_data if isinstance(item, (int, float))]
            if numeric_series:
                first = numeric_series[0]
                last = numeric_series[-1]
                direction = "increasing" if last > first else "decreasing" if last < first else "flat"
                trend_analysis = {
                    "series": "numeric",
                    "direction": direction,
                    "start": first,
                    "end": last,
                }

                mid = median(numeric_series)
                for idx, value in enumerate(numeric_series):
                    if mid == 0:
                        continue
                    if value > 2 * mid or value < 0.5 * mid:
                        anomalies.append(
                            {
                                "item": f"value[{idx}]",
                                "deviation": f"{value} vs median {mid}",
                                "impact": "potential outlier",
                                "evidence_refs": [f"series_index:{idx}"],
                            }
                        )

                key_patterns.append(
                    {
                        "pattern": f"Numeric series is {direction}",
                        "evidence_refs": ["numeric_series"],
                        "significance": "medium" if direction != "flat" else "low",
                    }
                )

            dict_series = [item for item in operational_data if isinstance(item, dict)]
            if dict_series:
                keys = set().union(*(item.keys() for item in dict_series))
                for key in sorted(keys):
                    values = [item.get(key) for item in dict_series if isinstance(item.get(key), (int, float))]
                    if len(values) >= 2:
                        direction = "increasing" if values[-1] > values[0] else "decreasing" if values[-1] < values[0] else "flat"
                        key_patterns.append(
                            {
                                "pattern": f"{key} trend is {direction}",
                                "evidence_refs": [f"field:{key}"],
                                "significance": "medium" if direction != "flat" else "low",
                            }
                        )

        return key_patterns, trend_analysis, anomalies