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

"""Tests for false positive reduction, especially friendly teasing."""

import pytest
from app.detection.engine import DetectionEngine
from app.utils.constants import RiskLevel


def test_friendly_teasing_with_joking_markers():
    """Test that friendly teasing with joking markers is classified as GREEN."""
    engine = DetectionEngine(use_ml=False)  # Use rules-only for consistent testing
    
    # Friendly teasing with joking markers
    text = """
    Friend: Hey, you're being such a baby about this lol
    You: What do you mean? 😂
    Friend: Everyone else is doing it, why can't you? jk
    You: Haha, all good!
    Friend: Just joking, no worries
    """
    
    result = engine.analyze(text)
    
    # Should be GREEN (friendly teasing, not bullying)
    assert result.risk_level == RiskLevel.GREEN, (
        f"Expected GREEN for friendly teasing, got {result.risk_level}. "
        f"Overall score: {result.overall_score}"
    )
    assert result.category_scores.get("bullying", 0.0) < 0.5, (
        f"Bullying score should be low for friendly teasing, got {result.category_scores.get('bullying', 0.0)}"
    )


def test_friendly_teasing_mutual():
    """Test that mutual teasing between friends is classified as GREEN."""
    engine = DetectionEngine(use_ml=False)
    
    # Mutual teasing - both sides tease
    text = """
    Friend1: You're so slow at this game haha
    Friend2: Yeah well you're terrible at math 😂
    Friend1: Touché! All good though
    Friend2: Just joking around
    """
    
    result = engine.analyze(text)
    
    assert result.risk_level == RiskLevel.GREEN, (
        f"Expected GREEN for mutual friendly teasing, got {result.risk_level}"
    )


def test_friendly_teasing_positive_ending():
    """Test that teasing with positive endings is classified as GREEN."""
    engine = DetectionEngine(use_ml=False)
    
    text = """
    Friend: You're being ridiculous
    You: What?
    Friend: Just kidding! All good, no worries
    You: Haha okay
    """
    
    result = engine.analyze(text)
    
    assert result.risk_level == RiskLevel.GREEN, (
        f"Expected GREEN for teasing with positive ending, got {result.risk_level}"
    )


def test_realistic_bullying_one_sided():
    """Test that one-sided bullying without joking markers is classified as YELLOW or RED."""
    engine = DetectionEngine(use_ml=False)
    
    # One-sided bullying - no joking markers, negative tone
    text = """
    Jordan: Hey loser
    Taylor: What?
    Jordan: You're so stupid. Everyone thinks you're annoying.
    Taylor: That's not true...
    Jordan: Yes it is. Nobody likes you. You're ugly and worthless.
    Taylor: Please stop
    Jordan: Why should I? You deserve it.
    """
    
    result = engine.analyze(text)
    
    # Should be YELLOW or RED (not GREEN)
    assert result.risk_level in [RiskLevel.YELLOW, RiskLevel.RED], (
        f"Expected YELLOW or RED for one-sided bullying, got {result.risk_level}"
    )
    assert result.category_scores.get("bullying", 0.0) > 0.3, (
        f"Bullying score should be significant, got {result.category_scores.get('bullying', 0.0)}"
    )


def test_realistic_bullying_severe_insults():
    """Test that severe insults without joking markers are classified as RED."""
    engine = DetectionEngine(use_ml=False)
    
    text = """
    Jordan: You're a waste of space
    Taylor: That's really mean
    Jordan: You deserve it. Kill yourself.
    """
    
    result = engine.analyze(text)
    
    # Should be RED for severe threats
    assert result.risk_level == RiskLevel.RED, (
        f"Expected RED for severe threats, got {result.risk_level}"
    )


def test_realistic_bullying_no_joking_markers():
    """Test that insults without joking markers are classified as risky."""
    engine = DetectionEngine(use_ml=False)
    
    text = """
    Person: You're pathetic
    You: What did I do?
    Person: Everything. You're the problem.
    """
    
    result = engine.analyze(text)
    
    # Should not be GREEN
    assert result.risk_level != RiskLevel.GREEN, (
        f"Expected YELLOW or RED for bullying without joking markers, got {result.risk_level}"
    )


def test_acceptance_criteria_green_chat():
    """Test acceptance criteria: GREEN chat with 'no pressure' should be GREEN."""
    engine = DetectionEngine(use_ml=False)
    
    text = """
    Friend: Hey, want to hang out later?
    You: Maybe, I'm not sure
    Friend: No pressure at all! Take your time
    You: Thanks
    Friend: That's okay, whenever you're ready
    """
    
    result = engine.analyze(text)
    
    assert result.risk_level == RiskLevel.GREEN, (
        f"Expected GREEN for 'no pressure' chat, got {result.risk_level}"
    )
    assert "no pressure" in result.explanation.lower() or result.overall_score < 0.3, (
        "Should detect no pressure or have low overall score"
    )


def test_acceptance_criteria_yellow_guilt_shifting():
    """Test acceptance criteria: YELLOW chat with guilt-shifting should mention it."""
    engine = DetectionEngine(use_ml=False)
    
    text = """
    Person: If you cared about me, you would have answered sooner
    You: I was busy
    Person: I'm the only one trying here
    You: That's not true
    """
    
    result = engine.analyze(text)
    
    assert result.risk_level == RiskLevel.YELLOW, (
        f"Expected YELLOW for guilt-shifting, got {result.risk_level}"
    )
    assert "guilt" in result.explanation.lower() or result.category_scores.get("guilt_shifting", 0.0) > 0.2, (
        "Should mention guilt-shifting or have guilt_shifting score > 0.2"
    )


def test_acceptance_criteria_red_coercive_control():
    """Test acceptance criteria: RED chat with coercive control should be RED."""
    engine = DetectionEngine(use_ml=False)
    
    text = """
    Person: Delete those messages and prove it
    You: Why?
    Person: Don't talk to other people about this
    You: But...
    Person: If you tell anyone, we're done
    """
    
    result = engine.analyze(text)
    
    assert result.risk_level == RiskLevel.RED, (
        f"Expected RED for coercive control, got {result.risk_level}"
    )
    assert "secrecy" in result.explanation.lower() or "isolation" in result.explanation.lower(), (
        "Should mention secrecy or isolation in explanation"
    )
    # Should have multiple pattern matches
    total_matches = sum(len(matches) for matches in result.matches.values())
    assert total_matches > 1, (
        f"Expected multiple pattern matches for RED case, got {total_matches}"
    )


def test_youth_friendly_banter_slang():
    """Test that youth-friendly banter with slang abbreviations is classified as GREEN."""
    engine = DetectionEngine(use_ml=False)
    
    text = """
    Friend: ur being so ridiculous rn lol
    You: idk what u mean jk 😂
    Friend: haha all good np
    You: ttyl
    """
    
    result = engine.analyze(text)
    
    assert result.risk_level == RiskLevel.GREEN, (
        f"Expected GREEN for youth-friendly banter with slang, got {result.risk_level}. "
        f"Overall score: {result.overall_score}"
    )
    assert result.category_scores.get("bullying", 0.0) < 0.5, (
        f"Bullying score should be low for friendly banter, "
        f"got {result.category_scores.get('bullying', 0.0)}"
    )


def test_slang_banter_with_mutuality_and_repair():
    """Test that slang banter with mutuality and repair markers is GREEN."""
    engine = DetectionEngine(use_ml=False)
    
    text = """
    A: bruh ur wild frfr 😂
    B: lol u too
    A: jk all good np
    B: haha my bad
    """
    
    result = engine.analyze(text)
    
    assert result.risk_level == RiskLevel.GREEN, (
        f"Expected GREEN for banter with mutuality and repair, got {result.risk_level}"
    )

