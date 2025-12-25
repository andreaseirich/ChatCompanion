"""Main detection engine orchestrator."""

import logging
from typing import Dict, Optional

from app.detection.aggregator import ScoreAggregator
from app.detection.explainer import ExplanationGenerator
from app.models_local.classifier import RiskClassifier
from app.models_local.embeddings import EmbeddingModel
from app.rules.rule_engine import RuleEngine
from app.utils.constants import RiskCategory, RiskLevel
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
                    logger.info("ML models available - using hybrid detection")
                else:
                    logger.warning("ML models not available - using rules-only mode")
            except Exception as e:
                logger.warning(f"Failed to initialize ML models: {e}. Using rules-only mode.")

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

        # Run ML classifier if available
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
            except Exception as e:
                logger.error(f"Error in ML classification: {e}")

        # Aggregate scores
        if ml_scores:
            category_scores = self.aggregator.aggregate_category_scores(
                rules_scores, ml_scores
            )
        else:
            # Rules-only mode
            category_scores = rules_scores
            # Adjust aggregator weights for rules-only
            self.aggregator.rules_weight = 1.0
            self.aggregator.ml_weight = 0.0

        # Calculate overall risk score
        overall_score = self.aggregator.get_overall_risk_score(category_scores)

        # Determine risk level
        risk_level = self._determine_risk_level(overall_score)

        # Generate explanation
        explanation = self.explainer.generate_explanation(
            risk_level, category_scores, matches
        )

        # Get advice
        advice = self.explainer.get_help_advice()

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
        # Adjusted thresholds: RED requires 0.8+ (clearly severe patterns)
        if score >= 0.8:
            return RiskLevel.RED
        elif score >= 0.3:
            return RiskLevel.YELLOW
        else:
            return RiskLevel.GREEN

