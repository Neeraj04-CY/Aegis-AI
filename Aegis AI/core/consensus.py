"""Consensus resolution logic (deterministic stub)."""
from __future__ import annotations

from typing import Dict, List


def _has_high_severity_objection(challenger: dict) -> bool:
    objections = challenger.get("objections", []) if isinstance(challenger, dict) else []
    for objection in objections:
        if isinstance(objection, dict) and objection.get("severity") == "HIGH":
            return True
    return False


def _risk_is_high_without_mitigation(risk: dict) -> bool:
    if not isinstance(risk, dict):
        return False
    severity = risk.get("severity")
    top_risks = risk.get("top_risks", [])
    lacks_mitigation = False
    for item in top_risks if isinstance(top_risks, list) else []:
        if isinstance(item, dict) and not item.get("mitigation"):
            lacks_mitigation = True
            break
    return severity == "HIGH" and lacks_mitigation


def _risk_is_medium_without_mitigation(risk: dict) -> bool:
    if not isinstance(risk, dict):
        return False
    severity = risk.get("severity")
    top_risks = risk.get("top_risks", [])
    lacks_mitigation = False
    for item in top_risks if isinstance(top_risks, list) else []:
        if isinstance(item, dict) and not item.get("mitigation"):
            lacks_mitigation = True
            break
    return severity == "MEDIUM" and lacks_mitigation


def _has_high_severity_risk(risk: dict) -> bool:
    return isinstance(risk, dict) and risk.get("severity") == "HIGH"


def _challenger_adjusted_confidence(challenger: dict, fallback: float) -> float:
    if not isinstance(challenger, dict):
        return fallback
    adjustment = challenger.get("confidence_adjustment", {})
    if isinstance(adjustment, dict) and isinstance(adjustment.get("adjusted_confidence"), (int, float)):
        return float(adjustment["adjusted_confidence"])
    return fallback


def _audit_pressure(audit_feedback: dict) -> tuple[float, str]:
    if not isinstance(audit_feedback, dict):
        return 0.5, "No audit feedback applied."

    violations = audit_feedback.get("violations", 0)
    warnings = audit_feedback.get("warnings", 0)
    if violations > 0:
        return 0.8, "Audit violations present; higher approval threshold enforced."
    if warnings >= 2:
        return 0.7, "Repeated audit warnings; elevated approval threshold enforced."
    if warnings == 1:
        return 0.6, "Audit warning present; mild approval pressure applied."
    return 0.5, "No audit pressure applied."


def resolve(
    planner: dict,
    analyst: dict,
    risk: dict,
    challenger: dict,
    audit_feedback: dict | None = None,
) -> Dict[str, object]:
    """Resolve consensus using deterministic rules."""
    governance_log: List[str] = ["CONSENSUS EVALUATION STARTED."]

    base_confidence = 0.7
    adjusted_confidence = _challenger_adjusted_confidence(challenger, base_confidence)
    required_confidence, pressure_note = _audit_pressure(audit_feedback or {})
    governance_log.append(pressure_note)

    if _risk_is_high_without_mitigation(risk):
        governance_log.append("POLICY VIOLATION: risk severity HIGH with missing mitigation.")
        return {
            "final_decision": "REJECT",
            "adjusted_confidence": min(adjusted_confidence, 0.3),
            "governance_log": governance_log,
            "resolution_notes": (
                "CONSENSUS REACHED: EXECUTION BLOCKED due to unmanaged high risk without mitigation."
            ),
        }

    if _has_high_severity_objection(challenger):
        governance_log.append("POLICY VIOLATION: challenger objections at HIGH severity.")
        return {
            "final_decision": "REVISE",
            "adjusted_confidence": min(adjusted_confidence, 0.45),
            "governance_log": governance_log,
            "resolution_notes": "CONSENSUS REACHED: POLICY VIOLATION requires revision due to high-severity objections.",
        }

    if _risk_is_medium_without_mitigation(risk):
        governance_log.append("POLICY VIOLATION: risk severity MEDIUM with missing mitigation.")
        return {
            "final_decision": "REVISE",
            "adjusted_confidence": min(adjusted_confidence, 0.55),
            "governance_log": governance_log,
            "resolution_notes": "CONSENSUS REACHED: POLICY VIOLATION requires mitigation updates.",
        }

    if _has_high_severity_risk(risk):
        governance_log.append("POLICY VIOLATION: risk severity HIGH; mitigation present.")
        return {
            "final_decision": "REVISE",
            "adjusted_confidence": min(adjusted_confidence, 0.6),
            "governance_log": governance_log,
            "resolution_notes": "CONSENSUS REACHED: POLICY VIOLATION requires revision due to high risk.",
        }

    if adjusted_confidence < required_confidence:
        governance_log.append("POLICY VIOLATION: adjusted confidence below threshold.")
        return {
            "final_decision": "REVISE",
            "adjusted_confidence": adjusted_confidence,
            "governance_log": governance_log,
            "resolution_notes": "CONSENSUS REACHED: POLICY VIOLATION requires higher confidence.",
        }

    governance_log.append("CONSENSUS REACHED: no blocking objections or unmanaged risks.")
    return {
        "final_decision": "APPROVE",
        "adjusted_confidence": adjusted_confidence,
        "governance_log": governance_log,
        "resolution_notes": "CONSENSUS REACHED: APPROVED with challenger adjustment. "
        + pressure_note,
    }
