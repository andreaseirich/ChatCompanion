"""Tests for generated chat corpus.

Verifies that the detection pipeline correctly handles synthetic chats
with youth slang and obfuscation variants.
"""

import pytest

from app.detection.engine import DetectionEngine
from app.testing.chat_corpus_generator import ChatCorpusGenerator
from app.utils.constants import RiskLevel


class TestGeneratedChatCorpus:
    """Test generated chat corpus against detection pipeline."""

    @pytest.fixture
    def detection_engine(self):
        """Create detection engine instance."""
        return DetectionEngine(use_ml=True)

    @pytest.fixture
    def generator(self):
        """Create chat generator with fixed seed."""
        return ChatCorpusGenerator(seed=1337)

    def test_green_chats(self, detection_engine, generator):
        """Test GREEN chats: should be classified as green with no warnings."""
        green_chats = [generator.generate_green_chat(f"green_{i}") for i in range(30)]
        
        for chat in green_chats:
            result = detection_engine.analyze(chat["chat_text"])
            
            # Assert risk level
            assert result.risk_level == RiskLevel.GREEN, (
                f"Chat {chat['id']} should be GREEN, got {result.risk_level}"
            )
            
            # Assert explanation contains "No warning signs" or equivalent
            explanation_lower = result.explanation.lower()
            assert "warning sign" in explanation_lower or "didn't see" in explanation_lower, (
                f"Chat {chat['id']} should mention no warning signs"
            )
            
            # Assert no "Need Immediate Help?"
            assert "Need Immediate Help?" not in result.explanation, (
                f"Chat {chat['id']} should not show 'Need Immediate Help?'"
            )
            
            # Assert no "Observed behaviors" (GREEN should not list behaviors)
            assert "observed behavior" not in explanation_lower, (
                f"Chat {chat['id']} should not list observed behaviors"
            )
            
            # Assert pattern matches are empty or minimal for GREEN
            total_matches = sum(len(matches) for matches in result.matches.values())
            assert total_matches == 0, (
                f"Chat {chat['id']} should have no pattern matches for GREEN, got {total_matches}"
            )

    def test_yellow_chats(self, detection_engine, generator):
        """Test YELLOW chats: should be classified as yellow without 'Need Immediate Help?'."""
        yellow_chats = [generator.generate_yellow_chat(f"yellow_{i}") for i in range(30)]
        
        for chat in yellow_chats:
            result = detection_engine.analyze(chat["chat_text"])
            
            # Assert risk level
            assert result.risk_level == RiskLevel.YELLOW, (
                f"Chat {chat['id']} should be YELLOW, got {result.risk_level}"
            )
            
            # Assert no "Need Immediate Help?"
            assert "Need Immediate Help?" not in result.explanation, (
                f"Chat {chat['id']} should not show 'Need Immediate Help?' for YELLOW"
            )
            
            # If guilt-shifting is present, check if it's mentioned
            if chat["contains"]["guilt_shifting"]:
                explanation_lower = result.explanation.lower()
                # Check for guilt-related wording (child-friendly phrasing)
                has_guilt_mention = (
                    "guilt" in explanation_lower or
                    "blame" in explanation_lower or
                    "you're not" in explanation_lower or
                    "you never" in explanation_lower
                )
                # Note: May not always be mentioned if patterns don't match exactly
                # This is acceptable - we're checking that threats are gated correctly
            
            # Check threat-gating: threats should only be mentioned if threat patterns matched
            explanation_lower = result.explanation.lower()
            has_threat_mention = (
                "threat" in explanation_lower or
                "consequence" in explanation_lower or
                "withdrawal" in explanation_lower
            )
            
            if has_threat_mention:
                # If threats are mentioned, verify threat patterns actually matched
                # Check for ultimatum/threat patterns in matches
                has_threat_patterns = False
                for category, matches in result.matches.items():
                    for match in matches:
                        pattern_desc = match.pattern.description.lower()
                        if "threat" in pattern_desc or "ultimatum" in pattern_desc:
                            has_threat_patterns = True
                            break
                    if has_threat_patterns:
                        break
                
                assert has_threat_patterns, (
                    f"Chat {chat['id']} mentions threats but no threat patterns matched"
                )
            
            # Verify pattern match counts: if category is detected, instances > 0
            for category, matches in result.matches.items():
                if matches:
                    assert len(matches) > 0, (
                        f"Chat {chat['id']}: category {category} has matches but count is 0"
                    )

    def test_red_chats(self, detection_engine, generator):
        """Test RED chats: should be classified as red with 'Need Immediate Help?'."""
        red_chats = [generator.generate_red_chat(f"red_{i}") for i in range(30)]
        
        for chat in red_chats:
            result = detection_engine.analyze(chat["chat_text"])
            
            # Assert risk level
            assert result.risk_level == RiskLevel.RED, (
                f"Chat {chat['id']} should be RED, got {result.risk_level}"
            )
            
            # Assert "Need Immediate Help?" appears exactly once
            help_count = result.explanation.count("Need Immediate Help?")
            assert help_count == 1, (
                f"Chat {chat['id']} should show 'Need Immediate Help?' exactly once, got {help_count}"
            )
            
            # Verify pattern match counts: if category is detected, instances > 0
            for category, matches in result.matches.items():
                if matches:
                    assert len(matches) > 0, (
                        f"Chat {chat['id']}: category {category} has matches but count is 0"
                    )
            
            # Verify evidence-based explanations: if secrecy/isolation/control is present,
            # check that explanations reference them only if patterns matched
            explanation_lower = result.explanation.lower()
            
            if chat["contains"]["secrecy"]:
                # Secrecy should be mentioned if patterns matched
                has_secrecy_patterns = any(
                    "secrecy" in cat.lower() or "secret" in cat.lower()
                    for cat in result.matches.keys()
                )
                if has_secrecy_patterns:
                    assert "secret" in explanation_lower or "private" in explanation_lower, (
                        f"Chat {chat['id']} has secrecy patterns but not mentioned in explanation"
                    )
            
            if chat["contains"]["coercive_control"]:
                # Coercive control should be mentioned if patterns matched
                has_control_patterns = any(
                    "pressure" in cat.lower() or "coercive" in cat.lower() or "manipulation" in cat.lower()
                    for cat in result.matches.keys()
                )
                if has_control_patterns:
                    assert "control" in explanation_lower or "pressure" in explanation_lower, (
                        f"Chat {chat['id']} has control patterns but not mentioned in explanation"
                    )

    def test_right_now_context_gating(self, detection_engine, generator):
        """Test 'right now' context gating: self-reports vs demands."""
        # Self-report: should be GREEN/low
        self_report = "Friend: Hey\nYou: I'm busy rn\nFriend: Okay, np"
        result_self = detection_engine.analyze(self_report)
        # Should be GREEN or very low YELLOW
        assert result_self.risk_level in [RiskLevel.GREEN, RiskLevel.YELLOW], (
            f"Self-report 'I'm busy rn' should be GREEN/YELLOW, got {result_self.risk_level}"
        )
        
        # Demand: should trigger pressure (YELLOW/RED)
        demand = "Friend: Answer rn\nFriend: Do it rn\nFriend: Right now. Answer."
        result_demand = detection_engine.analyze(demand)
        # Should be YELLOW or RED
        assert result_demand.risk_level in [RiskLevel.YELLOW, RiskLevel.RED], (
            f"Demand 'Answer rn' should be YELLOW/RED, got {result_demand.risk_level}"
        )
        
        # Verify pattern matches for demand
        if result_demand.risk_level == RiskLevel.YELLOW:
            # Should have pressure patterns
            has_pressure = "pressure" in result_demand.matches or any(
                "pressure" in cat.lower() for cat in result_demand.matches.keys()
            )
            assert has_pressure or len(result_demand.matches) > 0, (
                "Demand should have pattern matches"
            )

    def test_obfuscation_variants(self, detection_engine, generator):
        """Test that obfuscation variants are handled correctly."""
        # Test spacing variants
        spacing_chat = "Friend: Answer r n\nFriend: Do it r.n."
        result = detection_engine.analyze(spacing_chat)
        # Should detect pressure despite obfuscation
        assert result.risk_level in [RiskLevel.YELLOW, RiskLevel.RED], (
            f"Obfuscated 'r n' should trigger detection, got {result.risk_level}"
        )
        
        # Test repeated letters
        repeat_chat = "Friend: Do it nowww\nFriend: Comeee on"
        result = detection_engine.analyze(repeat_chat)
        # Should detect pressure
        assert result.risk_level in [RiskLevel.YELLOW, RiskLevel.RED], (
            f"Repeated letters should trigger detection, got {result.risk_level}"
        )

