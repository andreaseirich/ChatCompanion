#!/usr/bin/env python3
"""
Setup script to download ML models for ChatCompanion.

This script downloads models ONCE during setup phase.
Runtime remains completely offline - no downloads during analysis.

Usage:
    python scripts/download_models.py

Models will be stored in: models/
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.models_local.loader import ModelLoader


def download_models():
    """Download required ML models for hybrid detection."""
    print("=" * 60)
    print("ChatCompanion - Model Download Script")
    print("=" * 60)
    print()
    print("This script downloads ML models for enhanced risk detection.")
    print("Models will be stored locally and used for offline inference.")
    print()
    
    loader = ModelLoader()
    models_dir = loader.models_dir
    
    print(f"Models directory: {models_dir}")
    print()
    
    # Check if models already exist
    model_name = "all-MiniLM-L6-v2"
    if loader.is_model_available(model_name):
        print(f"✓ Model '{model_name}' already exists.")
        print(f"  Location: {loader.get_model_path(model_name)}")
        print()
        response = input("Download again? (y/N): ").strip().lower()
        if response != 'y':
            print("Skipping download.")
            return
    
    print(f"Downloading model: {model_name}")
    print("This may take a few minutes (~80MB download)...")
    print()
    
    try:
        from sentence_transformers import SentenceTransformer
        
        # Download model - this will save to cache first, then we copy to models/
        print("Step 1: Downloading from HuggingFace...")
        model = SentenceTransformer(model_name)
        
        # Save to local models directory
        print(f"Step 2: Saving to {models_dir}...")
        model.save(str(models_dir / model_name))
        
        print()
        print("=" * 60)
        print("✓ Model download completed successfully!")
        print("=" * 60)
        print()
        print(f"Model saved to: {models_dir / model_name}")
        print()
        print("You can now run ChatCompanion with hybrid detection enabled.")
        print("Runtime will be completely offline - no network calls.")
        
    except ImportError:
        print("ERROR: sentence-transformers not installed.")
        print("Please install dependencies first:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to download model: {e}")
        print()
        print("The application will still work in rules-only mode.")
        sys.exit(1)


if __name__ == "__main__":
    download_models()

