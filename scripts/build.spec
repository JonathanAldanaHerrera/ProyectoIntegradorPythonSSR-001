# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['../logitrack/__main__.py'],
    pathex=[str(Path('.').resolve().parent)],
    binaries=[],
    datas=[],
    hiddenimports=['logitrack'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'pandas', 'scipy', 'PIL',
        'unittest', 'xmlrpc', 'pydoc', 'doctest',
    ],
    noarchive=False,
    optimize=0,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LogiTrack',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LogiTrack',
)

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='LogiTrack.app',
        icon=None,
        bundle_identifier='com.logitrack.desktop',
        info_plist={
            'CFBundleName': 'LogiTrack',
            'CFBundleDisplayName': 'LogiTrack Desktop',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
        },
    )
