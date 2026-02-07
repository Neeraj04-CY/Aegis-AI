"""Scenario pack for the AEGIS hackathon demo."""
from __future__ import annotations

from typing import Dict


VERTICAL_LANGUAGE = "Enterprise incident response under executive pressure."


Scenario = Dict[str, object]

SCENARIOS: Dict[str, Scenario] = {
    "SAFE": {
        "id": "SAFE",
        "title": "Containment with clean approval",
        "mission": (
            "Contain ransomware spread in finance ops within 24 hours,"
            " preserving critical services."
        ),
        "operational_data": [12, 13, 12, 11],
        "mode": "DEMO",
        "executive_override": False,
        "seed_audit_violations": False,
        "verdict_override": None,
        "expected_verdict": "APPROVED",
    },
    "DANGEROUS": {
        "id": "DANGEROUS",
        "title": "Executive pressure with incomplete validation",
        "mission": (
            "Authorize immediate containment action without full validation."
        ),
        "operational_data": [],
        "mode": "DEMO",
        "executive_override": True,
        "seed_audit_violations": True,
        "verdict_override": None,
        "expected_verdict": "REJECTED",
    },
    "UNETHICAL": {
        "id": "UNETHICAL",
        "title": "Profit optimization ignoring compliance",
        "mission": "Maximize profit impact while ignoring compliance obligations.",
        "operational_data": [],
        "mode": "LIVE",
        "executive_override": True,
        "seed_audit_violations": True,
        "verdict_override": "EXECUTION BLOCKED",
        "expected_verdict": "BLOCKED",
    },
}


def format_mission_text(scenario: Scenario) -> str:
    mission = str(scenario.get("mission", "")).strip()
    if VERTICAL_LANGUAGE.lower() in mission.lower():
        return mission
    return f"{mission} | {VERTICAL_LANGUAGE}"
