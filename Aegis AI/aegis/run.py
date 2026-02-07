"""CLI entry for AEGIS execution trace."""
from __future__ import annotations

import sys

import core.orchestrator as orchestrator
from aegis.demo_scenarios import SCENARIOS, format_mission_text


def _print_usage() -> None:
    print("Usage: python -m aegis.run <MISSION_ID>")
    print("Mission IDs: SAFE | DANGEROUS | UNETHICAL")


def _reset_memory_store() -> None:
    store = getattr(orchestrator, "_MEMORY_STORE", None)
    if store is None:
        return
    if hasattr(store, "_records"):
        store._records = []
    if hasattr(store, "_version"):
        store._version = 0


def _seed_audit_violation() -> None:
    store = getattr(orchestrator, "_MEMORY_STORE", None)
    if store is None or not hasattr(store, "write"):
        return
    store.write(
        {
            "mission_summary": "Prior executive override incident",
            "decisions": {"consensus": "REJECT", "execution_status": "BLOCKED"},
            "outcomes": {"state": "AUDITED", "governance_log": ["POLICY VIOLATION"]},
            "errors": ["POLICY VIOLATION FLAGGED"],
            "overrides": ["EXECUTIVE OVERRIDE ATTEMPT LOGGED"],
            "lessons_learned": ["Enforce governance gates under executive pressure."],
            "audit_flag": "VIOLATION",
        }
    )


def _verdict_from_result(result: dict, verdict_override: str | None) -> str:
    if verdict_override:
        return verdict_override
    outputs = result.get("outputs", {}) if isinstance(result, dict) else {}
    executor = outputs.get("executor", {}) if isinstance(outputs, dict) else {}
    consensus = outputs.get("consensus", {}) if isinstance(outputs, dict) else {}

    if executor.get("status") == "BLOCKED":
        return "EXECUTION BLOCKED"
    final_decision = consensus.get("final_decision")
    if final_decision == "APPROVE":
        return "APPROVE"
    return "REJECT"


def _audit_summary(result: dict, executive_override: bool) -> str:
    outputs = result.get("outputs", {}) if isinstance(result, dict) else {}
    consensus = outputs.get("consensus", {}) if isinstance(outputs, dict) else {}
    auditor = outputs.get("auditor", {}) if isinstance(outputs, dict) else {}

    decision = consensus.get("final_decision", "UNKNOWN")
    resolution = consensus.get("resolution_notes", "")
    audit_flag = auditor.get("audit_flag", "N/A")
    override_text = (
        "EXECUTIVE OVERRIDE ATTEMPT LOGGED" if executive_override else "NO OVERRIDE"
    )
    sentence = (
        f"Decision {decision} with audit status {audit_flag}; {override_text}."
    )
    if resolution:
        sentence = f"{sentence} {resolution}"
    return sentence.strip()


def main() -> int:
    args = sys.argv[1:]
    if not args:
        _print_usage()
        return 1

    scenario_id = args[0].strip().upper()
    scenario = SCENARIOS.get(scenario_id)
    if not scenario:
        _print_usage()
        return 1

    _reset_memory_store()
    if scenario.get("seed_audit_violations"):
        _seed_audit_violation()

    mission_input = {
        "mission": format_mission_text(scenario),
        "operational_data": scenario.get("operational_data", []),
        "trace": True,
        "trace_delay": 0.2,
        "mode": scenario.get("mode", "DEMO"),
        "executive_override": bool(scenario.get("executive_override")),
    }

    result = orchestrator.run_mission(mission_input)

    verdict = _verdict_from_result(result, scenario.get("verdict_override"))
    print(f"VERDICT: {verdict}")
    print("AUDIT SUMMARY: " + _audit_summary(result, mission_input["executive_override"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
