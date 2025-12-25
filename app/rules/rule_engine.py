"""Rule engine for pattern-based risk detection."""

import re
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from app.rules.patterns import Pattern, PatternMatch, PatternRegistry
from app.utils.constants import RiskCategory


class RuleEngine:
    """Engine for matching rules against chat text."""

    def __init__(self, rules_config_path: Optional[Path] = None):
        """
        Initialize the rule engine.

        Args:
            rules_config_path: Path to YAML rules configuration file.
                              If None, uses default path.
        """
        if rules_config_path is None:
            rules_config_path = Path(__file__).parent / "rules_config.yaml"

        self.registry = PatternRegistry()
        self._load_rules(rules_config_path)

    def _load_rules(self, config_path: Path) -> None:
        """Load rules from YAML configuration file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Rules config not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        rules = config.get("rules", {})
        for category, category_rules in rules.items():
            patterns = category_rules.get("patterns", [])
            for pattern_def in patterns:
                pattern = Pattern(
                    pattern=pattern_def["pattern"],
                    confidence=pattern_def.get("confidence", 0.5),
                    description=pattern_def.get("description", ""),
                    category=category,
                )
                self.registry.add_pattern(pattern)

    def detect(self, text: str) -> Dict[str, List[PatternMatch]]:
        """
        Detect risks in text using pattern matching.

        Args:
            text: Chat text to analyze

        Returns:
            Dictionary mapping category to list of matches
        """
        matches_by_category: Dict[str, List[PatternMatch]] = {}

        for pattern in self.registry.get_all_patterns():
            regex = re.compile(pattern.pattern)
            for match in regex.finditer(text):
                pattern_match = PatternMatch(
                    pattern=pattern,
                    matched_text=match.group(0),
                    position=match.start(),
                    confidence=pattern.confidence,
                )

                if pattern.category not in matches_by_category:
                    matches_by_category[pattern.category] = []
                matches_by_category[pattern.category].append(pattern_match)

        return matches_by_category

    def get_category_score(self, matches: List[PatternMatch]) -> float:
        """
        Calculate aggregated score for a category based on matches.

        Args:
            matches: List of pattern matches

        Returns:
            Aggregated confidence score (0.0 - 1.0)
        """
        if not matches:
            return 0.0

        # Use maximum confidence as base, with reduced boost for multiple matches
        # Reduced boost to prevent over-sensitivity: max 0.1 instead of 0.2
        max_confidence = max(m.confidence for m in matches)
        # Only add boost if there are 3+ matches (multiple patterns indicate stronger signal)
        match_count_boost = min((len(matches) - 1) * 0.05, 0.1) if len(matches) >= 3 else 0.0

        return min(max_confidence + match_count_boost, 1.0)

    def analyze(self, text: str) -> Dict[str, any]:
        """
        Perform complete analysis of text.

        Args:
            text: Chat text to analyze

        Returns:
            Dictionary with category scores and matches
        """
        matches_by_category = self.detect(text)

        category_scores = {}
        for category, matches in matches_by_category.items():
            category_scores[category] = self.get_category_score(matches)

        return {
            "category_scores": category_scores,
            "matches": matches_by_category,
        }

