"""Main detection engine orchestrator."""

import logging
from typing import Dict, List, Optional, Tuple

from app.detection.aggregator import ScoreAggregator
from app.detection.explainer import ExplanationGenerator
from app.detection.slang_normalizer import SlangNormalizer
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
        # Normalize slang and abbreviations first
        slang_normalizer = SlangNormalizer()
        normalized_message = slang_normalizer.normalize_message(text)
        
        # Then apply standard text normalization
        normalized_text = normalize_text(normalized_message.normalized_text)
        sentences = segment_sentences(normalized_text)

        # Run rules engine on normalized text (with slang normalized)
        rules_result = self.rule_engine.analyze(normalized_text)
        rules_scores = rules_result["category_scores"]
        matches = rules_result["matches"]
        
        # Check for friendly teasing context and down-weight scores if detected
        # This reduces false positives for mutual teasing between friends
        # Pass normalized message and matches to use emoji, tone markers, and check hard blockers
        is_friendly_teasing = self._check_friendly_teasing_context(
            normalized_message, normalized_text, matches
        )
        is_professional_context = self._check_professional_context(normalized_text)
        
        if is_friendly_teasing:
            # Down-weight bullying score only (×0.3-0.4)
            # NEVER down-weight secrecy/manipulation/pressure when coercive control is present
            # Check for coercive control patterns before applying banter suppression
            has_coercive_control = any(
                category in matches and len(matches[category]) > 0
                for category in ["secrecy", "manipulation"]
            )
            
            if not has_coercive_control:
                # Only down-weight bullying, not other categories
                if "bullying" in rules_scores and rules_scores["bullying"] > 0:
                    original_score = rules_scores["bullying"]
                    rules_scores["bullying"] = original_score * 0.35  # ×0.3-0.4 range
                    logger.debug(
                        f"Friendly banter detected: down-weighted bullying from {original_score:.2f} "
                        f"to {rules_scores['bullying']:.2f}"
                    )
            else:
                logger.debug(
                    "Friendly banter detected but coercive control present - NOT down-weighting"
                )
        
        if is_professional_context:
            # Down-weight pressure/manipulation in professional/workplace contexts
            # Professional urgency ("I'll fix it immediately") is not manipulation
            for category in ["pressure", "manipulation"]:
                if category in rules_scores and rules_scores[category] > 0:
                    original_score = rules_scores[category]
                    rules_scores[category] = original_score * 0.4
                    logger.debug(
                        f"Professional context: down-weighted {category} from {original_score:.2f} "
                        f"to {rules_scores[category]:.2f}"
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

        # Apply context-based reductions to final category scores if detected
        # This ensures the reduction applies even after ML aggregation
        if is_friendly_teasing:
            for category in list(category_scores.keys()):
                if category_scores[category] > 0:
                    category_scores[category] = category_scores[category] * 0.3
                    logger.debug(f"Friendly teasing: final reduction for {category} to {category_scores[category]:.2f}")
        
        if is_professional_context:
            for category in ["pressure", "manipulation"]:
                if category in category_scores and category_scores[category] > 0:
                    category_scores[category] = category_scores[category] * 0.4
                    logger.debug(f"Professional context: final reduction for {category} to {category_scores[category]:.2f}")

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
        
        # Debug note for GREEN: if category scores are non-zero but no patterns match
        # This clarifies why developers might see non-zero scores in GREEN state
        if risk_level == RiskLevel.GREEN and not has_any_matches:
            has_non_zero_scores = any(score > 0.0 for score in category_scores.values()) if category_scores else False
            if has_non_zero_scores:
                logger.debug(
                    "Note: GREEN suppresses risk. Category scores may show raw signals even when no patterns match."
                )

        # Generate explanation (with overall_score for context)
        # Pass original text for threat detection in cross-sentence contexts
        explanation = self.explainer.generate_explanation(
            risk_level, category_scores, matches, overall_score, original_text=text
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

    def _extract_message_turns(self, text: str) -> List[tuple]:
        """
        Extract message turns from conversation text.
        
        Args:
            text: Conversation text (may have speaker labels or be plain text)
            
        Returns:
            List of (speaker, message) tuples, or [(None, text)] if no structure
        """
        from app.utils.text_processing import extract_message_pairs
        
        # Try to extract structured message pairs
        message_pairs = extract_message_pairs(text)
        
        if len(message_pairs) > 1:
            # Structured conversation with speaker labels
            return message_pairs
        else:
            # Plain text - split by lines and assign sequential speakers
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if len(lines) <= 1:
                return [(None, text)]
            
            # Assign alternating speakers (A, B, A, B, ...)
            turns = []
            for i, line in enumerate(lines):
                speaker = "A" if i % 2 == 0 else "B"
                turns.append((speaker, line))
            return turns

    def _check_mutuality(self, turns: List[tuple], normalized_text: str) -> bool:
        """
        Check if both sides use joking markers within last N turns (N=6).
        
        Args:
            turns: List of (speaker, message) tuples
            normalized_text: Normalized text for pattern matching
            
        Returns:
            True if mutuality detected (both sides have joking markers)
        """
        import re
        from app.detection.slang_normalizer import SlangNormalizer
        
        if len(turns) < 2:
            return False
        
        # Get last 6 turns
        recent_turns = turns[-6:] if len(turns) > 6 else turns
        
        # Normalize messages before checking for joking markers
        normalizer = SlangNormalizer()
        
        # Joking markers (normalized)
        joking_patterns = [
            r"\b(just kidding|just joking|kidding|joking)\b",
            r"\b(laughing|haha|hehe)\b",
        ]
        
        # Track which speakers have joking markers
        speakers_with_joking = set()
        
        for speaker, message in recent_turns:
            if not speaker:
                continue
            # Normalize the message before checking for joking markers
            normalized_message = normalizer.normalize_message(message)
            normalized_msg_text = normalized_message.normalized_text.lower()
            
            # Check if this message has joking markers (in normalized form)
            has_joking = any(
                re.search(pattern, normalized_msg_text, re.IGNORECASE)
                for pattern in joking_patterns
            )
            if has_joking:
                speakers_with_joking.add(speaker)
        
        # Mutuality: at least 2 different speakers have joking markers
        return len(speakers_with_joking) >= 2

    def _check_repair_markers(self, turns: List[tuple], normalized_text: str) -> bool:
        """
        Check if repair/closure markers exist near the end (last 2-3 messages).
        
        Args:
            turns: List of (speaker, message) tuples
            normalized_text: Normalized text for pattern matching
            
        Returns:
            True if repair markers found near the end
        """
        import re
        from app.detection.slang_normalizer import SlangNormalizer
        
        if len(turns) == 0:
            return False
        
        # Check last 2-3 messages
        last_messages = turns[-3:] if len(turns) >= 3 else turns
        
        # Normalize messages before checking for repair markers
        normalizer = SlangNormalizer()
        
        # Repair/closure markers (normalized)
        repair_patterns = [
            r"\b(jk|just kidding|just joking|kidding)\b",
            r"\b(all good|no worries|my bad|didn'?t mean it)\b",
            r"\b(lol jk|haha jk|laughing jk)\b",
        ]
        
        # Check if any of the last messages contain repair markers
        for speaker, message in last_messages:
            # Normalize the message before checking for repair markers
            normalized_message = normalizer.normalize_message(message)
            normalized_msg_text = normalized_message.normalized_text.lower()
            
            if any(re.search(pattern, normalized_msg_text, re.IGNORECASE) for pattern in repair_patterns):
                return True
        
        return False

    def _check_hard_blockers(self, normalized_text: str, matches: Dict[str, List]) -> bool:
        """
        Check for hard blockers that prevent banter suppression.
        
        Hard blockers:
        - Coercive control / secrecy / isolation / proof-of-compliance patterns
        - Threats/ultimatums
        - Severe insults
        - One-sided repeated insults without repair markers
        
        Args:
            normalized_text: Normalized text for pattern matching
            matches: Pattern matches by category
            
        Returns:
            True if hard blockers detected (banter suppression should NOT apply)
        """
        import re
        
        # Check for coercive control / secrecy / isolation / proof-of-compliance
        coercive_categories = ["secrecy", "manipulation"]
        for category in coercive_categories:
            if category in matches and len(matches[category]) > 0:
                # Check if matches indicate coercive control
                coercive_patterns = [
                    "coercive control", "secrecy", "isolation", "proof", "delete", "screenshot"
                ]
                for match in matches[category]:
                    if any(pattern in match.pattern.description.lower() for pattern in coercive_patterns):
                        return True
        
        # Check for threats/ultimatums
        threat_patterns = [
            r"\b(or else|we'?re done if|you'?ll regret it|don'?t expect)\b",
            r"\b(if you don'?t|unless you)\b",
        ]
        if any(re.search(pattern, normalized_text, re.IGNORECASE) for pattern in threat_patterns):
            return True
        
        # Check for severe insults (high confidence, short list)
        severe_insult_patterns = [
            r"\b(worthless|kill yourself|kys|go die|stfu|shut up|nobody likes you|pathetic)\b",
        ]
        if any(re.search(pattern, normalized_text, re.IGNORECASE) for pattern in severe_insult_patterns):
            return True
        
        # Check for one-sided repeated insults (same speaker) without repair markers
        # This is handled by checking if bullying matches exist without repair markers
        if "bullying" in matches and len(matches["bullying"]) > 0:
            # If multiple bullying matches and no repair markers, it's one-sided
            if len(matches["bullying"]) >= 2:
                # Check for repair markers
                repair_patterns = [
                    r"\b(jk|just kidding|all good|no worries|my bad)\b",
                ]
                has_repair = any(
                    re.search(pattern, normalized_text, re.IGNORECASE)
                    for pattern in repair_patterns
                )
                if not has_repair:
                    return True  # One-sided repeated insults without repair
        
        return False

    def _check_friendly_teasing_context(
        self, normalized_message, normalized_text: str, matches: Dict[str, List] = None
    ) -> bool:
        """
        Check if text shows signs of friendly teasing rather than bullying.
        
        Stricter model: Banter is TRUE only if ALL are met:
        1. Mutuality: Both sides tease OR both sides use joking markers within last N turns (N=6)
        2. Repair/closure: At least one repair marker exists near the end
        3. No severe insult/threat/control present (hard blockers)
        
        Args:
            normalized_message: NormalizedMessage object with raw text and tone markers
            normalized_text: Normalized text (for pattern matching)
            matches: Pattern matches by category (for hard blocker detection)
            
        Returns:
            True if friendly teasing context is detected, False otherwise
        """
        import re
        
        if matches is None:
            matches = {}
        
        # Extract raw text and tone markers
        original_text = normalized_message.raw_text
        tone_markers = normalized_message.tone_markers
        
        # Hard blockers check FIRST - if present, banter suppression should NOT apply
        has_hard_blockers = self._check_hard_blockers(normalized_text, matches)
        if has_hard_blockers:
            return False
        
        # Extract message turns
        turns = self._extract_message_turns(original_text)
        
        # Requirement 1: Mutuality
        has_mutuality = self._check_mutuality(turns, normalized_text)
        
        # Requirement 2: Repair/closure markers
        has_repair = self._check_repair_markers(turns, normalized_text)
        
        # Banter is TRUE only if ALL requirements met
        is_banter = has_mutuality and has_repair
        
        return is_banter

    def _check_professional_context(self, normalized_text: str) -> bool:
        """
        Check if text shows signs of professional/workplace context.
        
        Professional context indicators:
        - Work-related terms (bug, fix, code, production, project, deadline)
        - Professional apologies ("I'm so sorry", "I apologize")
        - Professional urgency ("I'll fix it immediately", "I'll get it done")
        - No personal attacks or manipulation
        
        Args:
            normalized_text: Normalized text (for pattern matching)
            
        Returns:
            True if professional context is detected, False otherwise
        """
        import re
        
        # Check for work-related terms
        work_terms = [
            r"\b(bug|fix|code|production|project|deadline|task|work|job|client|customer|team|meeting)\b",
            r"\b(I'll fix|I'll get|I'll handle|I'll resolve|I'll address)\b",
            r"\b(I'm so sorry|I apologize|my apologies|my mistake|my fault)\b",
        ]
        has_work_terms = any(
            re.search(pattern, normalized_text, re.IGNORECASE)
            for pattern in work_terms
        )
        
        # Check for personal attacks (if present, it's not professional)
        personal_attacks = [
            r"\b(you're (so|really|such a) (stupid|idiot|pathetic|ugly|worthless))\b",
            r"\b(kill yourself|kys|go die|hate you)\b",
        ]
        has_personal_attacks = any(
            re.search(pattern, normalized_text, re.IGNORECASE)
            for pattern in personal_attacks
        )
        
        # Professional context if:
        # - Has work terms
        # - AND no personal attacks
        is_professional = has_work_terms and not has_personal_attacks
        
        return is_professional

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

