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
                # Filter out grooming if it's not the primary category and score is low
                # (grooming should only be mentioned if it's actually present)
                primary = unique_detected[0] if unique_detected else None
                secondary = unique_detected[1:] if len(unique_detected) > 1 else []
                
                # Only include grooming in explanation if it's actually high-scoring
                # (grooming should not appear as secondary if score is low)
                if primary == "grooming indicators":
                    # Check if grooming score is actually high
                    grooming_score = next((score for cat, score in detected_categories if cat == "grooming"), 0.0)
                    if grooming_score < 0.6:
                        # Grooming is false positive, remove it and use next category
                        if secondary:
                            primary = secondary[0]
                            secondary = secondary[1:]
                        else:
                            primary = None
                
                # Filter secondary to exclude low-score grooming, but include ALL other detected categories
                # Even if scores are moderate (0.3-0.6), they should be mentioned if clearly present
                filtered_secondary = []
                for sec_cat in secondary:
                    if sec_cat == "grooming indicators":
                        sec_score = next((score for cat, score in detected_categories if cat == "grooming"), 0.0)
                        if sec_score >= 0.6:
                            filtered_secondary.append(sec_cat)
                    else:
                        # Include all non-grooming categories, even with moderate scores
                        # This ensures all clearly present risky behaviors are mentioned
                        filtered_secondary.append(sec_cat)
                
                if primary:
                    if filtered_secondary:
                        explanation_parts.append(
                            f"Analysis detected patterns of {primary}, "
                            f"with secondary patterns of {', '.join(filtered_secondary)}."
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
            
            # Provide context-specific explanation based on primary category and ACTUAL detected patterns
            # Only describe behaviors that were actually detected, not generic templates
            if top_category == "pressure" and top_score >= 0.6:
                # Check what pressure patterns were actually detected
                pressure_matches = matches.get("pressure", [])
                has_blackmail = any(
                    "emotional blackmail" in m.pattern.description.lower() or
                    "friendship threat" in m.pattern.description.lower()
                    for m in pressure_matches
                )
                has_withdrawal = any(
                    "withdrawal" in m.pattern.description.lower() or
                    "threats of withdrawal" in m.pattern.description.lower()
                    for m in pressure_matches
                )
                has_ultimatums = any(
                    "ultimatum" in m.pattern.description.lower() or 
                    "threat" in m.pattern.description.lower() or
                    "relationship threats" in m.pattern.description.lower()
                    for m in pressure_matches
                )
                has_strong_commands = any(
                    "strong pressure" in m.pattern.description.lower() or
                    "commands" in m.pattern.description.lower()
                    for m in pressure_matches
                )
                has_emotional_pressure = any(
                    "emotional pressure" in m.pattern.description.lower() or
                    "respond right now" in m.pattern.description.lower()
                    for m in pressure_matches
                )
                
                if has_blackmail:
                    explanation_parts.append(
                        "This conversation shows emotional blackmail with threats to end the friendship if demands are not met immediately."
                    )
                elif has_withdrawal:
                    explanation_parts.append(
                        "This conversation shows threats of withdrawal of affection or attention if demands are not met."
                    )
                elif has_ultimatums:
                    explanation_parts.append(
                        "This conversation shows repeated pressure with threats of consequences if demands are not met."
                    )
                elif has_strong_commands:
                    explanation_parts.append(
                        "This conversation shows strong pressure commands demanding immediate compliance."
                    )
                elif has_emotional_pressure:
                    explanation_parts.append(
                        "This conversation shows emotional pressure to respond immediately or disclose feelings."
                    )
                else:
                    explanation_parts.append(
                        "This conversation shows repeated pressure to act quickly or comply with demands."
                    )
            elif top_category == "bullying" and top_score >= 0.6:
                # Check what bullying patterns were detected
                bullying_matches = matches.get("bullying", [])
                has_victim_blaming = any(
                    "victim-blaming" in m.pattern.description.lower() or
                    "victim" in m.pattern.description.lower()
                    for m in bullying_matches
                )
                has_demeaning = any(
                    "demeaning" in m.pattern.description.lower() or
                    "put-down" in m.pattern.description.lower()
                    for m in bullying_matches
                )
                has_severe = any(
                    "severe" in m.pattern.description.lower() or
                    m.confidence >= 0.9
                    for m in bullying_matches
                )
                
                if has_victim_blaming and has_demeaning:
                    explanation_parts.append(
                        "This conversation contains direct insults, demeaning language, and victim-blaming statements."
                    )
                elif has_victim_blaming:
                    explanation_parts.append(
                        "This conversation contains victim-blaming statements that shift responsibility and dismiss your concerns."
                    )
                elif has_demeaning:
                    explanation_parts.append(
                        "This conversation contains demeaning language and put-downs designed to hurt and belittle."
                    )
                elif has_severe:
                    explanation_parts.append(
                        "This conversation contains severe threats or extreme insults that are clearly abusive."
                    )
                else:
                    explanation_parts.append(
                        "This conversation contains mean comments and personal attacks."
                    )
            elif top_category == "manipulation" and top_score >= 0.6:
                # Check what manipulation patterns were actually detected
                manip_matches = matches.get("manipulation", [])
                has_coercive = any(
                    "coercive control" in m.pattern.description.lower() or
                    "removing autonomy" in m.pattern.description.lower() or
                    "obedience" in m.pattern.description.lower()
                    for m in manip_matches
                )
                has_fear = any(
                    "fear" in m.pattern.description.lower() or
                    "deliberate use of fear" in m.pattern.description.lower()
                    for m in manip_matches
                )
                has_privacy = any("privacy invasion" in m.pattern.description.lower() for m in manip_matches)
                has_conditional = any(
                    "conditional" in m.pattern.description.lower() or 
                    "guilt-inducing" in m.pattern.description.lower()
                    for m in manip_matches
                )
                has_forced_disclosure = any(
                    "forced emotional disclosure" in m.pattern.description.lower() or
                    "demands for proof" in m.pattern.description.lower()
                    for m in manip_matches
                )
                has_boundary = any("boundaries" in m.pattern.description.lower() for m in manip_matches)
                has_gaslighting = any(
                    "gaslighting" in m.pattern.description.lower() or
                    "reality-questioning" in m.pattern.description.lower() or
                    "perception-questioning" in m.pattern.description.lower()
                    for m in manip_matches
                )
                
                # Priority: describe actual detected behaviors, not generic templates
                # Coercive control and fear are highest priority
                if has_coercive and has_fear:
                    explanation_parts.append(
                        "This person is using coercive control and deliberate fear tactics to force compliance. "
                        "This is a serious pattern of abuse that requires immediate attention."
                    )
                elif has_coercive:
                    explanation_parts.append(
                        "This person is using coercive control to remove your autonomy and demand obedience. "
                        "This is a serious pattern of controlling behavior."
                    )
                elif has_fear:
                    explanation_parts.append(
                        "This person is deliberately using fear to make you comply. This is a serious warning sign."
                    )
                elif has_forced_disclosure and has_conditional:
                    explanation_parts.append(
                        "This person is using guilt-inducing conditional statements and forcing emotional disclosure to control your behavior."
                    )
                elif has_conditional and has_gaslighting:
                    explanation_parts.append(
                        "This person is using guilt-inducing conditional statements and reality-questioning language to control your behavior."
                    )
                elif has_conditional:
                    explanation_parts.append(
                        "This person is using guilt-inducing conditional statements linking care or trust to compliance."
                    )
                elif has_forced_disclosure:
                    explanation_parts.append(
                        "This person is forcing emotional disclosure and demanding proof of feelings."
                    )
                elif has_gaslighting:
                    explanation_parts.append(
                        "This person is using reality-questioning or perception-questioning language to undermine your perspective."
                    )
                elif has_privacy:
                    explanation_parts.append(
                        "This person is using emotional pressure and requests that invade privacy to control your behavior."
                    )
                elif has_boundary:
                    explanation_parts.append(
                        "This person is framing boundaries as rejection or lack of care."
                    )
                else:
                    explanation_parts.append(
                        "This person is using emotional pressure to control your behavior."
                    )
            elif top_category == "guilt_shifting" and top_score >= 0.6:
                explanation_parts.append(
                    "This conversation includes attempts to make you feel responsible for the other "
                    "person's actions or emotions."
                )
            elif top_category == "secrecy" and top_score >= 0.6:
                # Check what secrecy patterns were detected
                secrecy_matches = matches.get("secrecy", [])
                has_isolation = any("isolation" in m.pattern.description.lower() or "discouraging" in m.pattern.description.lower() 
                                  for m in secrecy_matches)
                has_privacy_redef = any("privacy" in m.pattern.description.lower() and "secrecy" in m.pattern.description.lower()
                                       for m in secrecy_matches)
                
                if has_isolation:
                    explanation_parts.append(
                        "This conversation discourages seeking outside support or advice, attempting to isolate you."
                    )
                elif has_privacy_redef:
                    explanation_parts.append(
                        "This conversation redefines privacy as keeping secrets from trusted people."
                    )
                else:
                    explanation_parts.append(
                        "This conversation includes demands to keep secrets from trusted people."
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
                "\n\n⚠️ This is a high-risk situation requiring immediate attention. "
                "Consider getting help from a trusted adult or support service."
            )
        elif risk_level == RiskLevel.YELLOW:
            # Check if multiple strong patterns are present (even if overall score is YELLOW)
            strong_patterns = sum(1 for _, score in detected_categories if score >= 0.75)
            if strong_patterns >= 2:
                explanation_parts.append(
                    "\n\n⚠️ Multiple concerning patterns detected. Pay close attention to how this conversation makes you feel. "
                    "Consider setting clear boundaries or seeking support."
                )
            else:
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
                # Analyze pressure patterns - check pattern descriptions, not matched_text
                has_withdrawal_threats = any(
                    "withdrawal" in m.pattern.description.lower() or
                    "threats of withdrawal" in m.pattern.description.lower()
                    for m in category_matches
                )
                has_ultimatums = any(
                    "ultimatum" in m.pattern.description.lower() or 
                    "threat" in m.pattern.description.lower() or
                    "relationship threats" in m.pattern.description.lower()
                    for m in category_matches
                )
                has_emotional_pressure = any(
                    "emotional pressure" in m.pattern.description.lower() or
                    "respond right now" in m.pattern.description.lower()
                    for m in category_matches
                )
                has_time_pressure = any(
                    "urgency" in m.pattern.description.lower() or
                    "time ultimatums" in m.pattern.description.lower() or
                    "immediate" in m.pattern.description.lower()
                    for m in category_matches
                )
                
                # Priority: specific behaviors first
                if has_withdrawal_threats:
                    behavior_parts.append("threats of withdrawal of affection or attention")
                elif has_ultimatums:
                    behavior_parts.append("threats of withdrawal or relationship consequences")
                elif has_emotional_pressure:
                    behavior_parts.append("emotional pressure to respond right now")
                elif has_time_pressure and match_count >= 2:
                    behavior_parts.append("repeated demands for immediate response")
                elif match_count >= 3:
                    behavior_parts.append("repeated demands for immediate action")
                else:
                    behavior_parts.append("pressure to comply with demands")
            
            elif category == "manipulation":
                # Analyze manipulation patterns - ONLY describe what's actually present
                # Check pattern descriptions to see what was actually matched
                has_privacy_invasion = any(
                    "privacy invasion" in m.pattern.description.lower()
                    for m in category_matches
                )
                has_trust_manipulation = any(
                    "trust manipulation" in m.pattern.description.lower() or
                    ("trust" in m.pattern.description.lower() and "withdrawal" in m.pattern.description.lower())
                    for m in category_matches
                )
                has_conditional = any(
                    "conditional" in m.pattern.description.lower() or
                    ("guilt-inducing" in m.pattern.description.lower()) or
                    ("care" in m.pattern.description.lower() and "compliance" in m.pattern.description.lower())
                    for m in category_matches
                )
                has_forced_disclosure = any(
                    "forced emotional disclosure" in m.pattern.description.lower() or
                    "demands for proof" in m.pattern.description.lower()
                    for m in category_matches
                )
                has_boundary_framing = any(
                    "boundaries" in m.pattern.description.lower() or
                    "rejection" in m.pattern.description.lower()
                    for m in category_matches
                )
                has_isolation = any(
                    "isolation" in m.pattern.description.lower()
                    for m in category_matches
                )
                has_gaslighting = any(
                    "gaslighting" in m.pattern.description.lower() or
                    "reality-questioning" in m.pattern.description.lower() or
                    "perception-questioning" in m.pattern.description.lower()
                    for m in category_matches
                )
                has_coercive = any(
                    "coercive control" in m.pattern.description.lower() or
                    "removing autonomy" in m.pattern.description.lower() or
                    "obedience" in m.pattern.description.lower()
                    for m in category_matches
                )
                has_fear = any(
                    "fear" in m.pattern.description.lower() and "deliberate" in m.pattern.description.lower()
                    for m in category_matches
                )
                
                # Only add descriptions for patterns that were ACTUALLY detected
                # Priority: specific behaviors first, then generic
                if has_coercive:
                    behavior_parts.append("coercive control and removal of autonomy")
                if has_fear:
                    behavior_parts.append("deliberate use of fear for compliance")
                if has_forced_disclosure:
                    behavior_parts.append("forced emotional disclosure")
                if has_conditional:
                    behavior_parts.append("guilt-inducing conditional statements")
                if has_gaslighting:
                    behavior_parts.append("reality-questioning or perception-questioning language")
                if has_privacy_invasion:
                    behavior_parts.append("requests that invade privacy")
                if has_trust_manipulation:
                    behavior_parts.append("threats of withdrawal of trust")
                if has_boundary_framing:
                    behavior_parts.append("framing boundaries as rejection")
                if has_isolation:
                    behavior_parts.append("attempts to isolate from others")
                
                # If no specific patterns matched, use generic description
                if not (has_privacy_invasion or has_trust_manipulation or has_conditional or has_forced_disclosure or has_boundary_framing or has_isolation):
                    if match_count >= 2:
                        behavior_parts.append("repeated attempts to control behavior through emotional pressure")
                    else:
                        behavior_parts.append("attempts to manipulate through emotional pressure")
            
            elif category == "guilt_shifting":
                # Check for specific guilt-shifting patterns
                has_importance_questioning = any(
                    "importance questioning" in m.pattern.description.lower() or
                    "mattered" in m.pattern.description.lower()
                    for m in category_matches
                )
                has_effort_questioning = any(
                    "effort questioning" in m.pattern.description.lower() or
                    "don't care" in m.pattern.description.lower()
                    for m in category_matches
                )
                
                if has_importance_questioning:
                    behavior_parts.append("guilt-shifting through questioning your importance or care")
                elif has_effort_questioning:
                    behavior_parts.append("guilt-shifting through questioning your effort or commitment")
                elif match_count >= 2:
                    behavior_parts.append("repeated guilt induction and blame-shifting")
                else:
                    behavior_parts.append("attempts to shift blame or induce guilt")
            
            elif category == "bullying":
                # Check for specific bullying patterns
                has_victim_blaming = any(
                    "victim-blaming" in m.pattern.description.lower() or
                    "victim" in m.pattern.description.lower()
                    for m in category_matches
                )
                has_demeaning = any(
                    "demeaning" in m.pattern.description.lower() or
                    "put-down" in m.pattern.description.lower()
                    for m in category_matches
                )
                has_severe = any(
                    "severe" in m.pattern.description.lower() or
                    m.confidence >= 0.9
                    for m in category_matches
                )
                
                if has_victim_blaming:
                    behavior_parts.append("victim-blaming and dismissive language")
                elif has_demeaning:
                    behavior_parts.append("demeaning language and put-downs")
                elif has_severe:
                    behavior_parts.append("severe threats or extreme insults")
                else:
                    behavior_parts.append("mean comments or personal attacks")
            
            elif category == "secrecy":
                # Analyze secrecy patterns - check what was actually detected
                has_isolation_secrecy = any(
                    "isolation" in m.pattern.description.lower() or
                    "discouraging" in m.pattern.description.lower()
                    for m in category_matches
                )
                has_privacy_redefinition = any(
                    "privacy" in m.pattern.description.lower() and "secrecy" in m.pattern.description.lower()
                    for m in category_matches
                )
                
                if has_isolation_secrecy:
                    behavior_parts.append("discouraging outside support or advice")
                elif has_privacy_redefinition:
                    behavior_parts.append("redefining privacy as keeping secrets")
                else:
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

