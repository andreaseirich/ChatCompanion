# Installation Guide

This guide explains how to install and run ChatCompanion. For non-technical parents, we're working toward a "one-click installer" in the future, but for now, installation requires basic Python knowledge.

## Important Note

**ChatCompanion is not a medical tool.** It is a privacy-first assistant designed to help children and teenagers recognize risky chat patterns. It does not replace professional help, counseling, or trusted adult guidance.

## Prerequisites

- **Python 3.10 or higher** (Python 3.11 or 3.12 recommended)
- **pip** (Python package manager, usually included with Python)
- **Internet connection** (only during initial setup for downloading dependencies and optional ML models)

## Installation Methods

### Method 1: Developer Installation (Recommended)

This is the standard installation method for developers and technically-inclined users.

#### Step 1: Clone the Repository

```bash
git clone https://github.com/andreaseirich/ChatCompanion.git
cd ChatCompanion
```

#### Step 2: Create a Virtual Environment (Recommended)

A virtual environment isolates ChatCompanion's dependencies from other Python projects.

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Download ML Models (Optional)

For enhanced detection accuracy, you can download ML models. This requires internet during setup only.

```bash
python scripts/download_models.py
```

**Note:** If you skip this step, ChatCompanion will run in "rules-only" mode, which still provides good detection but may be slightly less accurate.

#### Step 5: Run the Application

```bash
streamlit run app/main.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Method 2: Standalone Executable (Future)

We're working on a PyInstaller-based standalone executable that will allow non-technical parents to run ChatCompanion without installing Python. This is currently in preparation and not yet available.

**Status:** PyInstaller structure is prepared, but a full cross-platform installer is not yet complete.

## Troubleshooting

### Python Version Issues

**Problem:** `python` command not found or wrong version

**Solution:**
- Check your Python version: `python --version` or `python3 --version`
- Install Python 3.10+ from [python.org](https://www.python.org/downloads/)
- On macOS/Linux, you may need to use `python3` instead of `python`

### Virtual Environment Issues

**Problem:** `venv` module not found

**Solution:**
- Ensure you're using Python 3.10+
- Try: `python3 -m venv venv` instead of `python -m venv venv`

### Dependency Installation Issues

**Problem:** `pip install -r requirements.txt` fails

**Solution:**
- Update pip: `pip install --upgrade pip`
- Try installing dependencies one by one to identify the problematic package
- Check that you're using the correct Python version (3.10+)

### ML Model Download Issues

**Problem:** Models fail to download or are very slow

**Solution:**
- Models are optional - you can skip this step and use rules-only mode
- Ensure you have a stable internet connection
- Models are ~80MB and stored locally after download

### Streamlit Not Starting

**Problem:** `streamlit run app/main.py` fails

**Solution:**
- Ensure Streamlit is installed: `pip install streamlit`
- Check that you're in the correct directory (ChatCompanion root)
- Try: `python -m streamlit run app/main.py`

### Port Already in Use

**Problem:** Port 8501 is already in use

**Solution:**
- Streamlit will automatically try the next available port (8502, 8503, etc.)
- Or specify a different port: `streamlit run app/main.py --server.port 8502`

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

## Next Steps

After installation:

1. **Launch the application** (see Method 1, Step 5)
2. **Try a demo chat** from the sidebar to see how it works
3. **Read the README** for usage instructions
4. **Review ETHICS.md** to understand privacy and limitations

## Getting Help

- Check the [README.md](../README.md) for general information
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- See [ETHICS.md](ETHICS.md) for privacy and ethical considerations
- Check existing GitHub issues for known problems

## Future Improvements

We're working on:

- **One-click installer** for non-technical parents (PyInstaller executable)
- **Cross-platform support** (Windows, macOS, Linux)
- **Simplified installation** process
- **Automated dependency management**

These improvements will make ChatCompanion more accessible to non-technical users while maintaining our privacy-first, offline approach.

