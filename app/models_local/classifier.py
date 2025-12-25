"""Risk classification using ML models."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from app.models_local.embeddings import EmbeddingModel
from app.utils.constants import RiskCategory

logger = logging.getLogger(__name__)

# Try to import scikit-learn, but allow fallback if not available
try:
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. ML classification will be disabled.")


class RiskClassifier:
    """Classifier for risk detection using embeddings."""

    def __init__(self, embedding_model: Optional[EmbeddingModel] = None):
        """
        Initialize risk classifier.

        Args:
            embedding_model: Pre-initialized embedding model.
                            If None, creates a new one.
        """
        if embedding_model is None:
            embedding_model = EmbeddingModel()
        self.embedding_model = embedding_model

        # Reference embeddings for risk categories (can be expanded)
        # These are example phrases that represent each risk category
        self.reference_phrases = {
            RiskCategory.BULLYING: [
                "You are ugly and stupid",
                "Nobody likes you",
                "Everyone hates you",
            ],
            RiskCategory.MANIPULATION: [
                "If you really cared about me, you would do this",
                "You owe me after all I did for you",
                "I'm the only one who understands you",
            ],
            RiskCategory.PRESSURE: [
                "You have to do this right now",
                "Don't be a baby, everyone else does it",
                "You must send this immediately",
            ],
            RiskCategory.SECRECY: [
                "Don't tell anyone about this",
                "Keep this our secret",
                "Delete these messages",
            ],
            RiskCategory.GUILT_SHIFTING: [
                "This is all your fault",
                "You made me do this",
                "This is because of you",
            ],
            RiskCategory.GROOMING: [
                "You're so mature for your age",
                "Adults won't understand us",
                "Meet me alone without telling anyone",
            ],
        }

        # Pre-compute reference embeddings if model is available
        self.reference_embeddings: Dict[str, List[List[float]]] = {}
        if self.embedding_model.available:
            self._precompute_references()

    def _precompute_references(self) -> None:
        """Pre-compute embeddings for reference phrases."""
        for category, phrases in self.reference_phrases.items():
            embeddings = self.embedding_model.encode(phrases)
            if embeddings:
                self.reference_embeddings[category] = embeddings

    def classify(self, text: str) -> Dict[str, float]:
        """
        Classify text for risk categories using semantic similarity.

        Args:
            text: Text to classify

        Returns:
            Dictionary mapping category to confidence score (0.0 - 1.0)
        """
        if not self.embedding_model.available or not SKLEARN_AVAILABLE:
            # Fallback: return empty scores (rules-only mode)
            return {}

        # Generate embedding for input text
        text_embedding = self.embedding_model.encode_single(text)
        if text_embedding is None:
            return {}

        text_embedding = np.array([text_embedding])
        category_scores = {}

        # Compare against reference embeddings for each category
        for category, ref_embeddings in self.reference_embeddings.items():
            if not ref_embeddings:
                category_scores[category] = 0.0
                continue

            # Calculate cosine similarity
            similarities = cosine_similarity(text_embedding, ref_embeddings)[0]
            # Use maximum similarity as category score
            max_similarity = float(np.max(similarities))
            category_scores[category] = max_similarity

        return category_scores

    def classify_batch(self, texts: List[str]) -> List[Dict[str, float]]:
        """
        Classify multiple texts.

        Args:
            texts: List of texts to classify

        Returns:
            List of category score dictionaries
        """
        return [self.classify(text) for text in texts]

