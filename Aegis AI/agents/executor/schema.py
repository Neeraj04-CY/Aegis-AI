"""Executor schema stub."""
from dataclasses import dataclass
from typing import List

@dataclass
class CommandOption:
    action: str
    preconditions: List[str]
    risks: List[str]
    expected_outcome: str

@dataclass
class ExecutorOutput:
    chosen_action: CommandOption
    command_options: List[CommandOption]
    execution_plan: List[dict]