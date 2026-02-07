"""Base agent contract for AEGIS."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List


class BaseAgent(ABC):
    """Core abstraction for all AEGIS agents."""

    name: str
    version: str

    def __init__(self, name: str, version: str) -> None:
        self.name = name
        self.version = version

    @abstractmethod
    def run(self, envelope: dict, context: dict) -> dict:
        """Execute the agent deterministically and return output."""

    def validate(self, output: dict) -> None:
        """Validate required output fields; raise if invalid or missing."""
        if not isinstance(output, dict):
            raise ValueError("Output must be a dict.")

        required = ["rationale", "confidence", "provenance"]
        missing = [key for key in required if key not in output]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        confidence = output.get("confidence")
        if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
            raise ValueError("Confidence must be a number in [0, 1].")

        provenance = output.get("provenance")
        if not isinstance(provenance, dict):
            raise ValueError("Provenance must be a dict.")

        if provenance.get("agent") != self.name:
            raise ValueError("Provenance agent mismatch.")

        if provenance.get("version") != self.version:
            raise ValueError("Provenance version mismatch.")

    @abstractmethod
    def policies(self) -> List[str]:
        """Return policy identifiers required by this agent."""
