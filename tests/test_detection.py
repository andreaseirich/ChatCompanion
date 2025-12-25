"""Tests for detection engine."""

import pytest
from app.detection.engine import DetectionEngine
from app.utils.constants import RiskLevel


def test_detection_engine_initialization():
    """Test that detection engine initializes correctly."""
    engine = DetectionEngine(use_ml=False)  # Use rules-only for testing
    assert engine is not None
    assert engine.rule_engine is not None


def test_rules_only_mode():
    """Test that rules-only mode works when ML is disabled."""
    engine = DetectionEngine(use_ml=False)
    text = "You are so stupid. Nobody likes you."
    result = engine.analyze(text)
    
    assert result is not None
    assert result.risk_level in [RiskLevel.GREEN, RiskLevel.YELLOW, RiskLevel.RED]
    assert result.overall_score >= 0.0
    assert result.overall_score <= 1.0


def test_high_risk_detection():
    """Test detection of high-risk content."""
    engine = DetectionEngine(use_ml=False)
    text = "Don't tell anyone. Meet me alone. Delete these messages."
    result = engine.analyze(text)
    
    # Should detect multiple risk categories
    assert len(result.category_scores) > 0
    # Should have high overall score
    assert result.overall_score > 0.5


def test_low_risk_detection():
    """Test detection of low-risk content."""
    engine = DetectionEngine(use_ml=False)
    text = "Hey! How was your day? Want to study together?"
    result = engine.analyze(text)
    
    # Should have low risk (GREEN)
    assert result.risk_level == RiskLevel.GREEN
    assert result.overall_score < 0.3


def test_mild_risk_detection():
    """Test detection of mild/ambiguous content (should be YELLOW)."""
    engine = DetectionEngine(use_ml=False)
    text = "Everyone else is doing it, why can't you? Don't be scared."
    result = engine.analyze(text)
    
    # Should be YELLOW (mild pressure, not severe)
    assert result.risk_level == RiskLevel.YELLOW
    assert 0.3 <= result.overall_score < 0.8


def test_severe_risk_detection():
    """Test detection of clearly severe content (should be RED)."""
    engine = DetectionEngine(use_ml=False)
    text = "You're so stupid. Nobody likes you. Kill yourself."
    result = engine.analyze(text)
    
    # Should be RED (severe bullying with threats)
    assert result.risk_level == RiskLevel.RED
    assert result.overall_score >= 0.8


def test_grooming_high_risk():
    """Test detection of grooming patterns (should be RED)."""
    engine = DetectionEngine(use_ml=False)
    text = "You're so mature for your age. Meet me alone without telling anyone. Don't tell your parents."
    result = engine.analyze(text)
    
    # Should be RED (multiple severe grooming patterns)
    assert result.risk_level == RiskLevel.RED
    assert result.overall_score >= 0.8


def test_professional_conversation_low_risk():
    """Test that professional/workplace conversations get appropriate guidance."""
    engine = DetectionEngine(use_ml=False)
    text = "Alex: Hey Sam, I need to talk about the bug fix. Sam: Sure, what's the issue? Alex: The code broke production. Sam: I'm so sorry! I'll fix it immediately."
    result = engine.analyze(text)
    
    # Should be GREEN or low YELLOW (professional stress, not abuse)
    assert result.risk_level in [RiskLevel.GREEN, RiskLevel.YELLOW]
    assert result.overall_score < 0.8
    
    # Guidance should NOT mention "trusted adult" for professional context
    assert "trusted adult" not in result.explanation.lower() or result.risk_level == RiskLevel.RED
    # Advice should be context-appropriate
    advice_text = " ".join(result.advice).lower()
    if result.risk_level != RiskLevel.RED:
        assert "trusted adult" not in advice_text


def test_guidance_by_risk_level():
    """Test that guidance messages match risk levels appropriately."""
    engine = DetectionEngine(use_ml=False)
    
    # Low risk - should get neutral guidance
    low_risk_text = "Hey! How was your day? Want to study together?"
    low_result = engine.analyze(low_risk_text)
    assert low_result.risk_level == RiskLevel.GREEN
    assert "trusted adult" not in " ".join(low_result.advice).lower()
    
    # High risk - should get child-safety guidance
    high_risk_text = "You're so stupid. Nobody likes you. Kill yourself."
    high_result = engine.analyze(high_risk_text)
    assert high_result.risk_level == RiskLevel.RED
    # RED should mention trusted adult
    advice_text = " ".join(high_result.advice).lower()
    assert "trusted adult" in advice_text or "trusted adult" in high_result.explanation.lower()


def test_explanation_generation():
    """Test that explanations are generated."""
    engine = DetectionEngine(use_ml=False)
    text = "You are so stupid."
    result = engine.analyze(text)
    
    assert result.explanation is not None
    assert len(result.explanation) > 0


def test_advice_generation():
    """Test that advice is provided."""
    engine = DetectionEngine(use_ml=False)
    text = "Test text"
    result = engine.analyze(text)
    
    assert result.advice is not None
    assert len(result.advice) > 0

