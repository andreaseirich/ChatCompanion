# Architecture Documentation

## Overview

ChatCompanion follows a modular, layered architecture with strict separation of concerns between UI, detection engine, rules, and models. The system is designed to run fully offline with no cloud dependencies.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         UI Layer                              │
│  (Streamlit - Input, Display, Interaction)                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Detection Engine                          │
│  (Orchestrates analysis, scoring, explanation generation)     │
└───────────────┬───────────────────────┬─────────────────────┘
                │                       │
                ▼                       ▼
┌──────────────────────────┐  ┌──────────────────────────────┐
│      Rules Engine         │  │      Model Inference         │
│  (Pattern matching,       │  │  (NLP embeddings,            │
│   heuristic detection)    │  │   risk classification)       │
└──────────────────────────┘  └──────────────────────────────┘
                │                       │
                └───────────┬───────────┘
                            ▼
                ┌──────────────────────┐
                │   Explainability     │
                │   (Risk scoring,     │
                │    evidence tracing) │
                └──────────────────────┘
```

## Component Responsibilities

### UI Layer (`app/ui/`)

- **components.py**: Reusable UI components (traffic light, explanations, advice)
- **input_handler.py**: Chat input processing and demo chat loading
- **main.py**: Streamlit application entry point

**Responsibilities:**
- Chat text input (manual or demo selection)
- Display traffic light indicator (green/yellow/red)
- Show child-friendly explanations
- Provide help advice and resources
- Handle user interactions ("This makes me uneasy" button)

**Privacy:** No data persistence - all data is ephemeral and cleared after session.

### Detection Engine (`app/detection/`)

- **engine.py**: Main orchestrator that coordinates rules and ML
- **aggregator.py**: Combines scores from multiple sources
- **explainer.py**: Generates child-friendly explanations

**Responsibilities:**
- Orchestrate the analysis pipeline
- Coordinate rules engine and model inference
- Aggregate risk scores from multiple sources
- Generate final risk level (green/yellow/red)
- Produce explainable evidence for each flag

**Key Feature:** Works in "rules-only" mode if ML models are unavailable.

### Rules Engine (`app/rules/`)

- **rule_engine.py**: Pattern matching logic
- **patterns.py**: Pattern data structures
- **rules_config.yaml**: YAML-based rule definitions

**Responsibilities:**
- Pattern-based detection using regex and keyword matching
- Heuristic rules for specific risk categories
- Configurable rule sets per risk type
- Returns structured matches with confidence scores

**Advantages:**
- Fully explainable (exact pattern matches)
- Fast and lightweight
- No dependencies on ML models
- Easy to update via YAML configuration

### Model Inference (`app/models_local/`)

- **loader.py**: Model loading utilities
- **embeddings.py**: Sentence embedding inference
- **classifier.py**: Risk classification using ML

**Responsibilities:**
- Load and run local NLP models (sentence-transformers)
- Generate sentence embeddings for semantic analysis
- Classify text for risk categories
- All processing happens in-memory, no external calls

**Fallback Behavior:**
- If models are unavailable, the system gracefully falls back to rules-only mode
- No errors are thrown - the detection engine adapts automatically

## Data Flow

1. **Input**: User pastes chat text or selects demo chat
2. **Preprocessing**: Text normalization, sentence segmentation (`app/utils/text_processing.py`)
3. **Parallel Analysis**:
   - Rules engine scans for patterns (`app/rules/rule_engine.py`)
   - Model inference generates embeddings and classifications (`app/models_local/`)
4. **Aggregation**: Detection engine combines results (`app/detection/aggregator.py`)
5. **Scoring**: Risk level calculated (weighted combination)
6. **Explanation**: Child-friendly text generated with evidence (`app/detection/explainer.py`)
7. **Display**: UI shows traffic light, explanation, and advice

## Technology Stack

### Backend Framework
- **Python 3.10+** with **Streamlit** for rapid UI development
- **FastAPI** structure for modular organization (though Streamlit is the entry point)

### NLP & Machine Learning
- **sentence-transformers**: Local sentence embeddings (`all-MiniLM-L6-v2` model, ~80MB)
- **scikit-learn**: Cosine similarity for semantic matching
- **ONNX Runtime**: Available for future model optimization (not currently used)

### Text Processing
- **spaCy**: Available for advanced text processing (currently using simple regex)
- **nltk**: Available if additional preprocessing needed

### Configuration
- **YAML**: Rule definitions (`app/rules/rules_config.yaml`)
- **pydantic**: Type validation (available for future use)

## Operating Modes

### Hybrid Mode (Default)

When ML models are available:
- Rules engine provides pattern-based detection (weight: 60%)
- ML classifier provides semantic similarity detection (weight: 40%)
- Scores are aggregated using weighted combination
- Provides best accuracy and coverage

### Rules-Only Mode (Fallback)

When ML models are unavailable or not yet integrated:
- System automatically falls back to rules-only detection
- All detection relies on pattern matching
- Still provides explainable results
- No errors or crashes - graceful degradation

**When Rules-Only Mode Activates:**
- ML models not downloaded during setup
- Model loading fails
- User explicitly disables ML features
- System runs in rules-only mode automatically

## Privacy & Security

### Offline Operation

- **Setup Phase**: Models may be downloaded once (requires internet)
- **Runtime**: Completely offline - no network calls
- **No Telemetry**: No tracking or analytics
- **No Persistence**: Chat text not saved by default

### Data Handling

- Chat text exists only in memory during analysis
- No database or file storage
- No background processes
- Explicit consent required for any future storage features

## Explainability

The system provides explainable results through:

1. **Pattern Matches**: Exact text snippets that triggered rules
2. **Category Scores**: Risk level for each category (bullying, manipulation, etc.)
3. **Evidence Extraction**: Specific phrases that caused flags
4. **Child-Friendly Explanations**: Simple language explaining what was detected

## Error Handling

- **Model Loading Failures**: Gracefully fall back to rules-only mode
- **Analysis Errors**: Caught and logged, user sees friendly error message
- **Missing Files**: Demo chats optional, rules config required
- **Invalid Input**: Text normalization handles edge cases

## Testing Strategy

- Unit tests for rules engine (`tests/test_rules.py`)
- Unit tests for detection engine (`tests/test_detection.py`)
- Unit tests for models (`tests/test_models.py`)
- Integration tests for full pipeline

## Future Enhancements

Potential improvements (out of scope for MVP):

- ONNX model optimization for faster inference
- Custom fine-tuned classifier models
- Additional risk categories
- Multi-language support
- Desktop app version (PyQt/Tkinter)

## Setup vs. Runtime

### Setup Phase (One-Time)

- Install Python dependencies (`pip install -r requirements.txt`)
- Download ML models (if using ML features):
  - Models are downloaded automatically on first use
  - Requires internet connection
  - Models stored in `models/` directory
- Configure rules (optional - defaults provided)

### Runtime Phase (Offline)

- Launch application: `streamlit run app/main.py`
- All processing happens locally
- No network calls
- No internet required
- Models loaded from local storage

## File Structure

```
app/
├── main.py                 # Streamlit entry point
├── ui/                     # UI components
├── detection/              # Detection engine
├── rules/                  # Rules engine
├── models_local/           # ML model inference
└── utils/                  # Utilities (text processing, constants)
```

## Dependencies

See `requirements.txt` for complete list. Key dependencies:

- `streamlit>=1.28.0`: UI framework
- `sentence-transformers>=2.2.2`: NLP embeddings
- `scikit-learn>=1.3.0`: ML utilities
- `pyyaml>=6.0.1`: Rule configuration

---

*This architecture supports the MVP goals while maintaining flexibility for future enhancements.*

