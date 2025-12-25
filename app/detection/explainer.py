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

    # Advice messages - context-appropriate based on risk level
    # These are base messages, will be filtered/selected by risk level
    ADVICE_MESSAGES_GREEN = [
        "This conversation looks mostly okay.",
        "There might be some stress or disagreement, but overall it does not show strong signs of bullying or manipulation.",
    ]
    
    ADVICE_MESSAGES_YELLOW = [
        "There are some tense or uncomfortable parts in this conversation.",
        "It can help to set clear boundaries and talk honestly about how you feel.",
    ]
    
    ADVICE_MESSAGES_RED = [
        "This conversation shows serious warning signs.",
        "If you feel unsafe or pressured, talk to a trusted adult (parent, teacher, counselor or another person you trust) as soon as possible.",
    ]

    def generate_explanation(
        self,
        risk_level: RiskLevel,
        category_scores: Dict[str, float],
        matches: Dict[str, List[PatternMatch]],
        overall_score: float = 0.0,
    ) -> str:
        """
        Generate context-appropriate explanation for detected risks.

        Args:
            risk_level: Overall risk level (green/yellow/red)
            category_scores: Scores for each risk category
            matches: Pattern matches by category
            overall_score: Overall risk score (0.0 - 1.0)

        Returns:
            Context-appropriate explanation text
        """
        # Context-appropriate guidance based on risk level
        if risk_level == RiskLevel.GREEN or overall_score < 0.3:
            # Neutral, context-agnostic message for low-risk conversations
            return (
                "This conversation looks mostly okay. There might be some stress or disagreement, "
                "but overall it does not show strong signs of bullying or manipulation."
            )

        # Find the highest-risk categories
        sorted_categories = sorted(
            category_scores.items(), key=lambda x: x[1], reverse=True
        )
        top_category = sorted_categories[0][0] if sorted_categories else None

        explanation_parts = []

        # Add category-specific explanation (only for YELLOW/RED)
        if top_category and top_category in self.EXPLANATIONS:
            # Adjust category explanations to be less child-focused for YELLOW
            if risk_level == RiskLevel.YELLOW:
                # Use milder, more general language
                category_explanation = self.EXPLANATIONS[top_category]
                # Remove "trusted adult" references for YELLOW
                category_explanation = category_explanation.replace("trusted adult", "someone you trust")
                explanation_parts.append(category_explanation)
            else:
                # RED: keep original child-focused explanation
                explanation_parts.append(self.EXPLANATIONS[top_category])

        # Add risk level context with appropriate severity
        if risk_level == RiskLevel.RED:
            explanation_parts.append(
                "\n\n⚠️ This is a high-risk situation. Please talk to a trusted adult "
                "right away."
            )
        elif risk_level == RiskLevel.YELLOW:
            explanation_parts.append(
                "\n\n⚠️ Be careful with this conversation. Pay attention to how it "
                "makes you feel."
            )

        # Add specific evidence if available
        if matches:
            evidence = self._extract_evidence(matches)
            if evidence:
                explanation_parts.append(f"\n\nSome concerning things we noticed: {evidence}")

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

