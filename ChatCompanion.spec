# -*- mode: python ; coding: utf-8 -*-

# PyInstaller spec file for ChatCompanion
# This file defines how to bundle the application into a standalone executable
# 
# To build: pyinstaller ChatCompanion.spec
# 
# Note: This is a preparation structure. Full cross-platform installer is not yet complete.

import sys
from pathlib import Path

# Get project root (where this spec file is located)
# When running PyInstaller, SPECPATH is automatically set to the directory containing the spec file
# Note: SPECPATH is the directory, not the file path
if 'SPECPATH' in globals() and SPECPATH:
    project_root = Path(SPECPATH)
else:
    # Fallback: assume spec file is in project root
    project_root = Path(__file__).parent if '__file__' in globals() else Path.cwd()

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
        # Include models if they exist (optional)
        # Note: Models are large (~80MB), so they may be excluded for smaller executables
        # Uncomment the line below if you want to include models:
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
    icon=None,  # Add icon path here if you have one
)

