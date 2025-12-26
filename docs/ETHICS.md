# Ethics Statement

## Core Principles

ChatCompanion is built on a foundation of ethical principles that prioritize the protection and dignity of children:

- **Protection and dignity of children**: The primary goal is to help children recognize potentially harmful situations, not to surveil or control them.
- **Honesty about limitations**: We are transparent about what the system can and cannot detect.
- **Transparency in data usage**: All processing happens locally with no data collection or cloud uploads.
- **No hidden monitoring**: The system is a tool for children to use voluntarily, not a surveillance mechanism.
- **Respectful, supportive language**: All explanations and advice use child-friendly, non-shaming language.

## Privacy & Data Handling

### Fully Offline Processing

- All chat analysis happens locally on the user's device
- No chat content is ever uploaded to cloud services
- No network calls are made during runtime analysis
- No telemetry or tracking is collected

### Data Storage

- **Default behavior**: Chat text is NOT saved automatically
- Chat content exists only in memory during analysis
- If storage is required in the future, explicit user consent will be required
- No background scanning or monitoring

### Model Downloads

- ML models may be downloaded once during initial setup
- After setup, the application runs completely offline
- Models are stored locally and never require network access during use

## Strong Prohibitions

ChatCompanion explicitly does NOT:

- Promise perfect detection (no system is 100% accurate)
- Make medical, psychological, or legal claims
- Generate sexual content
- Use manipulation, dark patterns, or fear-based pressure
- Automatically notify parents or authorities
- Replace professional help or counseling

## Limitations

### Detection Accuracy

- The system uses pattern matching and machine learning, which are not perfect
- **Slang and Irony Ambiguity**: Youth language often uses slang, abbreviations, and irony that can be ambiguous. The system attempts to normalize common patterns (e.g., "u" → "you", "rn" → "right now") but may misinterpret context or miss nuanced meaning. There is a risk of false positives (safe banter flagged as risky) or false negatives (risky content missed due to slang/obfuscation)
- **Tone Misinterpretation**: The system analyzes text patterns but cannot perfectly interpret tone, sarcasm, or cultural context. Friendly teasing may be flagged, or hostile content may be missed
- Some risky conversations may not be detected
- Some safe conversations may be flagged incorrectly
- The system is a tool to help awareness, not a definitive safety guarantee

### Scope

- Designed for text-based chat conversations
- Not designed for live monitoring or OS-level integration
- Not a replacement for parental supervision or professional help
- Not a therapy or legal tool

### Language and Context Limitations

- **Slang and irony are ambiguous**: The system includes slang normalization for common English youth/online abbreviations, but slang and irony can be context-dependent and may lead to false positives or negatives
- **Heuristic-based normalization**: Slang normalization is heuristic-based, not perfect—some slang may not be recognized, and some normalizations may not capture the full nuance
- **System stays careful and non-judgmental**: The system is designed to be supportive rather than decisive, recognizing that language interpretation requires human judgment
- **False positives possible**: Friendly banter with slang or irony may occasionally be flagged, or hostile slang may be missed—the tool is a helper, not a definitive judge

## User Responsibility

ChatCompanion is designed to:

- Help children recognize patterns in conversations
- Provide child-friendly explanations of concerning behaviors
- Encourage seeking help from trusted adults
- Support healthy boundary-setting

It is NOT designed to:

- Make decisions for children
- Replace judgment or intuition
- Guarantee safety
- Act as a substitute for adult guidance

## Ethical Framework

This project is guided by principles that emphasize:

- Protecting the weak and vulnerable
- Exposing manipulative behavior without shaming victims
- Emphasizing responsibility and truth
- Supporting children's autonomy while providing guidance

## Reporting Issues

If you encounter ethical concerns or have suggestions for improvement, please:

1. Review the limitations and design principles above
2. Consider whether the concern relates to misuse vs. design intent
3. Report issues through appropriate channels (GitHub issues, etc.)

## Continuous Improvement

We are committed to:

- Regular review of detection patterns for bias or over-detection
- Improving child-friendly language and explanations
- Maintaining transparency about capabilities and limitations
- Respecting user privacy and autonomy

---

*This ethics statement is aligned with the Master Prompt and project goals. It will be updated as the project evolves.*

