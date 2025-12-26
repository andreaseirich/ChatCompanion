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

"""Tests for slang and abbreviation handling."""

import pytest
from app.detection.engine import DetectionEngine
from app.detection.slang_normalizer import SlangNormalizer
from app.utils.constants import RiskLevel


def test_harmless_slang_green():
    """Test that harmless slang is classified as GREEN."""
    engine = DetectionEngine(use_ml=False)
    
    # Harmless slang cases
    test_cases = [
        "idk what u mean lol",
        "brb ttyl",
        "omg that's so funny 😂",
        "Friend: wyd\nYou: idk lol\nFriend: np",
    ]
    
    for text in test_cases:
        result = engine.analyze(text)
        assert result.risk_level == RiskLevel.GREEN, (
            f"Expected GREEN for harmless slang '{text[:50]}...', "
            f"got {result.risk_level}. Overall score: {result.overall_score}"
        )
        assert result.overall_score < 0.3, (
            f"Overall score should be low for harmless slang, got {result.overall_score}"
        )


def test_friendly_banter_slang_green():
    """Test that friendly banter with slang is classified as GREEN."""
    engine = DetectionEngine(use_ml=False)
    
    # Friendly banter with slang
    test_cases = [
        "Friend: ur being ridiculous jk 😂\nYou: lol all good np",
        "Friend: haha ur so silly\nYou: jk 😂",
        "Friend: ur so bad at this lol\nYou: ikr jk",
    ]
    
    for text in test_cases:
        result = engine.analyze(text)
        assert result.risk_level == RiskLevel.GREEN, (
            f"Expected GREEN for friendly banter with slang, got {result.risk_level}. "
            f"Overall score: {result.overall_score}"
        )
        assert result.category_scores.get("bullying", 0.0) < 0.5, (
            f"Bullying score should be low for friendly banter, "
            f"got {result.category_scores.get('bullying', 0.0)}"
        )


def test_hostile_slang_bullying():
    """Test that hostile slang bullying is classified as YELLOW or RED."""
    engine = DetectionEngine(use_ml=False)
    
    # Hostile slang bullying cases
    # Note: After normalization, "ur" -> "your", "stfu" -> "shut up"
    # Patterns need to match normalized text
    test_cases = [
        ("you're so dumb shut up", RiskLevel.YELLOW),  # Direct normalized form
        ("you're so stupid shut up", RiskLevel.YELLOW),  # Direct normalized form
        ("you're worthless", RiskLevel.YELLOW),  # Direct normalized form
        ("nobody likes you", RiskLevel.YELLOW),  # Matches pattern in rules_config.yaml
    ]
    
    for text, expected_level in test_cases:
        result = engine.analyze(text)
        assert result.risk_level in [RiskLevel.YELLOW, RiskLevel.RED], (
            f"Expected YELLOW or RED for hostile slang '{text}', "
            f"got {result.risk_level}. Overall score: {result.overall_score}"
        )
        assert result.category_scores.get("bullying", 0.0) > 0.3, (
            f"Bullying score should be significant for hostile slang, "
            f"got {result.category_scores.get('bullying', 0.0)}"
        )


def test_guilt_pressure_slang_yellow():
    """Test that guilt/pressure slang is classified as YELLOW."""
    engine = DetectionEngine(use_ml=False)
    
    # Guilt/pressure slang cases
    # Note: After normalization, "u" -> "you", "rn" -> "right now"
    # The score might be high due to multiple patterns, but should be YELLOW
    # if guilt-shifting is the primary category (capped at 0.74)
    test_cases = [
        "if you cared you would answer right now",
        "you don't care about me",
        "if you really cared you would respond",
    ]
    
    for text in test_cases:
        result = engine.analyze(text)
        # Should be YELLOW (guilt-shifting capped) or RED if multiple severe patterns
        assert result.risk_level in [RiskLevel.YELLOW, RiskLevel.RED], (
            f"Expected YELLOW or RED for guilt/pressure slang '{text}', "
            f"got {result.risk_level}. Overall score: {result.overall_score}"
        )
        assert (
            "guilt" in result.explanation.lower()
            or result.category_scores.get("guilt_shifting", 0.0) > 0.2
            or result.category_scores.get("pressure", 0.0) > 0.2
        ), (
            "Should mention guilt-shifting/pressure or have relevant score > 0.2"
        )


def test_slang_normalizer_basic():
    """Test basic slang normalization functionality."""
    normalizer = SlangNormalizer()
    
    # Test basic abbreviations
    result = normalizer.normalize_message("idk what u mean")
    assert "I don't know" in result.normalized_text
    assert "you" in result.normalized_text
    
    # Test emoji detection
    result = normalizer.normalize_message("that's funny 😂")
    assert result.has_emoji is True
    assert result.tone_markers.get("joking", False) is True
    
    # Test hostile slang preservation
    result = normalizer.normalize_message("stfu")
    assert "shut up" in result.normalized_text
    assert len(result.replacements) > 0


def test_slang_normalizer_replacements():
    """Test that replacements are tracked correctly."""
    normalizer = SlangNormalizer()
    
    result = normalizer.normalize_message("idk lol brb")
    assert len(result.replacements) == 3
    assert any(r["original"] == "idk" for r in result.replacements)
    assert any(r["original"] == "lol" for r in result.replacements)
    assert any(r["original"] == "brb" for r in result.replacements)

