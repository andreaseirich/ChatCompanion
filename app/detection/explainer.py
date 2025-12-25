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
        # BUT: Only say "no strong patterns" if there are truly NO matches or very weak ones
        has_any_matches = bool(matches) and any(len(m) > 0 for m in matches.values())
        has_meaningful_scores = any(score >= 0.3 for score in category_scores.values())
        
        if (risk_level == RiskLevel.GREEN or overall_score < 0.3) and not has_meaningful_scores:
            explanation_parts.append(
                "Analysis checked for patterns of bullying, manipulation, pressure, secrecy demands, "
                "guilt-shifting, and grooming indicators."
            )
            explanation_parts.append(
                "No strong patterns of these risky behaviors were detected in this conversation."
            )
            if matches and has_any_matches:
                # Even in GREEN, if there are weak matches, mention them
                evidence = self._extract_evidence(matches)
                if evidence:
                    explanation_parts.append(
                        f"Some mild patterns were noted but are not concerning: {evidence}"
                    )
            return " ".join(explanation_parts)
        
        # If we have matches but still GREEN, it means weak signals - be more specific
        if risk_level == RiskLevel.GREEN and has_any_matches:
            explanation_parts.append(
                "Analysis detected some patterns, but they appear to be isolated or mild."
            )
            evidence = self._extract_evidence(matches)
            if evidence:
                explanation_parts.append(f"Patterns noted: {evidence}")
            return " ".join(explanation_parts)

        # For YELLOW/RED: Explain what WAS detected with specific details
        # Include ALL detected categories, not just top 3
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
            
            # List ALL detected categories (primary and secondary)
            high_score_cats = [cat for cat, score in detected_categories if score >= 0.6]
            moderate_cats = [cat for cat, score in detected_categories if 0.3 <= score < 0.6]
            
            all_detected = []
            if high_score_cats:
                high_names = [category_names.get(cat, cat) for cat in high_score_cats]
                all_detected.extend(high_names)
            if moderate_cats:
                mod_names = [category_names.get(cat, cat) for cat in moderate_cats]
                all_detected.extend(mod_names)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_detected = []
            for name in all_detected:
                if name not in seen:
                    seen.add(name)
                    unique_detected.append(name)
            
            if unique_detected:
                # Primary category (highest score) and secondary categories
                primary = unique_detected[0] if unique_detected else None
                secondary = unique_detected[1:] if len(unique_detected) > 1 else []
                
                if primary:
                    if secondary:
                        explanation_parts.append(
                            f"Analysis detected patterns of {primary}, "
                            f"with secondary patterns of {', '.join(secondary)}."
                        )
                    else:
                        explanation_parts.append(
                            f"Analysis detected patterns of {primary}."
                        )

        # Add behavioral context explanation (focus on conversation dynamics)
        # Instead of generic category explanations, describe what's happening
        if detected_categories:
            top_category = detected_categories[0][0]
            top_score = detected_categories[0][1]
            
            # Provide context-specific explanation based on primary category
            if top_category == "pressure" and top_score >= 0.6:
                explanation_parts.append(
                    "This conversation shows repeated pressure to act quickly, with threats of "
                    "consequences if demands are not met."
                )
            elif top_category == "manipulation" and top_score >= 0.6:
                explanation_parts.append(
                    "This person is using emotional pressure and conditional statements to control "
                    "your behavior or invade your privacy."
                )
            elif top_category == "guilt_shifting" and top_score >= 0.6:
                explanation_parts.append(
                    "This conversation includes attempts to make you feel responsible for the other "
                    "person's actions or emotions."
                )
            elif risk_level == RiskLevel.YELLOW:
                # For YELLOW, use milder language
                if top_category in self.EXPLANATIONS:
                    category_explanation = self.EXPLANATIONS[top_category]
                    category_explanation = category_explanation.replace("trusted adult", "someone you trust")
                    category_explanation = category_explanation.replace("kids", "people")
                    explanation_parts.append(category_explanation)
            elif risk_level == RiskLevel.RED:
                # For RED, use full explanation
                if top_category in self.EXPLANATIONS:
                    explanation_parts.append(self.EXPLANATIONS[top_category])

        # Add behavioral description instead of raw keyword quotes
        # Describe what behaviors were observed in conversational context
        if matches:
            behavior_descriptions = self._describe_behaviors(matches, category_scores, detected_categories)
            if behavior_descriptions:
                explanation_parts.append(f"\n\nObserved behaviors: {behavior_descriptions}")

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
        Extract evidence snippets from matches (for weak signals only).

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

    def _describe_behaviors(
        self, 
        matches: Dict[str, List[PatternMatch]], 
        category_scores: Dict[str, float],
        detected_categories: List[tuple]
    ) -> str:
        """
        Describe observed behaviors in conversational context, not just keywords.
        Focus on behavior patterns and dynamics, not isolated trigger words.

        Args:
            matches: Pattern matches by category
            category_scores: Scores for each category
            detected_categories: List of (category, score) tuples, sorted by score

        Returns:
            Behavioral description string focusing on conversation dynamics
        """
        behavior_parts = []
        
        # Process categories in order of significance (highest score first)
        for category, score in detected_categories:
            if score < 0.3:
                continue
                
            category_matches = matches.get(category, [])
            if not category_matches:
                continue
                
            match_count = len(category_matches)
            
            # Describe behaviors based on category and match patterns
            # Focus on conversational dynamics, not keywords
            if category == "pressure":
                # Analyze pressure patterns
                has_ultimatums = any(
                    "ultimatum" in m.pattern.description.lower() or 
                    "threat" in m.pattern.description.lower() or
                    "done" in m.matched_text.lower() or
                    "over" in m.matched_text.lower()
                    for m in category_matches
                )
                has_time_pressure = any(
                    "faster" in m.matched_text.lower() or 
                    "respond" in m.matched_text.lower() or
                    "minutes" in m.matched_text.lower()
                    for m in category_matches
                )
                
                if has_ultimatums:
                    behavior_parts.append("threats of withdrawal or relationship consequences")
                elif has_time_pressure and match_count >= 2:
                    behavior_parts.append("repeated demands for immediate response")
                elif match_count >= 3:
                    behavior_parts.append("repeated demands for immediate action")
                else:
                    behavior_parts.append("pressure to comply with demands")
            
            elif category == "manipulation":
                # Analyze manipulation patterns
                has_privacy_invasion = any(
                    "prove" in m.matched_text.lower() or 
                    "screenshot" in m.matched_text.lower() or
                    "show me" in m.matched_text.lower()
                    for m in category_matches
                )
                has_trust_manipulation = any(
                    "trust" in m.matched_text.lower() or
                    "don't trust" in m.matched_text.lower()
                    for m in category_matches
                )
                has_conditional = any(
                    "if you" in m.matched_text.lower() or
                    "care" in m.matched_text.lower() or
                    "love" in m.matched_text.lower()
                    for m in category_matches
                )
                
                if has_privacy_invasion:
                    behavior_parts.append("requests that invade privacy (e.g., screenshots)")
                elif has_trust_manipulation:
                    behavior_parts.append("threats of withdrawal of trust")
                elif has_conditional:
                    behavior_parts.append("conditional statements implying negative consequences")
                elif match_count >= 2:
                    behavior_parts.append("repeated attempts to control behavior through emotional pressure")
                else:
                    behavior_parts.append("attempts to manipulate through emotional pressure")
            
            elif category == "guilt_shifting":
                if match_count >= 2:
                    behavior_parts.append("repeated guilt induction and blame-shifting")
                else:
                    behavior_parts.append("attempts to shift blame or induce guilt")
            
            elif category == "bullying":
                behavior_parts.append("mean comments or personal attacks")
            
            elif category == "secrecy":
                behavior_parts.append("demands to keep secrets from trusted people")
            
            elif category == "grooming":
                behavior_parts.append("inappropriate trust-building attempts")
        
        # Limit to most significant behaviors (3-4 max), prioritize by score
        if len(behavior_parts) > 4:
            behavior_parts = behavior_parts[:4]
        
        if behavior_parts:
            # Join with natural language
            if len(behavior_parts) == 1:
                return behavior_parts[0]
            elif len(behavior_parts) == 2:
                return f"{behavior_parts[0]} and {behavior_parts[1]}"
            else:
                return f"{', '.join(behavior_parts[:-1])}, and {behavior_parts[-1]}"
        
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

