"""Deterministic Auditor agent."""
from __future__ import annotations

from typing import List

from agents.base import BaseAgent


class AuditorAgent(BaseAgent):
    """Record what happened, policy compliance, and improvement notes."""

    def __init__(self, name: str = "AuditorAgent", version: str = "0.2.0") -> None:
        super().__init__(name=name, version=version)

    def policies(self) -> List[str]:
        return ["AUDIT_LOGGING", "AUDIT_MEMORY_WRITE"]

    def run(self, envelope: dict, context: dict) -> dict:
        execution_output = context.get("execution_output", {})
        governance_log = context.get("governance_log", [])
        consensus = context.get("consensus", {})
        mission_input = context.get("mission_input", {})

        audit_record = {
            "what_happened": execution_output.get("status", "UNKNOWN"),
            "deviations": ["EXECUTION BLOCKED"] if execution_output.get("status") == "BLOCKED" else [],
            "evidence_refs": ["execution_output", "governance_log"],
        }

        policy_compliance = {
            "consensus_decision": consensus.get("final_decision"),
            "governance_log": governance_log,
        }

        improvement_notes = []
        if execution_output.get("status") == "BLOCKED":
            improvement_notes.append(
                "Resolve POLICY VIOLATION and governance objections before re-submission."
            )

        decision = consensus.get("final_decision")
        execution_status = execution_output.get("status")
        decision_outcome_consistency = "OK"
        if decision == "APPROVE" and execution_status == "BLOCKED":
            decision_outcome_consistency = "VIOLATION"
        elif decision in {"REJECT", "REVISE"} and execution_status == "READY":
            decision_outcome_consistency = "WARNING"

        policy_drift = "OK"
        if any("not enforced" in str(entry).lower() for entry in governance_log):
            policy_drift = "WARNING"

        adjusted_confidence = consensus.get("adjusted_confidence")
        confidence_calibration_error = "OK"
        if decision == "APPROVE" and isinstance(adjusted_confidence, (int, float)):
            if adjusted_confidence < 0.4:
                confidence_calibration_error = "VIOLATION"
            elif adjusted_confidence < 0.6:
                confidence_calibration_error = "WARNING"

        mode = mission_input.get("mode") if isinstance(mission_input, dict) else None
        audit_flag = "OK"
        if decision_outcome_consistency == "VIOLATION" or confidence_calibration_error == "VIOLATION":
            audit_flag = "VIOLATION"
        elif policy_drift == "WARNING" and mode == "LIVE":
            audit_flag = "VIOLATION"
        elif decision_outcome_consistency == "WARNING" or policy_drift == "WARNING" or confidence_calibration_error == "WARNING":
            audit_flag = "WARNING"

        output = {
            "audit_record": audit_record,
            "policy_compliance": policy_compliance,
            "decision_outcome_consistency": decision_outcome_consistency,
            "policy_compliance_drift": policy_drift,
            "confidence_calibration_error": confidence_calibration_error,
            "audit_flag": audit_flag,
            "improvement_notes": improvement_notes,
            "rationale": "Audit record assembled deterministically from execution and governance data.",
            "confidence": 0.85,
            "provenance": {"agent": self.name, "version": self.version},
        }

        memory_store = context.get("memory_store")
        if memory_store and hasattr(memory_store, "write"):
            mission_summary = mission_input.get("mission", "") if isinstance(mission_input, dict) else ""
            decisions = {
                "consensus": consensus.get("final_decision"),
                "execution_status": execution_output.get("status"),
            }
            outcomes = {
                "state": "AUDITED",
                "governance_log": governance_log,
            }
            errors = []
            if execution_output.get("status") == "BLOCKED":
                errors.append("EXECUTION BLOCKED")
            if consensus.get("final_decision") == "REJECT":
                errors.append("CONSENSUS REJECTED MISSION")
            if audit_flag == "VIOLATION":
                errors.append("POLICY VIOLATION FLAGGED")

            overrides = []
            lessons_learned = improvement_notes or [
                "Maintain governance checks and anomaly reviews before execution."
            ]

            memory_store.write(
                {
                    "mission_summary": mission_summary,
                    "decisions": decisions,
                    "outcomes": outcomes,
                    "errors": errors,
                    "overrides": overrides,
                    "lessons_learned": lessons_learned,
                    "trace_id": envelope.get("trace_id"),
                    "audit_flag": audit_flag,
                    "audit": output,
                }
            )

        self.validate(output)
        return output
