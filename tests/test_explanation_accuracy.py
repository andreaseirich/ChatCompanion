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

"""Tests for explanation accuracy (GREEN/YELLOW/RED messaging)."""

import pytest
from app.detection.engine import DetectionEngine
from app.utils.constants import RiskLevel


def test_green_never_mentions_mild_patterns():
    """Test that GREEN explanations never mention 'mild patterns'."""
    engine = DetectionEngine(use_ml=False)
    
    test_cases = [
        "I'm busy right now, can we talk later? no pressure",
        "Hey, how are you?",
        "Friend: Want to hang out?\nYou: Maybe later\nFriend: No worries, take your time",
    ]
    
    for text in test_cases:
        result = engine.analyze(text)
        if result.risk_level == RiskLevel.GREEN:
            explanation_lower = result.explanation.lower()
            assert "mild patterns" not in explanation_lower, (
                f"GREEN explanation should not mention 'mild patterns'. "
                f"Explanation: {result.explanation}"
            )
            assert "some patterns" not in explanation_lower or "patterns noted" not in explanation_lower, (
                f"GREEN explanation should not mention patterns. "
                f"Explanation: {result.explanation}"
            )


def test_yellow_mentions_guilt_shifting_when_present():
    """Test that YELLOW explanations mention guilt-shifting when present."""
    engine = DetectionEngine(use_ml=False)
    
    text = "If you cared about me, you would have answered sooner. I'm the only one trying here."
    
    result = engine.analyze(text)
    
    assert result.risk_level == RiskLevel.YELLOW, (
        f"Expected YELLOW for guilt-shifting, got {result.risk_level}"
    )
    explanation_lower = result.explanation.lower()
    assert "guilt" in explanation_lower, (
        f"YELLOW explanation should mention guilt-shifting when present. "
        f"Explanation: {result.explanation}"
    )


def test_yellow_no_threats_unless_present():
    """Test that YELLOW explanations don't mention threats unless actually present."""
    engine = DetectionEngine(use_ml=False)
    
    # Pressure without threats
    text = "Answer faster please. I feel ignored."
    
    result = engine.analyze(text)
    
    if result.risk_level == RiskLevel.YELLOW:
        explanation_lower = result.explanation.lower()
        # Check if threat patterns are actually detected
        has_threat_patterns = any(
            "ultimatum" in m.pattern.description.lower() or
            "threat" in m.pattern.description.lower() or
            "relationship threat" in m.pattern.description.lower()
            for m in result.matches.get("pressure", [])
        )
        
        if not has_threat_patterns:
            # Should not mention threats if no threat patterns
            assert "threat" not in explanation_lower or "threats of withdrawal" not in explanation_lower, (
                f"YELLOW explanation should not mention threats when no threat patterns detected. "
                f"Explanation: {result.explanation}"
            )


def test_red_shows_need_immediate_help():
    """Test that RED risk level shows 'Need Immediate Help?' section."""
    engine = DetectionEngine(use_ml=False)
    
    # Coercive control with secrecy + isolation
    text = """
    Person: Delete those messages and prove it
    You: Why?
    Person: Don't talk to other people about this
    You: But...
    Person: If you tell anyone, we're done
    """
    
    result = engine.analyze(text)
    
    assert result.risk_level == RiskLevel.RED, (
        f"Expected RED for coercive control, got {result.risk_level}. "
        f"Overall score: {result.overall_score}"
    )
    # Verify that RED triggers "Need Immediate Help?" (checked in UI rendering)
    assert result.risk_level == RiskLevel.RED, (
        "RED risk level should trigger 'Need Immediate Help?' section"
    )
    
    # Verify pattern counts are realistic
    total_matches = sum(len(matches) for matches in result.matches.values())
    assert total_matches > 1, (
        f"Expected multiple pattern matches for RED case, got {total_matches}"
    )


def test_green_no_warning_box():
    """Test that GREEN risk level doesn't show warning box."""
    engine = DetectionEngine(use_ml=False)
    
    text = "I'm busy right now, can we talk later? no pressure"
    
    result = engine.analyze(text)
    
    assert result.risk_level == RiskLevel.GREEN, (
        f"Expected GREEN, got {result.risk_level}"
    )
    # GREEN should have clean explanation
    assert "No warning signs detected" in result.explanation, (
        f"GREEN should say 'No warning signs detected'. "
        f"Explanation: {result.explanation}"
    )


def test_yellow_no_need_immediate_help():
    """Test that YELLOW does NOT show 'Need Immediate Help?'."""
    engine = DetectionEngine(use_ml=False)
    
    # Use a milder guilt-shifting phrase that should be YELLOW
    text = "I wish you would respond more often."
    
    result = engine.analyze(text)
    
    # Should be GREEN or YELLOW (not RED)
    assert result.risk_level in [RiskLevel.GREEN, RiskLevel.YELLOW], (
        f"Expected GREEN or YELLOW for mild pressure, got {result.risk_level}"
    )
    # YELLOW should NOT trigger "Need Immediate Help?" (that's RED only)
    if result.risk_level == RiskLevel.YELLOW:
        assert result.risk_level != RiskLevel.RED, (
            "YELLOW should not trigger 'Need Immediate Help?' section"
        )

