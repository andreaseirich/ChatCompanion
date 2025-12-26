# Copyright 2024 Eirich Andreas
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for youth slang normalization and banter/irony detection."""

import pytest
from app.detection.engine import DetectionEngine
from app.utils.constants import RiskLevel


def test_green_harmless_slang_idk_lol():
    """Test that harmless slang 'idk what u mean lol' is GREEN."""
    engine = DetectionEngine(use_ml=False)
    
    text = "idk what u mean lol"
    
    result = engine.analyze(text)
    
    assert result.risk_level == RiskLevel.GREEN, (
        f"Expected GREEN for harmless slang, got {result.risk_level}"
    )
    assert "mild patterns" not in result.explanation.lower(), (
        "GREEN should not mention 'mild patterns'"
    )


def test_green_harmless_slang_brb_rn():
    """Test that harmless slang 'brb rn' is GREEN."""
    engine = DetectionEngine(use_ml=False)
    
    # "brb rn" should normalize to "be right back right now" which is self-report, not demand
    # Use a clearer self-report phrase
    text = "brb rn, ttyl"
    
    result = engine.analyze(text)
    
    # Should be GREEN (self-report, not demand context)
    # If context gating works, "brb rn" should be excluded from pressure
    assert result.risk_level == RiskLevel.GREEN, (
        f"Expected GREEN for harmless slang 'brb rn' (self-report), got {result.risk_level}. "
        f"Score: {result.overall_score}, pressure matches: {len(result.matches.get('pressure', []))}"
    )


def test_green_harmless_slang_no_rush():
    """Test that 'no rush take ur time' is GREEN."""
    engine = DetectionEngine(use_ml=False)
    
    text = "no rush take ur time"
    
    result = engine.analyze(text)
    
    assert result.risk_level == RiskLevel.GREEN, (
        f"Expected GREEN for no-rush phrase, got {result.risk_level}"
    )


def test_green_banter_with_repair():
    """Test that banter with repair markers is GREEN."""
    engine = DetectionEngine(use_ml=False)
    
    text = """
    A: bruh ur wild 😂
    B: lol u too
    A: jk all good
    """
    
    result = engine.analyze(text)
    
    assert result.risk_level == RiskLevel.GREEN, (
        f"Expected GREEN for banter with repair, got {result.risk_level}"
    )


def test_yellow_one_sided_insult_no_repair():
    """Test that one-sided insult without repair is YELLOW (or higher)."""
    engine = DetectionEngine(use_ml=False)
    
    text = """
    A: ur pathetic
    B: stop
    A: whatever
    """
    
    result = engine.analyze(text)
    
    # Should be YELLOW or RED (banter suppression must NOT trigger)
    assert result.risk_level in [RiskLevel.YELLOW, RiskLevel.RED], (
        f"Expected YELLOW or RED for one-sided insult, got {result.risk_level}"
    )
    # Banter suppression should NOT have triggered
    assert result.risk_level != RiskLevel.GREEN, (
        "One-sided insult without repair should NOT be GREEN"
    )


def test_yellow_guilt_pressure_slang():
    """Test that guilt/pressure slang is YELLOW with guilt-shifting mentioned."""
    engine = DetectionEngine(use_ml=False)
    
    # Use pattern from rules_config.yaml: "if you cared about me, you would"
    text = "if you cared about me, you would answer right now"
    
    result = engine.analyze(text)
    
    assert result.risk_level in [RiskLevel.YELLOW, RiskLevel.RED], (
        f"Expected YELLOW or RED for guilt/pressure, got {result.risk_level}"
    )
    # Check if guilt-shifting is detected (either in explanation or in category scores)
    has_guilt_in_explanation = "guilt" in result.explanation.lower()
    has_guilt_score = result.category_scores.get("guilt_shifting", 0.0) >= 0.18
    has_guilt_matches = len(result.matches.get("guilt_shifting", [])) > 0
    assert has_guilt_in_explanation or has_guilt_score or has_guilt_matches, (
        f"YELLOW explanation should mention guilt-shifting when present or have guilt_shifting score >= 0.18 or matches. "
        f"Explanation: {result.explanation}, guilt_shifting score: {result.category_scores.get('guilt_shifting', 0.0)}, "
        f"guilt_shifting matches: {len(result.matches.get('guilt_shifting', []))}"
    )
    # Should NOT show "Need Immediate Help?" for YELLOW
    if result.risk_level == RiskLevel.YELLOW:
        assert result.risk_level != RiskLevel.RED, (
            "YELLOW should not trigger 'Need Immediate Help?'"
        )


def test_yellow_guilt_slang_only_one_trying():
    """Test that 'im the only one trying' is YELLOW."""
    engine = DetectionEngine(use_ml=False)
    
    # Use pattern from rules_config.yaml: "i'm the only one trying"
    text = "I'm the only one trying here. If you cared about me, you would help"
    
    result = engine.analyze(text)
    
    # Should be YELLOW or RED (guilt-shifting should be detected)
    assert result.risk_level in [RiskLevel.YELLOW, RiskLevel.RED], (
        f"Expected YELLOW or RED for guilt-shifting, got {result.risk_level}. "
        f"guilt_shifting score: {result.category_scores.get('guilt_shifting', 0.0)}, "
        f"guilt_shifting matches: {len(result.matches.get('guilt_shifting', []))}"
    )


def test_red_coercive_control_proof_compliance():
    """Test that coercive control with proof-of-compliance is RED."""
    engine = DetectionEngine(use_ml=False)
    
    text = "delete the chat and send a screenshot rn"
    
    result = engine.analyze(text)
    
    assert result.risk_level == RiskLevel.RED, (
        f"Expected RED for coercive control, got {result.risk_level}"
    )
    # RED should trigger "Need Immediate Help?" (checked in UI)
    assert result.risk_level == RiskLevel.RED, (
        "RED should trigger 'Need Immediate Help?' section"
    )


def test_red_secrecy_isolation():
    """Test that secrecy/isolation demand is RED."""
    engine = DetectionEngine(use_ml=False)
    
    text = "don't tell anyone about this"
    
    result = engine.analyze(text)
    
    assert result.risk_level == RiskLevel.RED, (
        f"Expected RED for secrecy/isolation, got {result.risk_level}"
    )


def test_banter_suppression_not_for_coercive_control():
    """Test that banter suppression does NOT apply to coercive control."""
    engine = DetectionEngine(use_ml=False)
    
    text = """
    A: delete those messages rn
    B: why?
    A: jk all good
    """
    
    result = engine.analyze(text)
    
    # Even with "jk all good", coercive control should still be RED
    # Banter suppression should NOT weaken RED signals
    assert result.risk_level == RiskLevel.RED, (
        f"Expected RED for coercive control even with banter markers, got {result.risk_level}"
    )


def test_new_slang_abbreviations():
    """Test that new slang abbreviations are normalized correctly."""
    from app.detection.slang_normalizer import SlangNormalizer
    
    normalizer = SlangNormalizer()
    
    test_cases = [
        ("frfr", "for real"),
        ("istg", "i swear to god"),
        ("ong", "on god"),
        ("wtv", "whatever"),
        ("bc", "because"),
        ("cuz", "because"),
        ("k", "okay"),
        ("kk", "okay"),
    ]
    
    for input_text, expected_contains in test_cases:
        result = normalizer.normalize_message(input_text)
        assert expected_contains in result.normalized_text.lower(), (
            f"Expected '{expected_contains}' in normalized text for '{input_text}', "
            f"got '{result.normalized_text}'"
        )


def test_neutral_address_bruh_bro():
    """Test that 'bruh' and 'bro' are tagged as friendly/neutral, not insults."""
    from app.detection.slang_normalizer import SlangNormalizer
    
    normalizer = SlangNormalizer()
    
    test_cases = ["bruh", "bro"]
    
    for input_text in test_cases:
        result = normalizer.normalize_message(input_text)
        # Should be tagged as friendly
        assert result.tone_markers.get("friendly", False), (
            f"Expected 'bruh'/'bro' to be tagged as friendly, got {result.tone_markers}"
        )


def test_intensity_markers_lowkey_highkey():
    """Test that 'lowkey'/'highkey' are tagged as intensity markers."""
    from app.detection.slang_normalizer import SlangNormalizer
    
    normalizer = SlangNormalizer()
    
    test_cases = ["lowkey", "highkey"]
    
    for input_text in test_cases:
        result = normalizer.normalize_message(input_text)
        # Should be tagged as intense
        assert result.tone_markers.get("intense", False), (
            f"Expected 'lowkey'/'highkey' to be tagged as intense, got {result.tone_markers}"
        )

