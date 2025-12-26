# ChatCompanion 🛡️

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CodeQL](https://github.com/andreaseirich/ChatCompanion/workflows/CodeQL%20Analysis/badge.svg)](https://github.com/andreaseirich/ChatCompanion/actions/workflows/codeql-analysis.yml)
[![Privacy](https://img.shields.io/badge/Privacy-First%20Offline-green.svg)](docs/ETHICS.md)

**Privacy-first assistant to help children and teenagers recognize risky chat patterns**

ChatCompanion is a local, fully offline tool that helps identify concerning patterns in chat conversations such as bullying, manipulation, emotional pressure, secrecy demands, guilt-shifting, and grooming indicators. It explains situations in simple, child-friendly language and encourages healthy boundaries and seeking help—without surveillance and without uploading any chat data.

## Problem

Children and teenagers face increasing risks in online communication:
- **Bullying**: Mean comments, insults, and social exclusion
- **Manipulation**: Pressure to do things they don't want to do
- **Grooming**: Inappropriate behavior from adults or peers
- **Secrecy Demands**: Requests to keep conversations hidden from trusted adults
- **Guilt Shifting**: Being blamed for someone else's actions

Many existing solutions require cloud uploads, lack explainability, or are designed for surveillance rather than empowerment. ChatCompanion puts the child in control with a privacy-first, offline approach.

## Solution

ChatCompanion provides:
- **Local Processing**: All analysis happens on your device—nothing is uploaded
- **Explainable Detection**: Clear explanations of what patterns were detected and why
- **Child-Friendly Language**: Simple, supportive explanations that don't shame or scare
- **Traffic Light System**: Visual green/yellow/red indicators for quick understanding
- **Help Resources**: Guidance on talking to trusted adults and setting boundaries

## Features

### MVP Features

✅ **Chat Text Analysis**
- Paste any chat conversation for analysis
- Demo chat examples included for testing

✅ **Risk Detection**
- Bullying patterns
- Manipulation tactics
- Emotional pressure
- Secrecy demands
- Guilt shifting
- Grooming indicators

✅ **Traffic Light Indicator**
- 🟢 Green: Conversation looks safe
- 🟡 Yellow: Some concerning patterns detected
- 🔴 Red: High-risk situation—talk to a trusted adult

✅ **Child-Friendly Explanations**
- Simple language suitable for ages 10-16
- Clear, calm titles and messages for each risk level
- Evidence snippets showing what was flagged
- Supportive, non-shaming tone

✅ **Help & Advice**
- "This makes me uneasy" button for immediate support
- Guidance on talking to trusted adults
- Reminders about healthy boundaries

## Language Support

ChatCompanion is designed for **English** as the primary language.

### Slang Normalization

The system includes a slang normalization layer to handle common English youth/online slang and abbreviations. This helps ensure that:

- **Common abbreviations are understood**: "u" → "you", "ur" → "your", "idk" → "I don't know", "lol" → "laughing", "jk" → "just kidding"
- **Friendly teasing in youth style is not falsely flagged**: Mutual banter with slang and emojis is recognized as friendly
- **Hostile slang remains recognized**: Abbreviations like "stfu" → "shut up" are still detected as hostile

**Examples of normalized slang:**
- Pronouns: `u` → `you`, `ur` → `your`
- Common phrases: `idk` → `I don't know`, `brb` → `be right back`, `ttyl` → `talk to you later`
- Expressions: `lol`/`lmao` → `laughing`, `jk` → `just kidding`, `np` → `no problem`
- Hostile slang: `stfu` → `shut up` (preserves hostility)

**Important Notes:**
- Slang normalization is **heuristic-based, not perfect**
- **Context-Aware Detection**: Neutral scheduling words like "right now" alone do not trigger warnings—the system analyzes context to distinguish between self-reports ("I'm busy right now") and demands ("Answer right now")
- The tool is **supportive, not decisive**—it helps identify patterns but doesn't replace human judgment
- Some slang or irony may be ambiguous and could lead to false positives or negatives
- The system stays careful and non-judgmental in its approach

## Technology Stack

### Core Technologies
- **Python 3.10+**: Backend language
- **Streamlit**: Web-based UI framework
- **sentence-transformers**: Local NLP embeddings
- **scikit-learn**: Machine learning utilities
- **YAML**: Rule configuration

### Detection Approach
- **Hybrid Detection**: Combines rule-based pattern matching (60%) with ML semantic analysis (40%)
- **Rules-Only Fallback**: Works fully offline even if ML models aren't available
- **Explainable Results**: Every detection includes evidence and reasoning

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed technical documentation.

## Setup

For detailed installation instructions, see [INSTALL.md](docs/INSTALL.md).

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/andreaseirich/ChatCompanion.git
   cd ChatCompanion
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download ML models** (optional, for enhanced detection)
   ```bash
   python scripts/download_models.py
   ```

5. **Run the application**
   ```bash
   streamlit run app/main.py
   ```

The application will open in your default web browser at `http://localhost:8501`.

**Note:** For non-technical users, we're working on a standalone executable installer. See [INSTALL.md](docs/INSTALL.md) for details.

## Setup vs. Runtime

### Setup Phase (One-Time, Requires Internet)

- Installing Python dependencies
- Downloading ML models (optional, ~80MB)
- Models stored locally in `models/` directory

### Runtime Phase (Fully Offline)

- Launching the application
- Analyzing chat conversations
- All processing happens locally
- **No network calls** during analysis
- **No data uploads**
- **No telemetry**

The application is designed to run completely offline after initial setup. If ML models aren't available, the system automatically uses rules-only detection mode.

## Usage

1. **Launch the application** (see Setup above)

2. **Enter chat text**:
   - Paste a chat conversation in the text area, OR
   - Select a demo chat from the sidebar

3. **Click "Analyze Chat"**

4. **Review results**:
   - Check the traffic light indicator
   - Read the explanation
   - Review the advice section
   - Use "This makes me uneasy" button if needed

5. **Get help**:
   - Talk to a trusted adult
   - Use the help resources in the app

## Privacy & Data Handling

### Privacy Guarantees

- ✅ **Fully Offline**: No cloud uploads, no network calls during analysis
- ✅ **No Persistence**: Chat text is NOT saved by default
- ✅ **No Telemetry**: No tracking or analytics
- ✅ **Memory-Only**: Data exists only during analysis session
- ✅ **Explicit Consent**: Any future storage features will require opt-in

### Data Flow

1. User pastes chat text → stored in memory
2. Text analyzed locally → no network calls
3. Results displayed → data remains in memory
4. Session ends → data cleared

See [ETHICS.md](docs/ETHICS.md) for detailed privacy and ethics information.

## Limitations

### Detection Accuracy

- The system is not 100% accurate
- Some risky conversations may not be detected
- Some safe conversations may be flagged incorrectly
- The system is a **tool to help awareness**, not a definitive safety guarantee

### Scope

- Designed for text-based chat conversations
- Not designed for live monitoring or OS-level integration
- Not a replacement for parental supervision or professional help
- Not a therapy or legal tool

### What ChatCompanion Does NOT Do

- ❌ Promise perfect detection
- ❌ Make medical, psychological, or legal claims
- ❌ Automatically notify parents or authorities
- ❌ Replace professional help or counseling
- ❌ Monitor conversations automatically
- ❌ Store chat data without explicit consent

## Awards Alignment

This project is designed for the "Code Spring – Where Ideas Bloom into Innovation" hackathon and aligns with multiple award categories:

### Champion Award
- **Innovation**: Privacy-first offline approach with explainable AI
- **Technical Depth**: Hybrid detection system with graceful fallback
- **Real-World Impact**: Addresses critical child safety issue

### Innovators Award
- **Originality**: Unique combination of explainability and privacy
- **Design Principles**: Ethical, child-centered design
- **Elegant Concept**: Simple interface, powerful detection

### Builders Award
- **Complete MVP**: Fully functional prototype
- **Structured Engineering**: Modular architecture, clean code
- **Documentation**: Comprehensive docs and clear setup

### Jury Excellence Award
- **Clarity**: Clear problem statement and solution
- **Presentation Quality**: Professional documentation and demo
- **Original Approach**: Offline-first, explainable detection

### Rising Coder Award
- **Beginner-Friendly**: Clear code structure, good documentation
- **Learning Outcomes**: Demonstrates NLP, ML, and ethical design
- **Simple Installation**: Straightforward setup process

## Project Structure

```
ChatCompanion/
├── app/
│   ├── main.py              # Streamlit entry point
│   ├── ui/                  # UI components
│   ├── detection/           # Detection engine
│   ├── rules/               # Rules engine
│   ├── models_local/        # ML model inference
│   └── utils/               # Utilities
├── demo_data/               # Demo chat examples
├── docs/                    # Documentation
├── tests/                   # Unit tests
├── models/                  # Local model storage (gitignored)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Technical architecture and design
- **[ETHICS.md](docs/ETHICS.md)**: Ethics statement and privacy principles
- **[CHANGELOG.md](docs/CHANGELOG.md)**: Version history and changes

## Contributing

This is a hackathon project. For questions or suggestions:
- Review the documentation
- Check existing issues
- Follow ethical guidelines in ETHICS.md

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built for the "Code Spring – Where Ideas Bloom into Innovation" hackathon.

Special thanks to:
- The open-source community for excellent tools (sentence-transformers, Streamlit, etc.)
- Ethical AI researchers who prioritize explainability and privacy

## Contact

[To be added]

---

**Remember**: ChatCompanion is a tool to help awareness and encourage seeking help. It is not a replacement for talking to trusted adults or professional support. Always trust your instincts and seek help when something feels wrong.

