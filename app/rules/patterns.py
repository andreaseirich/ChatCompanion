"""Pattern definitions for rule-based detection."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Pattern:
    """A detection pattern with metadata."""

    pattern: str
    confidence: float
    description: str
    category: str


@dataclass
class PatternMatch:
    """Result of a pattern match."""

    pattern: Pattern
    matched_text: str
    position: int
    confidence: float


class PatternRegistry:
    """Registry for all detection patterns."""

    def __init__(self):
        self.patterns: List[Pattern] = []

    def add_pattern(self, pattern: Pattern) -> None:
        """Add a pattern to the registry."""
        self.patterns.append(pattern)

    def get_patterns_by_category(self, category: str) -> List[Pattern]:
        """Get all patterns for a specific category."""
        return [p for p in self.patterns if p.category == category]

    def get_all_patterns(self) -> List[Pattern]:
        """Get all registered patterns."""
        return self.patterns.copy()

