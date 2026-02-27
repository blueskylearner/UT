
from dataclasses import dataclass
from typing import List, Dict

@dataclass(frozen=True)
class Question:
    """Immutable representation of a single quiz item."""
    id: str
    prompt: str
    options: List[str]  # empty list for short-answer
    answer: str
    topic: str  # e.g., "Safeguarding", "GDPR"

@dataclass
class Result:
    """A quiz attempt result."""
    user_hash: str
    timestamp_iso: str
    score: int
    total: int
    details: Dict[str, bool]  # question_id -> correctness
