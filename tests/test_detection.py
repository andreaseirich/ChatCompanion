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
    
    # Should have low risk
    assert result.risk_level == RiskLevel.GREEN or result.overall_score < 0.3


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

