"""Shared envelope & provenance schemas."""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Provenance:
    agent: str
    version: str
    policy_checks: list

@dataclass
class Envelope:
    trace_id: str
    mission_id: str
    step_id: str
    timestamp: str
    provenance: Provenance
    inputs_hash: str
    payload: Dict[str, Any]