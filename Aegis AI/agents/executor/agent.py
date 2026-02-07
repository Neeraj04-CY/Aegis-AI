"""Deterministic Executor agent."""
from __future__ import annotations

from typing import List

from agents.base import BaseAgent


class ExecutorAgent(BaseAgent):
    """Propose actions and guardrails; block if consensus is not APPROVE."""

    def __init__(self, name: str = "ExecutorAgent", version: str = "0.2.0") -> None:
        super().__init__(name=name, version=version)

    def policies(self) -> List[str]:
        return ["EXECUTION_GUARDRAILS", "EXECUTION_CONSENSUS_REQUIRED"]

    def run(self, envelope: dict, context: dict) -> dict:
        consensus = context.get("consensus", {})
        decision = consensus.get("final_decision")

        guardrails = [
            "Only execute with APPROVE consensus.",
            "Verify policy compliance before any external action.",
        ]

        if decision != "APPROVE":
            output = {
                "status": "BLOCKED",
                "reason": f"EXECUTION BLOCKED: consensus decision is {decision or 'UNKNOWN'}.",
                "guardrails": guardrails,
                "command_options": [],
                "execution_plan": [],
                "rationale": "EXECUTION BLOCKED by governance decision.",
                "confidence": 0.8,
                "provenance": {"agent": self.name, "version": self.version},
            }
            self.validate(output)
            return output

        command_options = [
            {
                "action": "Proceed with approved plan",
                "preconditions": ["Consensus APPROVE", "Policy checks complete"],
                "risks": ["Execution uncertainty"],
                "expected_outcome": "Plan executed within governance boundaries",
            }
        ]

        execution_plan = [
            {"step": 1, "action": "Validate inputs", "guardrail": "policy compliance"},
            {"step": 2, "action": "Execute plan", "guardrail": "monitoring enabled"},
        ]

        output = {
            "status": "READY",
            "chosen_action": command_options[0],
            "command_options": command_options,
            "execution_plan": execution_plan,
            "guardrails": guardrails,
            "rationale": "Execution plan prepared deterministically.",
            "confidence": 0.8,
            "provenance": {"agent": self.name, "version": self.version},
         }
        self.validate(output)
        return output
