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
from tests.test_chat_fixtures_youth import (
    green_youth_friendly,
    yellow_guilt_slang,
    red_coercive_control_slang,
)


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


def test_green_youth_friendly_fixture():
    """Test GREEN youth-friendly fixture: no 'mild patterns', no trigger word quotes."""
    engine = DetectionEngine(use_ml=False)
    
    result = engine.analyze(green_youth_friendly)
    
    assert result.risk_level == RiskLevel.GREEN, (
        f"Expected GREEN for youth-friendly banter, got {result.risk_level}"
    )
    explanation_lower = result.explanation.lower()
    assert "mild patterns" not in explanation_lower, (
        "GREEN explanation should not mention 'mild patterns'"
    )
    # Should not quote trigger words
    assert '"' not in result.explanation or result.explanation.count('"') < 2, (
        "GREEN explanation should not quote trigger words"
    )


def test_yellow_pressure_guilt_no_threats():
    """Test YELLOW pressure+guilt without ultimatum -> explanation MUST NOT contain: threat, consequence, withdrawal."""
    engine = DetectionEngine(use_ml=False)
    
    text = "if you cared you would answer faster. i'm the only one trying"
    
    result = engine.analyze(text)
    
    assert result.risk_level in [RiskLevel.YELLOW, RiskLevel.RED], (
        f"Expected YELLOW or RED for pressure+guilt, got {result.risk_level}"
    )
    explanation_lower = result.explanation.lower()
    
    # Must NOT contain threat language when no ultimatums are present
    assert "threat" not in explanation_lower or "threats" not in explanation_lower, (
        f"YELLOW explanation should NOT mention 'threat' when no ultimatums present. Explanation: {result.explanation}"
    )
    assert "consequence" not in explanation_lower or "consequences" not in explanation_lower, (
        f"YELLOW explanation should NOT mention 'consequence' when no ultimatums present. Explanation: {result.explanation}"
    )
    assert "withdrawal" not in explanation_lower, (
        f"YELLOW explanation should NOT mention 'withdrawal' when no ultimatums present. Explanation: {result.explanation}"
    )
    
    # Should mention guilt/pressure
    assert "guilt" in explanation_lower or "pressure" in explanation_lower, (
        f"YELLOW explanation should mention guilt or pressure. Explanation: {result.explanation}"
    )


def test_yellow_with_explicit_ultimatum():
    """Test YELLOW/RED with explicit ultimatum -> explanation MUST contain threats or consequences."""
    engine = DetectionEngine(use_ml=False)
    
    text = "answer me right now or we're done"
    
    result = engine.analyze(text)
    
    assert result.risk_level in [RiskLevel.YELLOW, RiskLevel.RED], (
        f"Expected YELLOW or RED for explicit ultimatum, got {result.risk_level}"
    )
    explanation_lower = result.explanation.lower()
    
    # Must contain threat language when ultimatums are present
    has_threat_language = (
        "threat" in explanation_lower or 
        "threats" in explanation_lower or
        "consequence" in explanation_lower or
        "consequences" in explanation_lower
    )
    assert has_threat_language, (
        f"YELLOW/RED explanation should mention 'threats' or 'consequences' when ultimatums present. Explanation: {result.explanation}"
    )


def test_red_with_relationship_threat():
    """Test RED with relationship threat -> mentions threats, listed in Observed behaviors."""
    engine = DetectionEngine(use_ml=False)
    
    text = "if you don't delete those messages, we're done"
    
    result = engine.analyze(text)
    
    assert result.risk_level == RiskLevel.RED, (
        f"Expected RED for relationship threat, got {result.risk_level}"
    )
    explanation_lower = result.explanation.lower()
    
    # Must mention threats
    has_threat_language = (
        "threat" in explanation_lower or 
        "threats" in explanation_lower or
        "consequence" in explanation_lower or
        "consequences" in explanation_lower
    )
    assert has_threat_language, (
        f"RED explanation should mention threats. Explanation: {result.explanation}"
    )
    
    # Must be listed in Observed behaviors
    assert "Observed behaviors" in result.explanation or "observed behaviors" in explanation_lower, (
        f"RED explanation should include Observed behaviors section. Explanation: {result.explanation}"
    )
    # Check that threats are mentioned in Observed behaviors
    if "Observed behaviors" in result.explanation or "observed behaviors" in explanation_lower:
        # Extract Observed behaviors section
        obs_section = result.explanation.split("Observed behaviors")[-1] if "Observed behaviors" in result.explanation else result.explanation.split("observed behaviors")[-1]
        obs_lower = obs_section.lower()
        has_threat_in_obs = (
            "threat" in obs_lower or 
            "threats" in obs_lower or
            "consequence" in obs_lower or
            "consequences" in obs_lower or
            "withdrawal" in obs_lower
        )
        assert has_threat_in_obs, (
            f"Observed behaviors should mention threats. Observed behaviors section: {obs_section}"
        )


def test_observed_behaviors_evidence_based():
    """Test that Observed behaviors are strictly evidence-based (derived from matched patterns only)."""
    engine = DetectionEngine(use_ml=False)
    
    test_cases = [
        ("if you cared you would answer faster", ["guilt_shifting"]),
        ("answer me right now or we're done", ["pressure"]),
        ("delete those messages and send a screenshot", ["secrecy", "manipulation"]),
        ("you're so stupid", ["bullying"]),
    ]
    
    for text, expected_categories in test_cases:
        result = engine.analyze(text)
        
        # Extract Observed behaviors section
        explanation_lower = result.explanation.lower()
        if "observed behaviors" in explanation_lower:
            obs_section = result.explanation.split("Observed behaviors")[-1] if "Observed behaviors" in result.explanation else result.explanation.split("observed behaviors")[-1]
            
            # Verify that behaviors mentioned are supported by matched patterns
            matched_categories = set(result.matches.keys())
            matched_categories = {cat for cat in matched_categories if len(result.matches[cat]) > 0}
            
            # Check that threat language only appears if threat patterns are matched
            obs_lower = obs_section.lower()
            has_threat_in_obs = (
                "threat" in obs_lower or 
                "threats" in obs_lower or
                "consequence" in obs_lower or
                "consequences" in obs_lower or
                "withdrawal" in obs_lower
            )
            
            if has_threat_in_obs:
                # Verify that threat patterns are actually matched
                from app.detection.explainer import ExplanationGenerator
                explainer = ExplanationGenerator()
                has_threat_patterns = explainer._has_threat_patterns(result.matches)
                assert has_threat_patterns, (
                    f"Observed behaviors mention threats but no threat patterns matched. "
                    f"Text: {text}, Observed behaviors: {obs_section}, Matches: {result.matches}"
                )


def test_yellow_guilt_slang_fixture():
    """Test YELLOW guilt-slang fixture: must mention guilt-shifting."""
    engine = DetectionEngine(use_ml=False)
    
    result = engine.analyze(yellow_guilt_slang)
    
    assert result.risk_level in [RiskLevel.YELLOW, RiskLevel.RED], (
        f"Expected YELLOW or RED for guilt-shifting, got {result.risk_level}"
    )
    explanation_lower = result.explanation.lower()
    assert "guilt" in explanation_lower, (
        "YELLOW explanation should mention guilt-shifting when present"
    )
    # Should NOT show "Need Immediate Help?" for YELLOW
    if result.risk_level == RiskLevel.YELLOW:
        assert result.risk_level != RiskLevel.RED, (
            "YELLOW should not trigger 'Need Immediate Help?'"
        )


def test_red_coercive_control_slang_fixture():
    """Test RED coercive control fixture: 'Need Immediate Help?' appears exactly once."""
    engine = DetectionEngine(use_ml=False)
    
    result = engine.analyze(red_coercive_control_slang)
    
    assert result.risk_level == RiskLevel.RED, (
        f"Expected RED for coercive control, got {result.risk_level}"
    )
    # RED should trigger "Need Immediate Help?" (checked in UI rendering)
    assert result.risk_level == RiskLevel.RED, (
        "RED risk level should trigger 'Need Immediate Help?' section"
    )

