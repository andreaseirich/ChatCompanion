# Contributing to ChatCompanion

Thank you for your interest in contributing to ChatCompanion! This document provides guidelines for contributing to the project.

## Code of Conduct

ChatCompanion is designed to help children and teenagers recognize risky chat patterns. All contributions should align with our ethical principles:

- **Privacy-first**: No telemetry, no tracking, no data collection
- **Child-centered**: All user-facing text must be age-appropriate (ages 10-16)
- **Honest limitations**: We don't promise perfect detection
- **Supportive tone**: Never shame, scare, or blame children

See [`docs/ETHICS.md`](docs/ETHICS.md) for our full ethics statement.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/andreaseirich/ChatCompanion.git
   cd ChatCompanion
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run tests**
   ```bash
   pytest tests/
   ```

## Code Style

- **Python**: Follow PEP 8 style guidelines
- **Type hints**: Use type hints for function parameters and return values
- **Docstrings**: Use Google-style docstrings for all public functions and classes
- **Line length**: Maximum 100 characters (soft limit)

## Testing

- **Write tests**: All new features should include tests
- **Test coverage**: Aim for >80% coverage for new code
- **Run tests**: Always run `pytest tests/` before committing
- **Test files**: Place tests in `tests/` directory, mirroring `app/` structure

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_detection.py
```

## Commit Messages

Use clear, descriptive commit messages:

- **Format**: `type: brief description`
- **Types**: `feat`, `fix`, `docs`, `test`, `refactor`, `style`
- **Examples**:
  - `feat: add context gating for time-phrase patterns`
  - `fix: prevent false positives in friendly banter detection`
  - `docs: update README with testing instructions`

## Pull Request Process

1. **Create a branch**: Use descriptive branch names (e.g., `feat/add-screenshots`)
2. **Write tests**: Include tests for new features
3. **Update documentation**: Update README, ARCHITECTURE, or other docs as needed
4. **Run tests**: Ensure all tests pass
5. **Submit PR**: Create a pull request with a clear description

## Areas for Contribution

### High Priority
- **False positive reduction**: Improve detection accuracy for friendly banter, sarcasm, slang
- **Multi-language support**: Extend beyond English
- **UI improvements**: Better visualizations, accessibility
- **Documentation**: Examples, tutorials, guides

### Medium Priority
- **Performance optimization**: Faster detection, lower memory usage
- **Additional risk categories**: New pattern types
- **Testing**: More test coverage, edge cases

### Low Priority
- **Packaging**: Standalone executables, installers
- **Integration**: Browser extensions, mobile apps

## Repository Hygiene

### Internal Files Must Be Excluded

**CRITICAL**: Internal development artifacts must NEVER be committed to the repository.

**Files that must be excluded**:
- Internal prompts (Master Prompt, Cursor prompts, debug prompts, evaluation prompts)
- Internal planning documents (checkpoints, benchmarks, quality gates)
- Private notes or scratch files
- Internal audit documents

**Rules**:
1. All internal prompts, notes, and planning documents must be excluded from commits
2. Use `.gitignore` to exclude internal directories and files
3. Before committing, run the repository hygiene checker:
   ```bash
   python3 scripts/repo_hygiene_check.py
   ```
4. If violations are found, exclude files before committing

**Repository Hygiene Checker**:
- Script: `scripts/repo_hygiene_check.py`
- Scans for disallowed patterns in filenames (prompt, debug_prompt, private, notes, scratch, local)
- Can be integrated into CI/CD pipelines
- Exit code 1 if violations found, 0 if clean

See [`docs/AUDIT.md`](docs/AUDIT.md) for complete repository scope definition.

## Important Notes

### What NOT to Include
- ❌ Internal development prompts or heuristics (must be excluded)
- ❌ Internal planning documents (checkpoints, benchmarks, quality gates)
- ❌ Hardcoded secrets or API keys
- ❌ Telemetry or tracking code
- ❌ Features that require internet connection (runtime must be offline)

### What to Include
- ✅ Tests for new features
- ✅ Documentation updates
- ✅ Clear commit messages
- ✅ Type hints and docstrings

## Questions?

- Review existing documentation: [`docs/`](docs/)
- Check existing issues on GitHub
- Follow ethical guidelines in [`docs/ETHICS.md`](docs/ETHICS.md)

---

**Thank you for contributing to ChatCompanion!** 🛡️

