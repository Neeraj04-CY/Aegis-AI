"""Deterministic risk scoring tables and helpers."""
from __future__ import annotations

from typing import Tuple

LIKELIHOOD_SCALE = {
    1: "RARE",
    2: "UNLIKELY",
    3: "POSSIBLE",
    4: "LIKELY",
    5: "ALMOST_CERTAIN",
}

IMPACT_SCALE = {
    1: "NEGLIGIBLE",
    2: "MINOR",
    3: "MODERATE",
    4: "MAJOR",
    5: "SEVERE",
}

RISK_SCORE_TABLE = {
    (l, i): l * i
    for l in range(1, 6)
    for i in range(1, 6)
}


def _normalize(value: float) -> int:
    if value <= 1:
        return 1
    if value >= 5:
        return 5
    return int(round(value))


def score_risk(likelihood: float, impact: float) -> Tuple[int, str]:
    """Return deterministic risk score and severity."""
    l = _normalize(likelihood)
    i = _normalize(impact)
    score = RISK_SCORE_TABLE[(l, i)]

    if score <= 4:
        severity = "LOW"
    elif score <= 9:
        severity = "MEDIUM"
    else:
        severity = "HIGH"

    return score, severity
