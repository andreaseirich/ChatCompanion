"""Explanation generation for risk detection results."""

import re
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
            "a trusted person or support service about this."
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
            "Someone is asking you to keep secrets from people you trust. "
            "This is a warning sign. Safe people don't ask you to keep secrets. "
            "It's important to tell a trusted person or support service about this."
        ),
        RiskCategory.GUILT_SHIFTING: (
            "This person is trying to make you feel bad or blame you for something. "
            "This is not fair. You are not responsible for someone else's actions. "
            "Talk to someone you trust about how this makes you feel."
        ),
        RiskCategory.GROOMING: (
            "This conversation has some concerning patterns. Someone might be trying "
            "to build trust in an inappropriate way. This is very serious. "
            "Please talk to a trusted person or support service immediately."
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
        # First message will be dynamically generated based on actual detected categories
        "If you feel unsafe, talk to a trusted person or support service immediately.",
    ]

    def _has_threat_patterns(self, matches: Dict[str, List[PatternMatch]], full_text: str = "") -> bool:
        """
        Check if any threat/ultimatum patterns are matched.
        
        Threat patterns are ONLY explicit ultimatums/withdrawal/consequence pressure:
        - Patterns with descriptions containing: "ultimatum", "relationship threat", 
          "threats of withdrawal", "or else", "we're done", "if you don't... then..."
        - Check both pattern descriptions AND matched text for threat markers
        - Also check full_text for threat markers if provided (for cross-sentence threats)
        
        Args:
            matches: Dictionary of category -> list of PatternMatch objects
            full_text: Optional full text to check for threat markers (for cross-sentence threats)
            
        Returns:
            True only if threat patterns are actually matched
        """
        threat_keywords = [
            "ultimatum", "relationship threat", "threats of withdrawal",
            "or else", "we're done", "i'm done", "it's over"
        ]
        
        # Check pattern descriptions
        for category, match_list in matches.items():
            for match in match_list:
                desc_lower = match.pattern.description.lower()
                if any(keyword in desc_lower for keyword in threat_keywords):
                    return True
                
                # Check matched text for explicit threat markers
                matched_text_lower = match.matched_text.lower()
                if re.search(r"\b(or else|we'?re done|i'?m done|it'?s over|if you don'?t.*then)\b", matched_text_lower):
                    return True
        
        # Check full_text for threat markers if provided (for cross-sentence threats)
        # This handles cases where threat is in a different sentence than the matched pattern
        if full_text:
            full_text_lower = full_text.lower()
            if re.search(r"\b(or else|we'?re done|i'?m done|it'?s over|if you don'?t.*then)\b", full_text_lower):
                # Verify that threat markers are in proximity to matched patterns
                # (within same sentence or adjacent sentences)
                for category, match_list in matches.items():
                    for match in match_list:
                        # Check if threat is in same sentence or adjacent to match
                        threat_match = re.search(r"\b(or else|we'?re done|i'?m done|it'?s over|if you don'?t.*then)\b", full_text_lower)
                        if threat_match:
                            # Simple proximity check: threat within 200 chars of match
                            threat_pos = threat_match.start()
                            match_pos = match.position
                            if abs(threat_pos - match_pos) < 200:
                                return True
        
        return False

    def generate_explanation(
        self,
        risk_level: RiskLevel,
        category_scores: Dict[str, float],
        matches: Dict[str, List[PatternMatch]],
        overall_score: float = 0.0,
        original_text: str = "",
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
        
        # GREEN criteria from Master Prompt:
        # - boundaries are expressed AND respected
        # - scheduling or delays are accepted
        # - no guilt language
        # - no consequences or threats
        # - no secrecy or isolation demands
        # - explicit "no pressure" phrases suppress pressure detection
        
        # Only generate explanation if there are actual matches OR meaningful scores
        # If no matches and no meaningful scores, it's truly GREEN
        if (risk_level == RiskLevel.GREEN or overall_score < 0.3) and not has_meaningful_scores and not has_any_matches:
            explanation_parts.append(
                "Analysis checked for patterns of bullying, manipulation, pressure, secrecy demands, "
                "guilt-shifting, and grooming indicators."
            )
            explanation_parts.append(
                "No warning signs detected in this conversation."
            )
            return " ".join(explanation_parts)
        
        # If GREEN but has matches (weak signals), still say "No warning signs"
        # Do NOT mention patterns or evidence in user-facing text
        if (risk_level == RiskLevel.GREEN or overall_score < 0.3) and not has_meaningful_scores:
            explanation_parts.append(
                "Analysis checked for patterns of bullying, manipulation, pressure, secrecy demands, "
                "guilt-shifting, and grooming indicators."
            )
            explanation_parts.append(
                "No warning signs detected in this conversation."
            )
            # Do NOT mention patterns or evidence - keep it clean for GREEN
            return " ".join(explanation_parts)
        
        # Only proceed with explanation if there are matches OR meaningful scores
        # Do not generate warnings without evidence
        if not has_any_matches and not has_meaningful_scores:
            # No matches and no meaningful scores - should not happen if we got here
            # but handle gracefully
            explanation_parts.append(
                "Analysis checked for patterns of bullying, manipulation, pressure, secrecy demands, "
                "guilt-shifting, and grooming indicators."
            )
            explanation_parts.append(
                "No warning signs detected in this conversation."
            )
            return " ".join(explanation_parts)
        
        # If we have matches but still GREEN, it means weak signals
        # Still return clean "No warning signs" message - no pattern mentions
        if risk_level == RiskLevel.GREEN and has_any_matches:
            explanation_parts.append(
                "Analysis checked for patterns of bullying, manipulation, pressure, secrecy demands, "
                "guilt-shifting, and grooming indicators."
            )
            explanation_parts.append(
                "No warning signs detected in this conversation."
            )
            # Do NOT mention patterns or evidence - keep GREEN explanations clean
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
            # BUT: Only include categories that have actual matches (not just scores from ML)
            # This ensures explanations are strictly aligned with actual conversation text
            high_score_cats = [
                cat for cat, score in detected_categories 
                if score >= 0.6 and cat in matches and len(matches[cat]) > 0
            ]
            moderate_cats = [
                cat for cat, score in detected_categories 
                if 0.3 <= score < 0.6 and cat in matches and len(matches[cat]) > 0
            ]
            
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

        # Check for guilt-shifting even if it's not the top category
        # Mention it if score >= 0.18 OR patterns detected
        guilt_shifting_score = category_scores.get("guilt_shifting", 0.0)
        guilt_matches = matches.get("guilt_shifting", [])
        has_guilt_shifting = guilt_shifting_score >= 0.18 or len(guilt_matches) > 0
        
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
                
                # Use strict threat detection - only mention threats if threat patterns are actually matched
                has_threat = self._has_threat_patterns(matches, original_text)
                
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
                
                # Strict threat gating: only mention threats if threat patterns are actually detected
                if has_threat:
                    # Check for specific threat types for more precise messaging
                    has_withdrawal = any(
                        "threats of withdrawal" in m.pattern.description.lower()
                        for m in pressure_matches
                    )
                    has_blackmail = any(
                        "emotional blackmail" in m.pattern.description.lower() or
                        "friendship threat" in m.pattern.description.lower()
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
                    else:
                        explanation_parts.append(
                            "This conversation shows pressure with threats of consequences if demands are not met."
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
                    # Default: pressure without threats - use neutral phrasing
                    if has_guilt_shifting:
                        explanation_parts.append(
                            "This conversation shows pressure or guilt-making language."
                        )
                    else:
                        explanation_parts.append(
                            "This conversation shows pressure to act quickly or comply with demands."
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
                    "forced emotional disclosure" in m.pattern.description.lower()
                    for m in manip_matches
                )
                has_proof_requests = any(
                    "demands for proof" in m.pattern.description.lower() or
                    "proof" in m.pattern.description.lower() or
                    "screenshot" in m.pattern.description.lower() or
                    "delete" in m.pattern.description.lower() and "prove" in m.pattern.description.lower()
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
                elif has_proof_requests:
                    # Proof-of-compliance requests (delete messages, send screenshots, etc.)
                    explanation_parts.append(
                        "This person is making proof-of-compliance requests (such as deleting messages or sending screenshots) "
                        "to control your behavior and isolate you from support."
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
                        "This person is forcing emotional disclosure to control your behavior."
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
            # Check for guilt-shifting even if it's not the top category
            # Mention it if score > 0.20 OR patterns detected
            guilt_shifting_score = category_scores.get("guilt_shifting", 0.0)
            guilt_matches = matches.get("guilt_shifting", [])
            has_guilt_shifting = guilt_shifting_score >= 0.18 or len(guilt_matches) > 0
            
            if top_category == "guilt_shifting" and top_score >= 0.5:
                # Check what guilt-shifting patterns were actually detected
                # Lower threshold to 0.5 to catch more guilt-shifting cases
                has_response_time = any(
                    "response time questioning" in m.pattern.description.lower()
                    for m in guilt_matches
                )
                has_conditional_care = any(
                    "conditional care" in m.pattern.description.lower()
                    for m in guilt_matches
                )
                has_emotional_blame = any(
                    "emotional blame" in m.pattern.description.lower()
                    for m in guilt_matches
                )
                has_effort_comparison = any(
                    "effort comparison" in m.pattern.description.lower()
                    for m in guilt_matches
                )
                has_direct_guilt = any(
                    "guilt induction" in m.pattern.description.lower() or
                    "direct guilt" in m.pattern.description.lower()
                    for m in guilt_matches
                )
                
                if has_response_time:
                    explanation_parts.append(
                        "This conversation includes guilt-shifting through questioning your response time or attention "
                        "(e.g., 'If you cared, you'd have answered faster')."
                    )
                elif has_conditional_care:
                    explanation_parts.append(
                        "This conversation includes guilt-shifting through conditional statements about care "
                        "(e.g., 'If you cared about me, you would...')."
                    )
                elif has_emotional_blame:
                    explanation_parts.append(
                        "This conversation includes guilt-shifting through blaming you for the other person's emotions "
                        "(e.g., 'You make me feel bad because you didn't...')."
                    )
                elif has_effort_comparison:
                    explanation_parts.append(
                        "This conversation includes guilt-shifting through comparing efforts "
                        "(e.g., 'I'm the only one trying')."
                    )
                elif has_direct_guilt:
                    explanation_parts.append(
                        "This conversation includes direct attempts to make you feel guilty "
                        "(e.g., 'Maybe you should feel bad')."
                    )
                else:
                    explanation_parts.append(
                        "This conversation includes attempts to make you feel responsible for the other "
                        "person's actions or emotions."
                    )
            # If guilt-shifting is present but not the top category, mention it explicitly
            elif has_guilt_shifting and top_category != "guilt_shifting":
                # Guilt-shifting detected but not primary - mention it explicitly
                if guilt_matches:
                    has_conditional = any(
                        "conditional care" in m.pattern.description.lower() or
                        "response time questioning" in m.pattern.description.lower()
                        for m in guilt_matches
                    )
                    if has_conditional:
                        explanation_parts.append(
                            "This conversation includes guilt-inducing conditional statements "
                            "(e.g., 'if you cared...') that were detected."
                        )
                    else:
                        explanation_parts.append(
                            "This conversation includes guilt-shifting patterns that were detected."
                        )
            elif top_category == "secrecy" and top_score >= 0.6:
                # Check what secrecy patterns were detected
                secrecy_matches = matches.get("secrecy", [])
                # Use strict threat detection - only mention threats if threat patterns are actually matched
                has_threat = self._has_threat_patterns(matches, original_text)
                
                has_isolation = any("isolation" in m.pattern.description.lower() or "discouraging" in m.pattern.description.lower() 
                                  for m in secrecy_matches)
                has_proof_destruction = any(
                    "delete" in m.pattern.description.lower() and "prove" in m.pattern.description.lower()
                    for m in secrecy_matches
                )
                has_privacy_redef = any("privacy" in m.pattern.description.lower() and "secrecy" in m.pattern.description.lower()
                                       for m in secrecy_matches)
                
                if has_proof_destruction:
                    explanation_parts.append(
                        "This conversation includes secrecy demands with proof-of-compliance requests (such as deleting messages) "
                        "and attempts to isolate you from support."
                    )
                elif has_isolation:
                    explanation_parts.append(
                        "This conversation includes secrecy demands and attempts to isolate you from support."
                    )
                elif has_threat:
                    # Only mention threats if threat patterns are actually detected
                    explanation_parts.append(
                        "This conversation includes secrecy demands with threats to end the relationship if you tell anyone."
                    )
                elif has_privacy_redef:
                    explanation_parts.append(
                        "This conversation redefines privacy as keeping secrets from trusted people."
                    )
                else:
                    explanation_parts.append(
                        "This conversation includes secrecy demands designed to isolate you from support."
                    )
            elif risk_level == RiskLevel.YELLOW:
                # For YELLOW, use milder language
                if top_category in self.EXPLANATIONS:
                    category_explanation = self.EXPLANATIONS[top_category]
                    category_explanation = category_explanation.replace("trusted adult", "someone you trust")
                    category_explanation = category_explanation.replace("kids", "people")
                    explanation_parts.append(category_explanation)
            elif risk_level == RiskLevel.RED:
                # For RED, check if threats are present and mention them appropriately
                has_threat = self._has_threat_patterns(matches)
                
                if top_category == "secrecy":
                    # Check for relationship threats in secrecy context
                    secrecy_matches = matches.get("secrecy", [])
                    if has_threat:
                        explanation_parts.append(
                            "This conversation includes secrecy demands with threats to end the relationship if you tell anyone."
                        )
                    else:
                        # Use standard secrecy explanation without threat language
                        if top_category in self.EXPLANATIONS:
                            explanation_parts.append(self.EXPLANATIONS[top_category])
                elif top_category in self.EXPLANATIONS:
                    explanation_parts.append(self.EXPLANATIONS[top_category])

        # Add behavioral description instead of raw keyword quotes
        # Describe what behaviors were observed in conversational context
        if matches:
            behavior_descriptions = self._describe_behaviors(matches, category_scores, detected_categories, original_text)
            if behavior_descriptions:
                explanation_parts.append(f"\n\nObserved behaviors: {behavior_descriptions}")

        # Add risk level context with appropriate severity
        if risk_level == RiskLevel.RED:
            explanation_parts.append(
                "\n\n⚠️ This is a high-risk situation requiring immediate attention. "
                "Consider getting help from a trusted person or support service."
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
        detected_categories: List[tuple],
        original_text: str = ""
    ) -> str:
        """
        Describe observed behaviors in conversational context, not just keywords.
        Focus on behavior patterns and dynamics, not isolated trigger words.

        Args:
            matches: Pattern matches by category
            category_scores: Scores for each category
            detected_categories: List of (category, score) tuples, sorted by score
            original_text: Optional full text for cross-sentence threat detection

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
            # Use strict threat detection - only mention threats if threat patterns are actually matched
            has_threat = self._has_threat_patterns({category: category_matches}, original_text)
            
            if category == "pressure":
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
                # Only mention threats if threat patterns are actually detected
                if has_threat:
                    # Check for specific threat types
                    has_withdrawal_threats = any(
                        "withdrawal" in m.pattern.description.lower() or
                        "threats of withdrawal" in m.pattern.description.lower()
                        for m in category_matches
                    )
                    if has_withdrawal_threats:
                        behavior_parts.append("threats of withdrawal of affection or attention")
                    else:
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
                    "forced emotional disclosure" in m.pattern.description.lower()
                    for m in category_matches
                )
                has_proof_requests = any(
                    "demands for proof" in m.pattern.description.lower() or
                    "proof" in m.pattern.description.lower() or
                    "screenshot" in m.pattern.description.lower() or
                    ("delete" in m.pattern.description.lower() and "prove" in m.pattern.description.lower())
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
                # Use preferred terms: coercive control, isolation from support, secrecy demands, proof-of-compliance requests
                if has_coercive:
                    behavior_parts.append("coercive control and removal of autonomy")
                if has_fear:
                    behavior_parts.append("deliberate use of fear for compliance")
                if has_proof_requests:
                    behavior_parts.append("proof-of-compliance requests (e.g., delete messages, send screenshots)")
                # Only mention forced emotional disclosure if emotions were actually demanded (not just proof requests)
                if has_forced_disclosure and not has_proof_requests:
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
                    behavior_parts.append("isolation from support")
                
                # If no specific patterns matched, use generic description
                if not (has_privacy_invasion or has_trust_manipulation or has_conditional or has_forced_disclosure or has_proof_requests or has_boundary_framing or has_isolation or has_coercive or has_fear):
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
                    "don't care" in m.pattern.description.lower() or
                    "effort comparison" in m.pattern.description.lower()
                    for m in category_matches
                )
                has_response_time_questioning = any(
                    "response time questioning" in m.pattern.description.lower() or
                    ("cared" in m.pattern.description.lower() and "answered" in m.pattern.description.lower())
                    for m in category_matches
                )
                has_conditional_care = any(
                    "conditional care" in m.pattern.description.lower()
                    for m in category_matches
                )
                has_emotional_blame = any(
                    "emotional blame" in m.pattern.description.lower() or
                    ("make me feel" in m.pattern.description.lower() and "because" in m.pattern.description.lower())
                    for m in category_matches
                )
                has_direct_guilt = any(
                    "guilt induction" in m.pattern.description.lower() or
                    "direct guilt" in m.pattern.description.lower()
                    for m in category_matches
                )
                
                if has_importance_questioning:
                    behavior_parts.append("guilt-shifting through questioning your importance or care")
                elif has_response_time_questioning:
                    behavior_parts.append("guilt-shifting through questioning your response time or attention")
                elif has_conditional_care:
                    behavior_parts.append("guilt-shifting through conditional statements about care")
                elif has_effort_questioning:
                    behavior_parts.append("guilt-shifting through questioning your effort or commitment")
                elif has_emotional_blame:
                    behavior_parts.append("guilt-shifting through blaming you for their emotions")
                elif has_direct_guilt:
                    behavior_parts.append("direct attempts to make you feel guilty")
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
                # Use strict threat detection - only mention threats if threat patterns are actually matched
                # Check threats in full_text context for cross-sentence threats
                has_threat = self._has_threat_patterns({category: category_matches}, original_text)
                
                has_isolation_secrecy = any(
                    "isolation" in m.pattern.description.lower() or
                    "discouraging" in m.pattern.description.lower()
                    for m in category_matches
                )
                has_proof_destruction = any(
                    "delete" in m.pattern.description.lower() and "prove" in m.pattern.description.lower()
                    for m in category_matches
                )
                has_privacy_redefinition = any(
                    "privacy" in m.pattern.description.lower() and "secrecy" in m.pattern.description.lower()
                    for m in category_matches
                )
                
                # Priority: threats first (most severe), then proof destruction, then isolation
                if has_threat:
                    # Only mention threats if threat patterns are actually detected
                    behavior_parts.append("secrecy demands with relationship threats")
                elif has_proof_destruction:
                    behavior_parts.append("secrecy demands with proof-of-compliance requests (delete messages)")
                elif has_isolation_secrecy:
                    behavior_parts.append("secrecy demands and isolation from support")
                elif has_privacy_redefinition:
                    behavior_parts.append("redefining privacy as keeping secrets")
                else:
                    behavior_parts.append("secrecy demands")
            
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

    def get_help_advice(
        self, 
        risk_level: RiskLevel, 
        overall_score: float = 0.0,
        category_scores: Dict[str, float] = None,
        matches: Dict[str, List] = None
    ) -> List[str]:
        """
        Get context-appropriate help advice messages based on risk level.

        Args:
            risk_level: Overall risk level (green/yellow/red)
            overall_score: Overall risk score (0.0 - 1.0)
            category_scores: Category scores for RED-specific messaging
            matches: Pattern matches for RED-specific messaging

        Returns:
            List of context-appropriate advice strings
        """
        # Use risk-level appropriate messages
        if risk_level == RiskLevel.RED or overall_score >= 0.8:
            # For RED, generate dynamic message based on actual detected categories
            if category_scores and matches:
                # Identify dominant categories (score >= 0.6)
                dominant_categories = [
                    cat for cat, score in category_scores.items() 
                    if score >= 0.6
                ]
                
                # Map to readable names
                category_names = {
                    "coercive control": "coercive control",
                    "manipulation": "coercive control" if "manipulation" in dominant_categories and category_scores.get("manipulation", 0) >= 0.7 else "manipulation",
                    "secrecy": "secrecy demands",
                    "pressure": "pressure" if "pressure" in dominant_categories else None,
                    "bullying": "bullying",
                    "grooming": "grooming indicators",
                    "guilt_shifting": "guilt-shifting",
                }
                
                # Check for specific high-risk patterns
                has_secrecy = "secrecy" in dominant_categories or category_scores.get("secrecy", 0) >= 0.6
                has_isolation = any(
                    "isolation" in m.pattern.description.lower() or
                    "discouraging" in m.pattern.description.lower()
                    for cat_matches in matches.values()
                    for m in cat_matches
                ) if matches else False
                has_proof_requests = any(
                    "proof" in m.pattern.description.lower() or
                    "delete" in m.pattern.description.lower()
                    for cat_matches in matches.values()
                    for m in cat_matches
                ) if matches else False
                has_coercive = "manipulation" in dominant_categories and category_scores.get("manipulation", 0) >= 0.7
                
                # Build message based on actual patterns
                detected_terms = []
                if has_coercive:
                    detected_terms.append("coercive control")
                if has_secrecy:
                    detected_terms.append("secrecy demands")
                if has_isolation:
                    detected_terms.append("isolation from support")
                if has_proof_requests:
                    detected_terms.append("proof-of-compliance requests")
                
                # Only add bullying/grooming if they're actually dominant
                if "bullying" in dominant_categories:
                    detected_terms.append("bullying")
                if "grooming" in dominant_categories and category_scores.get("grooming", 0) >= 0.6:
                    detected_terms.append("grooming indicators")
                
                if detected_terms:
                    message = f"Serious warning signs detected: {', '.join(detected_terms)}."
                else:
                    # Fallback if no specific patterns identified
                    message = "Serious warning signs detected: manipulation or pressure patterns."
                
                return [message] + self.ADVICE_MESSAGES_RED.copy()
            else:
                return self.ADVICE_MESSAGES_RED.copy()
        elif risk_level == RiskLevel.YELLOW or overall_score >= 0.3:
            return self.ADVICE_MESSAGES_YELLOW.copy()
        else:
            return self.ADVICE_MESSAGES_GREEN.copy()

