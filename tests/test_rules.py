"""Tests for rules engine."""

import pytest
from app.rules.rule_engine import RuleEngine


def test_rule_engine_initialization():
    """Test that rule engine initializes correctly."""
    engine = RuleEngine()
    assert engine is not None


def test_bullying_detection():
    """Test detection of bullying patterns."""
    engine = RuleEngine()
    text = "You are so stupid and ugly. Nobody likes you."
    result = engine.analyze(text)
    
    assert "bullying" in result["category_scores"]
    assert result["category_scores"]["bullying"] > 0


def test_manipulation_detection():
    """Test detection of manipulation patterns."""
    engine = RuleEngine()
    text = "If you really cared about me, you would do this."
    result = engine.analyze(text)
    
    assert "manipulation" in result["category_scores"]
    assert result["category_scores"]["manipulation"] > 0


def test_secrecy_detection():
    """Test detection of secrecy demands."""
    engine = RuleEngine()
    text = "Don't tell anyone about this. Keep it our secret."
    result = engine.analyze(text)
    
    assert "secrecy" in result["category_scores"]
    assert result["category_scores"]["secrecy"] > 0


def test_safe_text():
    """Test that safe text doesn't trigger false positives."""
    engine = RuleEngine()
    text = "Hey! How was your day? Want to hang out later?"
    result = engine.analyze(text)
    
    # Safe text should have low or zero scores
    max_score = max(result["category_scores"].values()) if result["category_scores"] else 0
    assert max_score < 0.5  # Should be below yellow threshold

