"""Model loading utilities for local inference."""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ModelLoader:
    """Utility for loading and managing local models."""

    def __init__(self, models_dir: Optional[Path] = None):
        """
        Initialize model loader.

        Args:
            models_dir: Directory containing model files.
                       If None, uses default models/ directory.
        """
        if models_dir is None:
            models_dir = Path(__file__).parent.parent.parent / "models"
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.embedding_model = None
        self.classifier_model = None

    def is_model_available(self, model_name: str) -> bool:
        """
        Check if a model is available locally.

        Args:
            model_name: Name of the model to check

        Returns:
            True if model is available, False otherwise
        """
        # Check for common model file extensions
        model_paths = [
            self.models_dir / f"{model_name}.onnx",
            self.models_dir / f"{model_name}.bin",
            self.models_dir / model_name,
        ]
        return any(path.exists() for path in model_paths)

    def get_model_path(self, model_name: str) -> Optional[Path]:
        """
        Get path to a model if it exists.

        Args:
            model_name: Name of the model

        Returns:
            Path to model or None if not found
        """
        if self.is_model_available(model_name):
            # Return directory or file path
            for ext in ["", ".onnx", ".bin"]:
                path = self.models_dir / f"{model_name}{ext}"
                if path.exists():
                    return path
        return None

