# Copyright 2024 Eirich Andreas
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Build script for creating PyInstaller executable.

This script prepares the structure for building a standalone executable.
Note: This is a preparation script, not a full cross-platform installer yet.

Usage:
    python scripts/build_executable.py

Requirements:
    pip install pyinstaller
"""

import sys
from pathlib import Path

# Get project root
project_root = Path(__file__).parent.parent


def create_spec_file():
    """Create PyInstaller spec file with proper path resolution."""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

# PyInstaller spec file for ChatCompanion
# This file defines how to bundle the application into a standalone executable

import sys
from pathlib import Path

# Get project root (where this spec file is located)
project_root = Path(SPECPATH).parent

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Include rules configuration
        (str(project_root / 'app' / 'rules' / 'rules_config.yaml'), 'app/rules'),
        # Include demo data (optional, for testing)
        (str(project_root / 'demo_data'), 'demo_data'),
        # Include assets (logo, icons)
        (str(project_root / 'assets'), 'assets'),
        # Include models if they exist (optional)
        # Note: Models are large (~80MB), so they may be excluded for smaller executables
        # (str(project_root / 'models'), 'models'),
    ],
    hiddenimports=[
        'streamlit',
        'yaml',
        'sentence_transformers',
        'sklearn',
        'nltk',
        'app.detection.engine',
        'app.detection.aggregator',
        'app.detection.explainer',
        'app.rules.rule_engine',
        'app.rules.patterns',
        'app.models_local.classifier',
        'app.models_local.embeddings',
        'app.models_local.loader',
        'app.ui.components',
        'app.ui.text_presets',
        'app.ui.input_handler',
        'app.utils.constants',
        'app.utils.text_processing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ChatCompanion',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / 'assets' / 'logo.svg') if (project_root / 'assets' / 'logo.svg').exists() else None,  # Use SVG logo if available (PyInstaller supports SVG on some platforms)
)
"""
    
    spec_path = project_root / "ChatCompanion.spec"
    spec_content = spec_content.replace("SPECPATH", str(spec_path))
    
    with open(spec_path, "w") as f:
        f.write(spec_content)
    
    print(f"Created PyInstaller spec file: {spec_path}")
    print("\nTo build the executable, run:")
    print(f"  pyinstaller {spec_path}")
    print("\nNote: This will create a standalone executable in the 'dist' directory.")
    print("The executable will be large (~200-300MB) due to included dependencies.")


def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("PyInstaller is not installed.")
        print("Install it with: pip install pyinstaller")
        return False


if __name__ == "__main__":
    print("ChatCompanion PyInstaller Build Script")
    print("=" * 50)
    
    if not check_pyinstaller():
        sys.exit(1)
    
    create_spec_file()
    print("\nBuild script completed successfully!")

