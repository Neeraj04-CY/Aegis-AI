"""Memory store abstraction with append-only, versioned records."""
from __future__ import annotations

import hashlib
import json
from typing import Dict, List, Optional

from memory.retrieval import retrieve_similar


class MemoryStore:
    """Append-only memory store with versioned records."""

    def __init__(self) -> None:
        self._records: List[dict] = []
        self._version = 0

    @property
    def records(self) -> List[dict]:
        return list(self._records)

    def read(self, query: Optional[dict] = None) -> List[dict]:
        if query and isinstance(query, dict) and "mission" in query:
            return retrieve_similar(self._records, query["mission"], top_k=query.get("top_k", 3))
        return list(self._records)

    def write(self, record: dict) -> dict:
        if not isinstance(record, dict):
            raise ValueError("Record must be a dict.")

        required = [
            "mission_summary",
            "decisions",
            "outcomes",
            "errors",
            "overrides",
            "lessons_learned",
        ]
        missing = [key for key in required if key not in record]
        if missing:
            raise ValueError(f"Missing required memory fields: {missing}")

        self._version += 1
        payload = json.dumps(record, sort_keys=True, separators=(",", ":"))
        record_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        versioned = {
            "version": self._version,
            "record_id": record_hash,
            **record,
        }

        self._records.append(versioned)
        return versioned