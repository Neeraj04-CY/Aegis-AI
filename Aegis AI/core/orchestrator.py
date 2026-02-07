"""Main control loop (state machine) for AEGIS — Phase 1 skeleton."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import logging
from pathlib import Path
from typing import Dict, List

from agents.analyst.agent import AnalystAgent
from agents.auditor.agent import AuditorAgent
from agents.challenger.agent import ChallengerAgent
from agents.executor.agent import ExecutorAgent
from agents.planner.agent import PlannerAgent
from agents.risk.agent import RiskAgent
from core import consensus, states
from memory.store import MemoryStore


_MEMORY_STORE = MemoryStore()

logger = logging.getLogger(__name__)


def _stable_hash(payload: dict) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _validate_output(output: dict) -> None:
    required = ["rationale", "confidence", "provenance"]
    missing = [key for key in required if key not in output]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")


def _policy_check(subject: dict) -> List[str]:
    return ["POLICY VIOLATION: policy checks not enforced (stub)."]


def _load_trace_logger() -> object:
    trace_path = Path(__file__).resolve().parents[1] / "logging" / "trace.py"
    if not trace_path.exists():
        return None
    spec = importlib.util.spec_from_file_location("aegis_trace", trace_path)
    if not spec or not spec.loader:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, "TraceLogger", None)


def _summarize_audits(records: List[dict]) -> dict:
    violations = 0
    warnings = 0
    recent_flags: List[str] = []
    for record in records[-5:]:
        flag = record.get("audit_flag")
        if flag == "VIOLATION":
            violations += 1
            recent_flags.append(flag)
        elif flag == "WARNING":
            warnings += 1
            recent_flags.append(flag)
    return {
        "violations": violations,
        "warnings": warnings,
        "recent_flags": recent_flags,
    }


def run_mission(mission_input: dict) -> Dict[str, object]:
    """Run the deterministic AEGIS control loop."""
    trace_id = _stable_hash({"mission": mission_input})

    envelope = {
        "trace_id": trace_id,
        "mission_input": mission_input,
    }

    transitions: List[str] = []
    state = states.State.DRAFT

    def transition(next_state: states.State) -> None:
        nonlocal state
        state = next_state
        transitions.append(state.value)
        logger.info("State transition to %s", state.value)

    outputs: Dict[str, dict] = {}
    governance_log: List[str] = []
    if mission_input.get("executive_override"):
        governance_log.append("EXECUTIVE OVERRIDE ATTEMPT LOGGED")

    planner_agent = PlannerAgent()
    analyst_agent = AnalystAgent()
    risk_agent = RiskAgent()
    challenger_agent = ChallengerAgent()
    executor_agent = ExecutorAgent()
    auditor_agent = AuditorAgent()

    memory_store = _MEMORY_STORE

    audit_feedback = _summarize_audits(memory_store.records)

    TraceLogger = _load_trace_logger()
    trace_logger = TraceLogger(
        enabled=mission_input.get("trace", True),
        delay_seconds=float(mission_input.get("trace_delay", 0.35)),
    ) if TraceLogger else None
    if trace_logger and mission_input.get("executive_override"):
        trace_logger.log("governance", "NOTICE", None, "EXECUTIVE OVERRIDE ATTEMPT LOGGED")

    context: Dict[str, object] = {
        "mission_input": mission_input,
        "operational_data": mission_input.get("operational_data", []),
        "memory_store": memory_store,
        "audit_feedback": audit_feedback,
    }

    max_revisions = 1
    revision_attempts = 0

    if mission_input.get("mode") == "LIVE" and audit_feedback.get("violations", 0) > 0:
        governance_log.append(
            "EXECUTION BLOCKED: POLICY VIOLATION - LIVE mode blocked by audits."
        )
        if trace_logger:
            trace_logger.log(
                "consensus",
                "ARCHIVED",
                0.0,
                "CONSENSUS REACHED: EXECUTION BLOCKED - LIVE mode blocked by audits",
            )
        return {
            "trace_id": trace_id,
            "envelope": envelope,
            "state": states.State.ARCHIVED.value,
            "transitions": [states.State.ARCHIVED.value],
            "outputs": {
                "consensus": {
                    "final_decision": "REJECT",
                    "adjusted_confidence": 0.0,
                    "governance_log": [
                        "EXECUTION BLOCKED: POLICY VIOLATION - LIVE mode blocked by audits."
                    ],
                    "resolution_notes": (
                        "CONSENSUS REACHED: EXECUTION BLOCKED: POLICY VIOLATION - LIVE execution halted until audit violations are resolved."
                    ),
                }
            },
            "governance_log": governance_log,
            "memory": memory_store.records,
        }

    while True:
        transition(states.State.DRAFT)

        planner = planner_agent.run(envelope, context)
        _validate_output(planner)
        outputs["planner"] = planner
        context["planner_output"] = planner
        if trace_logger:
            trace_logger.log(
                "planner",
                "DRAFT",
                planner.get("confidence"),
                planner.get("rationale", "Objectives generated"),
            )

        transition(states.State.REVIEW)
        governance_log.extend(_policy_check(planner))

        analyst = analyst_agent.run(envelope, context)
        _validate_output(analyst)
        outputs["analyst"] = analyst
        context["analyst_output"] = analyst
        if trace_logger:
            summary = analyst.get("rationale", "Analysis completed")
            if analyst.get("anomalies"):
                summary = f"{len(analyst.get('anomalies'))} anomalies detected"
            trace_logger.log("analyst", "REVIEW", analyst.get("confidence"), summary)

        risk = risk_agent.run(envelope, context)
        _validate_output(risk)
        outputs["risk"] = risk
        context["risk_output"] = risk
        if trace_logger:
            severity = risk.get("severity")
            if severity in {"MEDIUM", "HIGH"}:
                summary = f"RISK ESCALATED: {severity}"
            else:
                summary = f"RISK ESCALATED: {severity or 'LOW'}"
            trace_logger.log("risk", "REVIEW", risk.get("confidence"), summary)

        challenger = challenger_agent.run(envelope, context)
        _validate_output(challenger)
        outputs["challenger"] = challenger
        context["challenger_output"] = challenger
        if trace_logger:
            summary = "No objections"
            if challenger.get("objections"):
                summary = f"Objection: {challenger['objections'][0].get('argument', 'issue')}"
            trace_logger.log("challenger", "REVIEW", challenger.get("confidence"), summary)

        consensus_result = consensus.resolve(
            planner, analyst, risk, challenger, audit_feedback=audit_feedback
        )
        outputs["consensus"] = consensus_result
        governance_log.extend(consensus_result.get("governance_log", []))
        context["consensus"] = consensus_result
        if trace_logger:
            trace_logger.log(
                "consensus",
                consensus_result.get("final_decision", "REVIEW"),
                consensus_result.get("adjusted_confidence"),
                consensus_result.get("resolution_notes", "CONSENSUS REACHED"),
            )

        decision = consensus_result.get("final_decision")
        if decision == "REVISE":
            revision_attempts += 1
            governance_log.append("Consensus requested revision.")
            if revision_attempts > max_revisions:
                decision = "REJECT"
                outputs["consensus"]["final_decision"] = decision
                outputs["consensus"]["resolution_notes"] = "Revision limit exceeded."
            else:
                continue

        if decision == "REJECT":
            transition(states.State.ARCHIVED)
            break

        if decision == "APPROVE":
            transition(states.State.APPROVED)
            executor = executor_agent.run(envelope, context)
            _validate_output(executor)
            outputs["executor"] = executor
            context["execution_output"] = executor
            if trace_logger:
                trace_logger.log(
                    "executor",
                    "EXECUTING",
                    executor.get("confidence"),
                    executor.get("rationale", "EXECUTION READY"),
                )

            transition(states.State.EXECUTING)

            auditor = auditor_agent.run(envelope, {**context, "governance_log": governance_log})
            _validate_output(auditor)
            outputs["auditor"] = auditor
            if trace_logger:
                trace_logger.log(
                    "auditor",
                    "AUDITED",
                    auditor.get("confidence"),
                    auditor.get("rationale", "Audit complete"),
                )

            transition(states.State.AUDITED)
            transition(states.State.ARCHIVED)
            break

    return {
        "trace_id": trace_id,
        "envelope": envelope,
        "state": state.value,
        "transitions": transitions,
        "outputs": outputs,
        "governance_log": governance_log,
        "memory": memory_store.records,
    }


class Orchestrator:
    """Deterministic orchestrator skeleton."""

    def run(self, mission: dict) -> dict:
        return run_mission(mission)