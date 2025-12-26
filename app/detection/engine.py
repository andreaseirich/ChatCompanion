"""Main detection engine orchestrator."""

import logging
from typing import Dict, Optional

from app.detection.aggregator import ScoreAggregator
from app.detection.explainer import ExplanationGenerator
from app.models_local.classifier import RiskClassifier
from app.models_local.embeddings import EmbeddingModel
from app.rules.rule_engine import RuleEngine
from app.utils.constants import RiskCategory, RiskLevel, RISK_THRESHOLDS
from app.utils.text_processing import normalize_text, segment_sentences

logger = logging.getLogger(__name__)


class DetectionResult:
    """Result of risk detection analysis."""

    def __init__(
        self,
        risk_level: RiskLevel,
        overall_score: float,
        category_scores: Dict[str, float],
        explanation: str,
        advice: list,
        matches: Dict[str, list],
        ml_available: bool,
    ):
        self.risk_level = risk_level
        self.overall_score = overall_score
        self.category_scores = category_scores
        self.explanation = explanation
        self.advice = advice
        self.matches = matches
        self.ml_available = ml_available


class DetectionEngine:
    """Main orchestrator for risk detection."""

    def __init__(
        self,
        rules_config_path: Optional[str] = None,
        use_ml: bool = True,
        rules_weight: float = 0.6,
        ml_weight: float = 0.4,
    ):
        """
        Initialize detection engine.

        Args:
            rules_config_path: Path to rules configuration YAML file
            use_ml: Whether to use ML models (falls back to rules-only if unavailable)
            rules_weight: Weight for rule-based scores
            ml_weight: Weight for ML-based scores
        """
        self.rule_engine = RuleEngine(
            rules_config_path=None if rules_config_path is None else rules_config_path
        )
        self.aggregator = ScoreAggregator(rules_weight=rules_weight, ml_weight=ml_weight)
        self.explainer = ExplanationGenerator()

        # Initialize ML components (may not be available)
        self.use_ml = use_ml
        self.ml_available = False
        self.classifier = None

        if use_ml:
            try:
                embedding_model = EmbeddingModel()
                if embedding_model.available:
                    self.classifier = RiskClassifier(embedding_model)
                    self.ml_available = True
                    logger.info("=" * 60)
                    logger.info("Running in HYBRID mode (Rules + ML)")
                    logger.info("=" * 60)
                else:
                    self.ml_available = False
                    logger.info("=" * 60)
                    logger.info("Running in RULES-ONLY mode")
                    logger.info("(ML models not available - install via: python scripts/download_models.py)")
                    logger.info("=" * 60)
            except Exception as e:
                self.ml_available = False
                logger.warning(f"Failed to initialize ML models: {e}")
                logger.info("Running in RULES-ONLY mode (fallback)")
        else:
            logger.info("Running in RULES-ONLY mode (ML disabled by configuration)")

    def analyze(self, text: str) -> DetectionResult:
        """
        Perform complete risk analysis on chat text.

        Args:
            text: Chat text to analyze

        Returns:
            DetectionResult with risk level, scores, and explanations
        """
        # Normalize and preprocess text
        normalized_text = normalize_text(text)
        sentences = segment_sentences(normalized_text)

        # Run rules engine
        rules_result = self.rule_engine.analyze(normalized_text)
        rules_scores = rules_result["category_scores"]
        matches = rules_result["matches"]
        
        # Check for friendly teasing context and down-weight bullying if detected
        # This reduces false positives for mutual teasing between friends
        if rules_scores.get("bullying", 0.0) > 0:
            is_friendly_teasing = self._check_friendly_teasing_context(text, normalized_text)
            if is_friendly_teasing:
                # Down-weight bullying score (multiply by 0.4)
                original_bullying_score = rules_scores["bullying"]
                rules_scores["bullying"] = original_bullying_score * 0.4
                logger.debug(
                    f"Friendly teasing detected: down-weighted bullying from {original_bullying_score:.2f} "
                    f"to {rules_scores['bullying']:.2f}"
                )
        
        # Debug logging for detection
        if rules_scores:
            logger.debug(f"Rules detection: {len(rules_scores)} categories with scores > 0")
            for cat, score in rules_scores.items():
                logger.debug(f"  - {cat}: {score:.2f} ({len(matches.get(cat, []))} matches)")
        else:
            logger.debug("Rules detection: No patterns matched")

        # Run ML classifier if available (hybrid mode)
        ml_scores = {}
        if self.ml_available and self.classifier:
            try:
                # Classify each sentence and take maximum
                sentence_scores = self.classifier.classify_batch(sentences)
                if sentence_scores:
                    # Aggregate sentence-level scores
                    for category in RiskCategory:
                        category_str = category.value
                        max_score = max(
                            (s.get(category_str, 0.0) for s in sentence_scores), default=0.0
                        )
                        if max_score > 0:
                            ml_scores[category_str] = max_score
                    
                    if ml_scores:
                        logger.debug(f"ML scores generated: {len(ml_scores)} categories")
            except Exception as e:
                logger.error(f"Error in ML classification: {e}")
                logger.warning("Continuing with rules-only scores")

        # Aggregate scores (hybrid mode if ML available, rules-only otherwise)
        if ml_scores and self.ml_available:
            # Hybrid mode: combine rules (60%) and ML (40%) scores
            category_scores = self.aggregator.aggregate_category_scores(
                rules_scores, ml_scores
            )
            logger.debug(f"Hybrid scoring: {len(rules_scores)} rule categories, {len(ml_scores)} ML categories")
        else:
            # Rules-only mode: use only rule-based scores
            category_scores = rules_scores
            logger.debug(f"Rules-only scoring: {len(rules_scores)} categories")

        # Calculate overall risk score
        overall_score = self.aggregator.get_overall_risk_score(category_scores)

        # Hard rule for GREEN: if all category scores < 0.30 and zero pattern matches → force GREEN
        # This ensures healthy conversations with "no pressure" phrases are correctly classified
        has_any_matches = bool(matches) and any(len(m) > 0 for m in matches.values())
        all_scores_below_threshold = all(score < 0.30 for score in category_scores.values()) if category_scores else True
        
        # Determine risk level
        if all_scores_below_threshold and not has_any_matches:
            # Force GREEN: no matches and all scores below threshold
            risk_level = RiskLevel.GREEN
            overall_score = 0.0  # Reset to 0.0 for truly safe conversations
        else:
            # Rule: Do NOT raise yellow/red unless at least ONE matched pattern exists
            # This prevents false positives from ML-only scores without pattern evidence
            if not has_any_matches:
                # No pattern matches found - force GREEN even if ML scores are high
                risk_level = RiskLevel.GREEN
                overall_score = 0.0
            else:
                risk_level = self._determine_risk_level(overall_score)

        # Generate explanation (with overall_score for context)
        explanation = self.explainer.generate_explanation(
            risk_level, category_scores, matches, overall_score
        )

        # Get context-appropriate advice based on risk level
        advice = self.explainer.get_help_advice(risk_level, overall_score)

        return DetectionResult(
            risk_level=risk_level,
            overall_score=overall_score,
            category_scores=category_scores,
            explanation=explanation,
            advice=advice,
            matches=matches,
            ml_available=self.ml_available,
        )

    def _check_friendly_teasing_context(self, original_text: str, normalized_text: str) -> bool:
        """
        Check if text shows signs of friendly teasing rather than bullying.
        
        Friendly teasing indicators:
        - Mutual teasing (both sides tease)
        - Joking markers ("jk", "lol", "haha", emojis)
        - Positive endings ("all good", "just joking", "no worries")
        - No direct slurs or severe insults
        
        Args:
            original_text: Original text (for emoji detection)
            normalized_text: Normalized text (for pattern matching)
            
        Returns:
            True if friendly teasing context is detected, False otherwise
        """
        import re
        
        # Check for joking markers
        joking_patterns = [
            r"\b(jk|just kidding|just joking|kidding|joking)\b",
            r"\b(lol|haha|hehe|hahaha)\b",
            r"\b(all good|no worries|no problem|it's fine|it's okay)\b",
            r"\b(just joking|just kidding|only joking)\b",
        ]
        has_joking_markers = any(
            re.search(pattern, normalized_text, re.IGNORECASE) 
            for pattern in joking_patterns
        )
        
        # Check for emojis (common in friendly teasing)
        # Use explicit emoji ranges to avoid CodeQL warnings about overly large ranges
        # Match common emoji ranges: Emoticons, Miscellaneous Symbols, Dingbats, etc.
        emoji_pattern = r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U00002600-\U000026FF\U00002700-\U000027BF]"
        has_emojis = bool(re.search(emoji_pattern, original_text))
        
        # Check for positive endings
        positive_endings = [
            r"\b(all good|no worries|it's fine|it's okay|just joking|no problem)\b",
        ]
        has_positive_ending = any(
            re.search(pattern, normalized_text, re.IGNORECASE)
            for pattern in positive_endings
        )
        
        # Check for severe insults (if present, it's not friendly teasing)
        severe_insult_patterns = [
            r"\b(kill yourself|kys|go die|worthless|pathetic|dead weight)\b",
            r"\b(you're (so|really|such a) (ugly|stupid|idiot|pathetic))\b",
        ]
        has_severe_insults = any(
            re.search(pattern, normalized_text, re.IGNORECASE)
            for pattern in severe_insult_patterns
        )
        
        # If severe insults are present, it's not friendly teasing
        if has_severe_insults:
            return False
        
        # Check for mutual teasing (both sides have some form of teasing)
        # Simple heuristic: look for multiple speakers and teasing patterns
        lines = original_text.split('\n')
        teasing_indicators = [
            r"\b(you're|you are) (so|really|such a) (slow|bad|terrible|annoying|ridiculous)\b",
            r"\b(being|acting) (so|really|such a) (baby|ridiculous|silly|dumb)\b",
        ]
        teasing_count = sum(
            1 for line in lines
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in teasing_indicators)
        )
        has_mutual_teasing = teasing_count >= 2  # At least 2 instances suggests mutual teasing
        
        # Friendly teasing if:
        # - Has joking markers OR emojis OR positive ending
        # - AND (mutual teasing OR no severe insults)
        is_friendly = (
            (has_joking_markers or has_emojis or has_positive_ending) and
            (has_mutual_teasing or not has_severe_insults)
        )
        
        return is_friendly

    def _determine_risk_level(self, score: float) -> RiskLevel:
        """
        Determine risk level from score.

        Args:
            score: Overall risk score (0.0 - 1.0)

        Returns:
            RiskLevel (GREEN, YELLOW, or RED)
        """
        # Updated thresholds: RED requires 0.75+ (severe patterns or high-risk combinations)
        if score >= RISK_THRESHOLDS[RiskLevel.RED]:
            return RiskLevel.RED
        elif score >= RISK_THRESHOLDS[RiskLevel.YELLOW]:
            return RiskLevel.YELLOW
        else:
            return RiskLevel.GREEN

