"""State machine definitions."""
from enum import Enum

class State(str, Enum):
    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    AUDITED = "AUDITED"
    ARCHIVED = "ARCHIVED"