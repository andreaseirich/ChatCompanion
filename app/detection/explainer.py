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

    # Advice messages
    ADVICE_MESSAGES = [
        "Remember: you have the right to feel safe and respected.",
        "It's okay to say no, even to friends or people you know.",
        "Trust your feelings. If something feels wrong, it probably is.",
        "Talk to a trusted adult: a parent, teacher, counselor, or family member.",
        "You are not alone. There are people who want to help you.",
    ]

    def generate_explanation(
        self,
        risk_level: RiskLevel,
        category_scores: Dict[str, float],
        matches: Dict[str, List[PatternMatch]],
    ) -> str:
        """
        Generate child-friendly explanation for detected risks.

        Args:
            risk_level: Overall risk level (green/yellow/red)
            category_scores: Scores for each risk category
            matches: Pattern matches by category

        Returns:
            Child-friendly explanation text
        """
        if risk_level == RiskLevel.GREEN:
            return (
                "This conversation looks okay. Remember to always trust your feelings "
                "and talk to a trusted adult if something doesn't feel right."
            )

        # Find the highest-risk categories
        sorted_categories = sorted(
            category_scores.items(), key=lambda x: x[1], reverse=True
        )
        top_category = sorted_categories[0][0] if sorted_categories else None

        explanation_parts = []

        # Add category-specific explanation
        if top_category and top_category in self.EXPLANATIONS:
            explanation_parts.append(self.EXPLANATIONS[top_category])

        # Add risk level context
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

    def get_help_advice(self) -> List[str]:
        """
        Get list of help advice messages.

        Returns:
            List of advice strings
        """
        return self.ADVICE_MESSAGES.copy()

