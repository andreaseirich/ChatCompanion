"""Rule engine for pattern-based risk detection."""

import re
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from app.rules.patterns import Pattern, PatternMatch, PatternRegistry
from app.utils.constants import RiskCategory
from app.utils.text_processing import get_sentence_context, segment_sentences


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

    def _check_pressure_context(self, text: str, match_position: int, matched_text: str) -> bool:
        """
        Check if "right now"/"now" appears in a demand context (not self-report).
        Includes cross-sentence coercion detection.

        Args:
            text: Full text
            match_position: Position of the match in text
            matched_text: The matched text (e.g., "right now", "now")

        Returns:
            True if match is in demand context (should be counted as pressure),
            False if it's a self-report (should NOT be counted as pressure)
        """
        # Only apply context gating to "right now" or "now" patterns
        if not re.search(r"(?i)\b(right now|now)\b", matched_text):
            return True  # Not a time phrase pattern, always count
        
        # Get sentence context (±1 sentence window for cross-sentence coercion)
        context = get_sentence_context(text, match_position, window=1)
        context_lower = context.lower()
        
        # Self-report exclusion patterns (NOT pressure)
        # Include normalized forms: "I'm busy rn", "not rn", "can't rn", "brb rn" (be right back right now)
        self_report_patterns = [
            r"\b(i'?m|i am|i'm) (busy|not available|unavailable) (right now|now|rn)\b",
            r"\b(not|can'?t|cannot) (right now|now|rn)\b",
            r"\b(can we|can you) (talk|chat) (later|after|tomorrow)\b",
            r"\b(no pressure|take your time|whenever)\b",
            r"\b(be right back|brb) (right now|now|rn)\b",  # "brb rn" -> "be right back right now"
        ]
        
        # If self-report pattern found, it's NOT pressure
        for pattern in self_report_patterns:
            if re.search(pattern, context_lower):
                return False
        
        # Demand indicators (IS pressure)
        # Includes cross-sentence coercion: demand verb in one sentence, time urgency in another
        demand_indicators = [
            # Imperative verbs (can be in previous/next sentence)
            r"\b(answer|reply|call|do it|send|prove|decide|respond|tell me|show me|delete|share)\b",
            # Coercive phrasing
            r"\b(you (have to|must|need to|should))\b",
            r"\b(no excuses|don'?t get time|no more time)\b",
            # Ultimatum markers
            r"\b(or else|if you don'?t|we'?re done|don'?t expect)\b",
        ]
        
        # Check if any demand indicator is present in context (including cross-sentence)
        for indicator in demand_indicators:
            if re.search(indicator, context_lower):
                return True  # Demand context - count as pressure
        
        # Cross-sentence coercion check:
        # If time urgency token is in sentence N and demand verb in sentence N-1 or N+1
        sentences = segment_sentences(text)
        current_sentence_idx = -1
        
        # Find which sentence contains the match
        current_pos = 0
        for i, sentence in enumerate(sentences):
            sentence_end = current_pos + len(sentence)
            if current_pos <= match_position < sentence_end:
                current_sentence_idx = i
                break
            current_pos = sentence_end + 1
        
        if current_sentence_idx >= 0:
            # Check adjacent sentences for demand verbs
            for offset in [-1, 1]:
                check_idx = current_sentence_idx + offset
                if 0 <= check_idx < len(sentences):
                    adjacent_sentence = sentences[check_idx].lower()
                    # Check for demand verbs in adjacent sentence
                    if re.search(r"\b(answer|reply|call|do it|send|prove|decide|respond|tell me|show me|you (have to|must|need to))\b", adjacent_sentence):
                        return True  # Cross-sentence coercion detected
        
        # Default: if no clear demand context, be conservative and count it
        # (better to have false positive than miss real pressure)
        return True

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
                matched_text = match.group(0)
                match_position = match.start()
                
                # Apply context gating for pressure patterns with "right now"/"now"
                if pattern.category == "pressure":
                    if not self._check_pressure_context(text, match_position, matched_text):
                        # Context gate failed - skip this match
                        continue
                
                pattern_match = PatternMatch(
                    pattern=pattern,
                    matched_text=matched_text,
                    position=match_position,
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

        # Use maximum confidence as base, with boost for multiple matches
        # Multiple matches in same category indicate stronger pattern
        max_confidence = max(m.confidence for m in matches)
        
        # Boost calculation: more matches = stronger signal
        # 2 matches: +0.05, 3+ matches: +0.1-0.2 (capped)
        # Increased boost for secrecy/isolation patterns to better surface them
        if len(matches) >= 3:
            match_count_boost = min((len(matches) - 2) * 0.05, 0.2)
        elif len(matches) >= 2:
            match_count_boost = 0.05
        else:
            match_count_boost = 0.0

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

        # Suppression logic: Check for explicit "no pressure" phrases
        # These MUST suppress pressure detection unless there is a clear contradiction
        no_pressure_phrases = [
            r"(?i)\b(no pressure|that's okay|take your time|whenever you can|no rush|no hurry)\b",
            r"(?i)\b(it's (fine|okay|alright) (if|that) you (can't|don't|won't))\b",
            r"(?i)\b(no worries|don't worry|it's fine)\b",
            r"(?i)\b(don't rush|only if you have time|whenever you're ready)\b",
            r"(?i)\b(no need to (hurry|rush|worry)|there's no rush)\b",
        ]
        
        # Check if suppression phrases are present
        has_suppression = any(re.search(phrase, text) for phrase in no_pressure_phrases)
        
        # Check for contradictions (pressure patterns that override suppression)
        has_contradiction = False
        if has_suppression and "pressure" in matches_by_category:
            pressure_matches = matches_by_category["pressure"]
            # Strong pressure patterns override suppression
            strong_pressure_indicators = [
                "ultimatum", "threat", "or else", "we're done", "must", "have to"
            ]
            for match in pressure_matches:
                matched_text_lower = match.matched_text.lower()
                if any(indicator in matched_text_lower for indicator in strong_pressure_indicators):
                    has_contradiction = True
                    break
        
        # Apply suppression: remove pressure matches if suppression present and no contradiction
        if has_suppression and not has_contradiction and "pressure" in matches_by_category:
            # Suppress pressure detection - remove matches
            matches_by_category["pressure"] = []

        # Recalculate category scores AFTER suppression
        # This ensures suppressed categories have score 0.0
        category_scores = {}
        for category, matches in matches_by_category.items():
            category_scores[category] = self.get_category_score(matches)

        return {
            "category_scores": category_scores,
            "matches": matches_by_category,
        }

