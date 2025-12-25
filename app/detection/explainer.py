"""Explanation generation for risk detection results."""

from typing import Dict, List

from app.rules.patterns import PatternMatch
from app.utils.constants import RiskCategory, RiskLevel


class ExplanationGenerator:
    """Generates child-friendly explanations for detected risks."""

    # Child-friendly explanations for each risk category
    EXPLANATIONS = {
        RiskCategory.BULLYING: (
            "Someone is saying mean things to you. This is not okay. "
            "You don't deserve to be treated this way. It's important to talk to "
            "a trusted adult about this."
        ),
        RiskCategory.MANIPULATION: (
            "This person is trying to make you feel like you have to do something "
            "you don't want to do. They might be using your friendship or feelings "
            "against you. Remember: real friends respect your boundaries."
        ),
        RiskCategory.PRESSURE: (
            "Someone is pushing you to do something quickly or without thinking. "
            "It's okay to take your time and say no. You don't have to do anything "
            "that makes you uncomfortable."
        ),
        RiskCategory.SECRECY: (
            "Someone is asking you to keep secrets from adults you trust. "
            "This is a warning sign. Safe adults don't ask kids to keep secrets. "
            "It's important to tell a trusted adult about this."
        ),
        RiskCategory.GUILT_SHIFTING: (
            "This person is trying to make you feel bad or blame you for something. "
            "This is not fair. You are not responsible for someone else's actions. "
            "Talk to someone you trust about how this makes you feel."
        ),
        RiskCategory.GROOMING: (
            "This conversation has some concerning patterns. Someone might be trying "
            "to build trust in an inappropriate way. This is very serious. "
            "Please talk to a trusted adult immediately."
        ),
    }

    # Advice messages - context-appropriate, non-repetitive, specific to risk level
    ADVICE_MESSAGES_GREEN = [
        "No strong patterns of bullying, manipulation, or grooming were detected.",
    ]
    
    ADVICE_MESSAGES_YELLOW = [
        "Some patterns of pressure or discomfort were detected.",
        "Consider setting clear boundaries and communicating your concerns directly.",
    ]
    
    ADVICE_MESSAGES_RED = [
        "Serious warning signs detected: bullying, manipulation, or grooming patterns.",
        "If you feel unsafe, talk to a trusted adult (parent, teacher, counselor) immediately.",
    ]

    def generate_explanation(
        self,
        risk_level: RiskLevel,
        category_scores: Dict[str, float],
        matches: Dict[str, List[PatternMatch]],
        overall_score: float = 0.0,
    ) -> str:
        """
        Generate context-appropriate, specific explanation for detected risks.

        Args:
            risk_level: Overall risk level (green/yellow/red)
            category_scores: Scores for each risk category
            matches: Pattern matches by category
            overall_score: Overall risk score (0.0 - 1.0)

        Returns:
            Context-appropriate, specific explanation text
        """
        # Build explanation based on what was actually detected
        explanation_parts = []
        
        # For GREEN: Explain what was analyzed and what was NOT found
        if risk_level == RiskLevel.GREEN or overall_score < 0.3:
            explanation_parts.append(
                "Analysis checked for patterns of bullying, manipulation, pressure, secrecy demands, "
                "guilt-shifting, and grooming indicators."
            )
            explanation_parts.append(
                "No strong patterns of these risky behaviors were detected in this conversation."
            )
            if matches:
                # Even in GREEN, if there are weak matches, mention them
                evidence = self._extract_evidence(matches)
                if evidence:
                    explanation_parts.append(
                        f"Some mild patterns were noted but are not concerning: {evidence}"
                    )
            return " ".join(explanation_parts)

        # For YELLOW/RED: Explain what WAS detected with specific details
        detected_categories = [(cat, score) for cat, score in category_scores.items() if score > 0]
        detected_categories.sort(key=lambda x: x[1], reverse=True)  # Sort by score
        
        if detected_categories:
            category_names = {
                "bullying": "bullying",
                "manipulation": "manipulation",
                "pressure": "pressure",
                "secrecy": "secrecy demands",
                "guilt_shifting": "guilt-shifting",
                "grooming": "grooming indicators",
            }
            
            # List detected categories with emphasis on high-scoring ones
            high_score_cats = [cat for cat, score in detected_categories if score >= 0.6]
            moderate_cats = [cat for cat, score in detected_categories if 0.3 <= score < 0.6]
            
            if high_score_cats:
                high_names = [category_names.get(cat, cat) for cat in high_score_cats[:3]]
                explanation_parts.append(
                    f"Analysis detected strong patterns of: {', '.join(high_names)}."
                )
            if moderate_cats and not high_score_cats:
                mod_names = [category_names.get(cat, cat) for cat in moderate_cats[:3]]
                explanation_parts.append(
                    f"Analysis detected patterns of: {', '.join(mod_names)}."
                )

        # Find the highest-risk category for specific explanation
        sorted_categories = sorted(
            category_scores.items(), key=lambda x: x[1], reverse=True
        )
        top_category = sorted_categories[0][0] if sorted_categories else None

        # Add category-specific explanation (only for YELLOW/RED)
        if top_category and top_category in self.EXPLANATIONS:
            # Adjust category explanations to be context-appropriate
            if risk_level == RiskLevel.YELLOW:
                # Use milder, more general language for YELLOW
                category_explanation = self.EXPLANATIONS[top_category]
                # Remove "trusted adult" and child-focused language for YELLOW
                category_explanation = category_explanation.replace("trusted adult", "someone you trust")
                category_explanation = category_explanation.replace("kids", "people")
                category_explanation = category_explanation.replace("kids", "people")
                explanation_parts.append(category_explanation)
            else:
                # RED: keep original child-focused explanation
                explanation_parts.append(self.EXPLANATIONS[top_category])

        # Add specific evidence - always show what was detected
        if matches:
            evidence = self._extract_evidence(matches)
            if evidence:
                explanation_parts.append(f"\n\nSpecific patterns detected: {evidence}")

        # Add risk level context with appropriate severity
        if risk_level == RiskLevel.RED:
            explanation_parts.append(
                "\n\n⚠️ This is a high-risk situation requiring immediate attention."
            )
        elif risk_level == RiskLevel.YELLOW:
            explanation_parts.append(
                "\n\n⚠️ Moderate concern: pay attention to how this conversation makes you feel."
            )

        return " ".join(explanation_parts)

    def _extract_evidence(self, matches: Dict[str, List[PatternMatch]]) -> str:
        """
        Extract evidence snippets from matches.

        Args:
            matches: Pattern matches by category

        Returns:
            Formatted evidence string
        """
        evidence_items = []
        for category, category_matches in matches.items():
            if category_matches:
                # Get first few matches as examples
                examples = category_matches[:2]
                for match in examples:
                    # Truncate long matches
                    text = match.matched_text
                    if len(text) > 50:
                        text = text[:47] + "..."
                    evidence_items.append(f'"{text}"')

        if evidence_items:
            return ", ".join(evidence_items[:3])  # Limit to 3 examples
        return ""

    def get_help_advice(self, risk_level: RiskLevel, overall_score: float = 0.0) -> List[str]:
        """
        Get context-appropriate help advice messages based on risk level.

        Args:
            risk_level: Overall risk level (green/yellow/red)
            overall_score: Overall risk score (0.0 - 1.0)

        Returns:
            List of context-appropriate advice strings
        """
        # Use risk-level appropriate messages
        if risk_level == RiskLevel.RED or overall_score >= 0.8:
            return self.ADVICE_MESSAGES_RED.copy()
        elif risk_level == RiskLevel.YELLOW or overall_score >= 0.3:
            return self.ADVICE_MESSAGES_YELLOW.copy()
        else:
            return self.ADVICE_MESSAGES_GREEN.copy()

