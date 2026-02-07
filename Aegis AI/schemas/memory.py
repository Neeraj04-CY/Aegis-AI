"""Memory contract."""
from dataclasses import dataclass
from typing import List, Any

@dataclass
class MemoryRecord:
    mission_summary: str
    decisions: List[Any]
    outcomes: List[Any]
    errors: List[Any]
    overrides: List[Any]
    lessons_learned: List[str]
    embedding_refs: List[Any]