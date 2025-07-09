# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

block_cipher = None

# Get the project root directory
ROOT_DIR = Path(SPECPATH).resolve()

a = Analysis(
    ['main.py'],
    pathex=[str(ROOT_DIR)],
    binaries=[],
    datas=[
        # Include D3.js
        ('md2pptx/assets/d3.v7.min.js', 'md2pptx/assets'),
        # Include any default templates
        ('templates/*.pptx', 'templates'),
    ],
    hiddenimports=[
        'markdown_it',
        'markdown_it.common',
        'markdown_it.common.utils',
        'markdown_it.ruler',
        'markdown_it.token',
        'markdown_it.block_state',
        'markdown_it.state_core',
        'markdown_it.state_inline',
        'markdown_it.renderer',
        'markdown_it.rules_block',
        'markdown_it.rules_core',
        'markdown_it.rules_inline',
        'mdformat',
        'pyppeteer',
        'websockets',
        'cairosvg',
        'cairocffi',
        'PIL',
        'pandas',
        'customtkinter',
        'loguru',
        'pptx',
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
    name='md2pptx',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='md2pptx.ico' if os.path.exists('md2pptx.ico') else None,
)