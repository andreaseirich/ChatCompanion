# Repository Audit

**Purpose**: This document provides transparency about what is included in this repository and why, ensuring it contains only what is needed for judges and recruiters to evaluate the project.

---

## Repository Contents

This repository contains:

1. **Source Code**: Application code (`app/`) and tests (`tests/`)
2. **Documentation**: README, ARCHITECTURE, ETHICS, INSTALL, CHANGELOG, SECURITY
3. **Demo Data**: Synthetic example chats for reproducibility (`demo_data/`)
4. **Setup Files**: Requirements, setup scripts, run scripts
5. **Scripts**: Model download and build scripts
6. **License**: LICENSE
7. **CI/CD**: GitHub Actions workflows

**Excluded**: Internal development artifacts (prompts, planning docs, private notes) are excluded via `.gitignore`.

---

## Key Files

| Category | Files | Purpose |
|----------|-------|---------|
| **Code** | `app/`, `tests/` | Application source code and test suite |
| **Documentation** | `README.md`, `docs/*.md` | Project documentation and guides |
| **Setup** | `requirements.txt` | Dependencies |
| **Demo Data** | `demo_data/` | Example chats for testing |
| **CI/CD** | `.github/workflows/` | Automated checks and workflows |

---

## Quality Assurance

This repository includes:
- **Automated Hygiene Checks**: GitHub Actions workflow scans for disallowed patterns
- **Comprehensive Tests**: Test suite covering core functionality
- **Security Scanning**: CodeQL analysis for security vulnerabilities
- **Documentation**: Complete setup and usage instructions

---

**Last Updated**: 2025-12-26

