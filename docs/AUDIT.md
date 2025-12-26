# Repository Audit

**Audit Date**: 2025-01-27  
**Purpose**: Ensure the GitHub repository contains ONLY what judges and recruiters need. Internal development artifacts (dev prompts, debugging prompts, personal notes, raw test chats, local fixtures not needed for reproducibility, private planning docs, etc.) must remain excluded and must NOT be committed.

---

## Repository Scope Definition

The repository should contain **ONLY**:

1. **Source Code**: All application code (`app/`, `tests/`)
2. **Public Documentation**: README, ARCHITECTURE, ETHICS, INSTALL, CHANGELOG, SECURITY, DEMO_SCRIPT
3. **Demo Data**: Synthetic example chats for reproducibility (`demo_data/`)
4. **Setup Files**: Requirements, setup scripts, run scripts
5. **Public Scripts**: Scripts needed for public use (`scripts/download_models.py`)
6. **License & Contributing**: LICENSE, CONTRIBUTING.md
7. **CI/CD Configuration**: GitHub Actions workflows (public)

**MUST NOT contain**:
- Internal prompts (Master Prompt, Cursor prompts, debug prompts, evaluation prompts)
- Internal planning documents (checkpoints, benchmarks, quality gates)
- Private notes or scratch files
- Build artifacts (dist/, build/, *.spec if local-only)
- Local development configurations
- Real chat logs or personal data

---

## Complete File Audit

| Path | Purpose | Needed for judges? | Needed for recruiters? | Should be public? | Action | Rationale |
|------|---------|-------------------|----------------------|------------------|--------|-----------|
| **Root Files** |
| `.gitignore` | Git ignore rules | Yes | Yes | Y | keep | Required for proper git behavior |
| `LICENSE` | Apache 2.0 license | Yes | Yes | Y | keep | Required for open source |
| `README.md` | Project overview and quickstart | Yes | Yes | Y | keep | Essential for judges and recruiters |
| `SECURITY.md` | Security policy | Yes | Yes | Y | keep | Shows security awareness |
| `CONTRIBUTING.md` | Contribution guidelines | Yes | Yes | Y | keep | Shows collaboration readiness |
| `requirements.txt` | Python dependencies | Yes | Yes | Y | keep | Required for setup |
| `run.sh` | Setup/run script | Yes | Yes | Y | keep | Helps with quickstart |
| `master_prompt.txt` | Internal Cursor AI master prompt | No | No | N | exclude | Internal development artifact |
| `ChatCompanion.spec` | PyInstaller build config | Maybe | Maybe | Optional | keep | Build config can be included for reproducibility |
| **Application Code** |
| `app/` (all files) | Application source code | Yes | Yes | Y | keep | Core application code |
| `tests/` (all files) | Test suite | Yes | Yes | Y | keep | Demonstrates quality and testing |
| **Documentation** |
| `docs/ARCHITECTURE.md` | Technical architecture | Yes | Yes | Y | keep | Essential technical documentation |
| `docs/ETHICS.md` | Ethics and privacy statement | Yes | Yes | Y | keep | Shows ethical considerations |
| `docs/INSTALL.md` | Installation instructions | Yes | Yes | Y | keep | Required for setup |
| `docs/CHANGELOG.md` | Version history | Yes | Yes | Y | keep | Shows project evolution |
| `docs/SECURITY.md` | Security policy (if separate) | Yes | Yes | Y | keep | Security documentation |
| `docs/DEMO_SCRIPT.md` | Demo video script | Yes | Maybe | Y | keep | Helps judges understand demo |
| `docs/DEVPOST_SUBMISSION.md` | Devpost submission content | Yes | Maybe | Y | keep | Submission content |
| `docs/CHECKPOINTS.md` | Internal project tracking | No | No | N | exclude | Internal planning document |
| `docs/QUALITY_GATES.md` | Internal quality checks | No | No | N | exclude | Internal development artifact |
| `docs/BENCHMARKS.md` | Internal benchmark analysis | No | No | N | exclude | Internal analysis document |
| `docs/DEVPOST_CHECKLIST.md` | Internal submission checklist | No | No | N | exclude | Internal planning document |
| `docs/REPO_AUDIT.md` | Previous audit document | No | No | N | exclude | Replaced by this document |
| **Demo Data** |
| `demo_data/` (all files) | Example chat conversations | Yes | Yes | Y | keep | Required for reproducibility and demo |
| **Scripts** |
| `scripts/download_models.py` | Model download script | Yes | Yes | Y | keep | Required for setup |
| `scripts/build_executable.py` | Build script | Maybe | Maybe | Y | keep | Can be public for reproducibility |
| **CI/CD** |
| `.github/workflows/` | GitHub Actions workflows | Yes | Yes | Y | keep | Shows CI/CD setup |
| **Models** |
| `models/.gitkeep` | Placeholder for models | Yes | Yes | Y | keep | Required for structure |
| `models/all-MiniLM-L6-v2/` | ML model files | No | No | N | gitignored | Large files, downloaded separately |

---

## Excluded Files

The following files are excluded from the repository:

1. `master_prompt.txt` - Internal development artifact
2. `docs/CHECKPOINTS.md` - Internal planning document
3. `docs/QUALITY_GATES.md` - Internal development artifact
4. `docs/BENCHMARKS.md` - Internal analysis document
5. `docs/DEVPOST_CHECKLIST.md` - Internal planning document
6. `docs/REPO_AUDIT.md` - Previous audit document (replaced by this document)

---

## Files Included in Repository (Justification)

### CodeSpring/Judge Requirements
- **Working Prototype**: `app/main.py`, `requirements.txt`, `run.sh` - Required for judges to run the app
- **Setup Instructions**: `README.md`, `docs/INSTALL.md` - Required for judges to set up
- **Demo Video Script**: `docs/DEMO_SCRIPT.md` - Helps judges understand the demo
- **Project Description**: `README.md` - Required for submission
- **Demo Data**: `demo_data/` - Required for reproducibility

### Recruiter Requirements
- **Code Quality**: `app/`, `tests/` - Shows technical skills
- **Documentation**: `docs/ARCHITECTURE.md`, `docs/ETHICS.md` - Shows communication and thoughtfulness
- **Security Awareness**: `SECURITY.md`, `.github/workflows/codeql-analysis.yml` - Shows security consciousness
- **Contributing Guidelines**: `CONTRIBUTING.md` - Shows collaboration readiness

### Optional Files
- `ChatCompanion.spec` - Build configuration, included for reproducibility
- `docs/DEVPOST_SUBMISSION.md` - Submission content
- `scripts/build_executable.py` - Build script

---

## Guardrails

To prevent future inclusion of internal artifacts:

1. **Repository Hygiene Checker**: `scripts/repo_hygiene_check.py` scans for disallowed patterns
2. **Gitignore Rules**: Build artifacts and excluded directories are gitignored
3. **Contributing Guidelines**: CONTRIBUTING.md includes rules about excluding internal files
4. **CI/CD Integration**: Hygiene checker can be integrated into GitHub Actions

---

## Verification Checklist

- [x] All internal prompts identified and excluded
- [x] All internal planning documents identified and excluded
- [x] `.gitignore` updated to exclude internal artifacts
- [x] Repository hygiene checker created
- [x] CONTRIBUTING.md updated with hygiene rules
- [x] All CodeSpring requirements still met
- [x] All tests pass
- [x] App starts successfully

---

**Last Updated**: 2025-01-27

