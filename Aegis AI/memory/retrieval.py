"""Deterministic memory retrieval via keyword overlap."""
from __future__ import annotations

import re
from typing import Iterable, List, Tuple


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _score(query_tokens: List[str], record_text: str) -> int:
    if not record_text:
        return 0
    record_tokens = set(_tokenize(record_text))
    return sum(1 for token in query_tokens if token in record_tokens)


def retrieve_similar(records: Iterable[dict], mission: str, top_k: int = 3) -> List[dict]:
    query_tokens = _tokenize(mission or "")
    scored: List[Tuple[int, dict]] = []

    for record in records:
        record_text = " ".join(
            str(record.get(field, ""))
            for field in ["mission_summary", "lessons_learned", "errors", "outcomes"]
        )
        score = _score(query_tokens, record_text)
        scored.append((score, record))

    scored.sort(key=lambda item: (-item[0], item[1].get("version", 0)))
    return [record for score, record in scored if score > 0][:top_k]
