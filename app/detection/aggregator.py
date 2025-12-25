"""Score aggregation logic for combining rules and ML results."""

from typing import Dict

from app.utils.constants import RiskCategory


class ScoreAggregator:
    """Aggregates risk scores from multiple sources."""

    def __init__(self, rules_weight: float = 0.6, ml_weight: float = 0.4):
        """
        Initialize aggregator with weights.

        Args:
            rules_weight: Weight for rule-based scores (default 0.6)
            ml_weight: Weight for ML-based scores (default 0.4)
        """
        total_weight = rules_weight + ml_weight
        if total_weight > 0:
            self.rules_weight = rules_weight / total_weight
            self.ml_weight = ml_weight / total_weight
        else:
            # Fallback: use rules only
            self.rules_weight = 1.0
            self.ml_weight = 0.0

    def aggregate_category_scores(
        self, rules_scores: Dict[str, float], ml_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Aggregate scores from rules and ML for each category.

        Args:
            rules_scores: Category scores from rules engine
            ml_scores: Category scores from ML classifier

        Returns:
            Aggregated category scores
        """
        all_categories = set(rules_scores.keys()) | set(ml_scores.keys())
        aggregated = {}

        for category in all_categories:
            rules_score = rules_scores.get(category, 0.0)
            ml_score = ml_scores.get(category, 0.0)

            # Weighted combination
            combined = (rules_score * self.rules_weight) + (ml_score * self.ml_weight)
            aggregated[category] = min(combined, 1.0)  # Cap at 1.0

        return aggregated

    def get_overall_risk_score(self, category_scores: Dict[str, float]) -> float:
        """
        Calculate overall risk score from category scores.

        Args:
            category_scores: Dictionary of category -> score

        Returns:
            Overall risk score (0.0 - 1.0)
        """
        if not category_scores:
            return 0.0

        scores = list(category_scores.values())
        max_score = max(scores)
        
        # If there's a clearly severe pattern (>=0.8), use it directly
        if max_score >= 0.8:
            return max_score
        
        # For moderate scores, require multiple categories to reach high risk
        # This reduces false positives from single weak signals
        if len(scores) >= 2:
            # If multiple categories are flagged, use weighted average
            # This prevents single moderate signal from triggering high risk
            avg_score = sum(scores) / len(scores)
            # Combine max and average: max gives weight to strongest signal,
            # but average prevents single moderate signal from dominating
            combined = (max_score * 0.7) + (avg_score * 0.3)
            return min(combined, 1.0)
        
        # Single category: use the score directly (but threshold is now 0.8 for RED)
        return max_score

