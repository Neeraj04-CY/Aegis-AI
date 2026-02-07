"""CLI trace logger for AEGIS execution."""
from __future__ import annotations

import time
from typing import Optional


VERTICAL_LANGUAGE = "Enterprise incident response under executive pressure."


class TraceLogger:
    """Emit deterministic execution traces to stdout."""

    def __init__(self, enabled: bool = True, delay_seconds: float = 0.35) -> None:
        self.enabled = enabled
        self.delay_seconds = delay_seconds

    def log(self, agent: str, state: str, confidence: Optional[float], summary: str) -> None:
        if not self.enabled:
            return

        conf = f"{confidence:.2f}" if isinstance(confidence, (int, float)) else "--"
        agent_label = agent.upper().ljust(10)
        state_label = state.upper().ljust(9)
        summary_text = summary.strip() if summary else ""
        summary_text = (
            f"{VERTICAL_LANGUAGE} | {summary_text}" if summary_text else VERTICAL_LANGUAGE
        )
        if len(summary_text) > 72:
            summary_text = summary_text[:69].rstrip() + "..."

        print(f"[{agent_label}] [{state_label}] {conf}  {summary_text}")

        if self.delay_seconds and self.delay_seconds > 0:
            time.sleep(self.delay_seconds)
