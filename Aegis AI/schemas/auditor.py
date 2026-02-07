"""Auditor contract."""
from dataclasses import dataclass
from typing import List, Any

@dataclass
class AuditRecord:
    what_happened: str
    deviations: List[str]
    evidence_refs: List[Any]

@dataclass
class AuditOutput:
    audit_record: AuditRecord
    policy_compliance: dict
    improvement_notes: List[str]