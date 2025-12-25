"""Tests for model inference."""

import pytest
from app.models_local.embeddings import EmbeddingModel
from app.models_local.classifier import RiskClassifier


def test_embedding_model_initialization():
    """Test that embedding model initializes (may not be available)."""
    model = EmbeddingModel()
    assert model is not None
    # Model may not be available, which is okay
    # The system should work in rules-only mode


def test_classifier_initialization():
    """Test that classifier initializes."""
    embedding_model = EmbeddingModel()
    classifier = RiskClassifier(embedding_model)
    assert classifier is not None


def test_classifier_without_ml():
    """Test that classifier handles missing ML gracefully."""
    embedding_model = EmbeddingModel()
    # If model not available, should still initialize
    classifier = RiskClassifier(embedding_model)
    
    # Classification should return empty dict if ML not available
    result = classifier.classify("Test text")
    assert isinstance(result, dict)

