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

