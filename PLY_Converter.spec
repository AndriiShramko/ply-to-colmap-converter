# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for PLY to COLMAP Converter
Portable standalone executable for Windows 10/11
"""

import sys
from pathlib import Path

block_cipher = None

# Get current directory
current_dir = Path.cwd()

# Data files to include
# Note: Shramko_Andrii_ply_to_colmap_converter will be auto-detected via hiddenimports
datas = []

# Hidden imports - all modules that need to be included
hiddenimports = [
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
    'tkinter.ttk',
    'struct',
    'json',
    'shutil',
    'threading',
    'io',
    'contextlib',
    'webbrowser',
    'time',
    'pathlib',
    'datetime',
    'argparse',
    'Shramko_Andrii_ply_to_colmap_converter',
]

a = Analysis(
    ['gui_converter.py'],
    pathex=[str(current_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='PLY_to_COLMAP_Converter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Can add icon file here if needed
)

