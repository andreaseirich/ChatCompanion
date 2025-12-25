"""Sentence embedding inference for semantic analysis."""

import logging
from pathlib import Path
from typing import List, Optional

from app.models_local.loader import ModelLoader

logger = logging.getLogger(__name__)

# Try to import sentence-transformers, but allow fallback if not available
try:
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available. ML features will be disabled.")


class EmbeddingModel:
    """Wrapper for sentence embedding model."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", models_dir: Optional[Path] = None):
        """
        Initialize embedding model.

        Args:
            model_name: Name of the sentence transformer model
            models_dir: Directory for model storage
        """
        self.model_name = model_name
        self.model = None
        self.loader = ModelLoader(models_dir)
        self.available = False

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self._load_model()

    def _load_model(self) -> None:
        """Load the sentence transformer model from local storage only."""
        try:
            # Try to load from local directory first
            model_path = self.loader.get_model_path(self.model_name)
            if model_path:
                logger.info(f"Loading model from local path: {model_path}")
                self.model = SentenceTransformer(str(model_path))
                self.available = True
                logger.info(f"Embedding model {self.model_name} loaded successfully")
            else:
                # Model not found locally - do NOT download at runtime
                logger.warning(
                    f"Model '{self.model_name}' not found locally. "
                    "Running in RULES-ONLY mode. "
                    "To enable hybrid detection, run: python scripts/download_models.py"
                )
                self.available = False
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            logger.warning("Falling back to RULES-ONLY mode.")
            self.available = False

    def encode(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to encode

        Returns:
            List of embedding vectors, or None if model not available
        """
        if not self.available or self.model is None:
            return None

        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return None

    def encode_single(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.

        Args:
            text: Text string to encode

        Returns:
            Embedding vector, or None if model not available
        """
        result = self.encode([text])
        if result:
            return result[0]
        return None

