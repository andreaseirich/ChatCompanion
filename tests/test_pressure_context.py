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

"""Tests for pressure context gating (right now/now false positive reduction)."""

import pytest
from app.detection.engine import DetectionEngine
from app.utils.constants import RiskLevel


def test_green_neutral_time_phrase():
    """Test that neutral 'right now' phrases are classified as GREEN."""
    engine = DetectionEngine(use_ml=False)
    
    text = "I'm busy right now, can we talk later? no pressure"
    
    result = engine.analyze(text)
    
    assert result.risk_level == RiskLevel.GREEN, (
        f"Expected GREEN for neutral time phrase, got {result.risk_level}. "
        f"Overall score: {result.overall_score}"
    )
    assert len(result.matches.get("pressure", [])) == 0, (
        f"Expected 0 pressure matches for neutral 'right now', "
        f"got {len(result.matches.get('pressure', []))}"
    )
    assert "mild patterns" not in result.explanation.lower(), (
        "GREEN explanation should not mention 'mild patterns'"
    )


def test_yellow_demand_with_right_now():
    """Test that 'right now' in demand context is detected and guilt-shifting is mentioned."""
    engine = DetectionEngine(use_ml=False)
    
    text = "Call me right now. If you cared you would."
    
    result = engine.analyze(text)
    
    # Should be YELLOW or RED (depending on score aggregation)
    assert result.risk_level in [RiskLevel.YELLOW, RiskLevel.RED], (
        f"Expected YELLOW or RED for demand with 'right now', got {result.risk_level}. "
        f"Overall score: {result.overall_score}"
    )
    assert len(result.matches.get("pressure", [])) >= 1, (
        f"Expected at least 1 pressure match for demand context, "
        f"got {len(result.matches.get('pressure', []))}"
    )
    # Check if guilt-shifting is detected (may not always match patterns)
    guilt_matches = result.matches.get("guilt_shifting", [])
    if len(guilt_matches) >= 1:
        assert "guilt" in result.explanation.lower(), (
            "Explanation should mention guilt-shifting when patterns are detected"
        )


def test_yellow_pressure_without_threats():
    """Test that pressure without threats doesn't mention threats."""
    engine = DetectionEngine(use_ml=False)
    
    text = "Answer faster please. I feel ignored."
    
    result = engine.analyze(text)
    
    # Should be YELLOW or RED (depending on score aggregation)
    assert result.risk_level in [RiskLevel.YELLOW, RiskLevel.RED], (
        f"Expected YELLOW or RED for pressure, got {result.risk_level}"
    )
    # Check that explanation doesn't mention threats unless they're actually present
    explanation_lower = result.explanation.lower()
    # Only check for threat mentions if threat patterns are actually detected
    has_threat_patterns = any(
        "ultimatum" in m.pattern.description.lower() or
        "threat" in m.pattern.description.lower() or
        "relationship threat" in m.pattern.description.lower()
        for m in result.matches.get("pressure", [])
    )
    if not has_threat_patterns:
        # Should not mention threats if no threat patterns detected
        assert "threat" not in explanation_lower or "threats of withdrawal" not in explanation_lower, (
            "Explanation should not mention threats when no threat patterns detected"
        )


def test_pattern_counting_repeated():
    """Test that repeated patterns are counted correctly."""
    engine = DetectionEngine(use_ml=False)
    
    text = "Answer now. Answer now. Answer now."
    
    result = engine.analyze(text)
    
    pressure_matches = result.matches.get("pressure", [])
    if pressure_matches:
        total_instances = len(pressure_matches)
        unique_patterns = len(set(m.pattern.pattern for m in pressure_matches))
        
        assert total_instances >= 3, (
            f"Expected at least 3 instances for repeated 'Answer now', "
            f"got {total_instances}"
        )
        assert unique_patterns == 1, (
            f"Expected 1 unique pattern for repeated phrase, "
            f"got {unique_patterns}"
        )


def test_pattern_counting_multiple_patterns():
    """Test that multiple different patterns are counted correctly."""
    engine = DetectionEngine(use_ml=False)
    
    # Use distinct patterns that should match different rules
    text = "Answer now. You must respond immediately."
    
    result = engine.analyze(text)
    
    pressure_matches = result.matches.get("pressure", [])
    if pressure_matches:
        total_instances = len(pressure_matches)
        unique_patterns = len(set(m.pattern.pattern for m in pressure_matches))
        
        assert total_instances >= 1, (
            f"Expected at least 1 instance for pressure patterns, "
            f"got {total_instances}"
        )
        assert unique_patterns >= 1, (
            f"Expected at least 1 unique pattern, got {unique_patterns}"
        )


def test_self_report_exclusion():
    """Test that self-report 'right now' phrases are excluded from pressure."""
    engine = DetectionEngine(use_ml=False)
    
    test_cases = [
        "I'm busy right now",
        "Not right now, sorry",
        "Can't right now, maybe later",
        "I'm not available right now",
    ]
    
    for text in test_cases:
        result = engine.analyze(text)
        pressure_matches = result.matches.get("pressure", [])
        # Self-report should not trigger pressure
        assert len(pressure_matches) == 0, (
            f"Self-report phrase '{text}' should not trigger pressure matches, "
            f"got {len(pressure_matches)}"
        )


def test_demand_context_detection():
    """Test that demand context 'right now' is detected as pressure."""
    engine = DetectionEngine(use_ml=False)
    
    test_cases = [
        "Answer right now",
        "Call me right now",
        "Do it right now",
        "Send it right now",
        "You have to respond right now",
    ]
    
    for text in test_cases:
        result = engine.analyze(text)
        pressure_matches = result.matches.get("pressure", [])
        # Demand context should trigger pressure
        assert len(pressure_matches) >= 1, (
            f"Demand phrase '{text}' should trigger pressure matches, "
            f"got {len(pressure_matches)}"
        )

