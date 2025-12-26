# Changelog

All notable changes to ChatCompanion will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Dates are in ISO format (YYYY-MM-DD) with Europe/Berlin timezone.

## [0.1.0] - 2024-01-XX

### Added

- Initial MVP release for Code Spring hackathon
- Core detection engine with rules-based pattern matching
- ML model integration with sentence-transformers (optional)
- Hybrid detection system (rules + ML)
- Rules-only fallback mode when ML models unavailable
- Streamlit-based user interface
- Traffic light risk indicator (green/yellow/red)
- Child-friendly explanation generation
- Help advice and resources section
- "This makes me uneasy" button
- Demo chat examples for testing
- YAML-based rule configuration system
- Support for 6 risk categories:
  - Bullying
  - Manipulation
  - Pressure
  - Secrecy demands
  - Guilt shifting
  - Grooming indicators
- Fully offline processing (no network calls at runtime)
- Privacy-first design (no data persistence by default)
- Comprehensive documentation:
  - README.md with setup and usage instructions
  - ARCHITECTURE.md with technical details
  - ETHICS.md with privacy and ethics statement
  - CHANGELOG.md (this file)
- Repository structure with modular components
- Text preprocessing utilities
- Score aggregation logic
- Explainability module with evidence extraction

### Technical Details

- Python 3.10+ support
- Streamlit 1.28.0+ for UI
- sentence-transformers 2.2.2+ for NLP embeddings
- scikit-learn 1.3.0+ for ML utilities
- YAML configuration for rules
- Modular architecture with separation of concerns

### Privacy & Ethics

- Fully offline operation after setup
- No telemetry or tracking
- No automatic data persistence
- Transparent about limitations
- Child-friendly, non-shaming language
- Clear ethics statement and privacy guarantees

## [Unreleased]

### Added

- Slang normalization layer for English youth/online slang and abbreviations
- Support for common abbreviations (e.g., "u" → "you", "lol" → "laughing", "jk" → "just kidding")
- Emoji tone detection (joking vs. annoyed markers)
- Enhanced friendly teasing heuristics that recognize slang joking markers
- Comprehensive slang handling tests
- Language Support section in README
- Updated architecture documentation with slang normalizer role
- Context gating for time-phrase patterns ("right now"/"now") to reduce false positives
- Sentence context helper for analyzing demand vs self-report contexts
- Pattern match counting improvements (instances vs patterns distinction)
- Post-test fixes for explanation accuracy and messaging clarity

### Changed

- Detection pipeline now includes slang normalization step before pattern matching
- Friendly teasing detection now uses normalized message with emoji tone markers
- Explanations continue to use raw text for user-facing output
- Enhanced slang normalization to handle masked slang, typos, and obfuscation
- Added cross-sentence coercion detection for split demands
- Improved pattern counting accuracy (instance-based counting verified)
- Extended English youth slang normalization (frfr, istg, ong, wtv, bc, cuz, k/kk)
- Enhanced tone markers (joking, friendly, annoyed, intense) with punctuation/caps detection
- Strengthened banter detection with mutuality + repair marker requirements and hard blockers
- Banter suppression only down-weights bullying, never weakens RED signals (coercive control)
- Fixed "right now" pressure false positives with context gating (self-reports excluded)
- Cleaned up GREEN messaging - removed "mild patterns" phrasing
- Calibrated YELLOW explanations - only mention threats when actually present
- Improved pattern match counting display (always shows instances and patterns)
- Guilt-shifting threshold adjusted to 0.18 (from 0.20) for better detection

### Technical Details

- New module: `app/detection/slang_normalizer.py`
- NormalizedMessage dataclass for tracking replacements and tone markers
- Slang normalization runs before rule-based pattern matching
- Hostile slang remains hostile (e.g., "stfu" → "shut up" still detected)

### Limitations

- Slang normalization is heuristic-based, not perfect
- Some slang or irony may be ambiguous and could lead to false positives/negatives
- System stays careful and non-judgmental in its approach

---

[0.1.0]: https://github.com/yourusername/ChatCompanion/releases/tag/v0.1.0

