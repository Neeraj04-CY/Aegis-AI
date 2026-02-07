"""Common envelope + hashing stubs."""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class Envelope:
    trace_id: str
    mission_id: str
    step_id: str
    timestamp: str
    provenance: Dict[str, Any]
    inputs_hash: str
    payload: Dict[str, Any]

def compute_hash(payload: Dict[str, Any]) -> str:
    """Deterministic hash placeholder."""
    raise NotImplementedError("Phase 0: hashing not implemented.")