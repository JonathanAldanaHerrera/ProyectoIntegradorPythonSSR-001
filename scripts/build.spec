# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# SPECPATH es el directorio que contiene este archivo (scripts/).
# Su padre es la raíz del proyecto.
PROJECT_ROOT = str(Path(SPECPATH).parent)

a = Analysis(
    [str(Path(SPECPATH).parent / "logitrack" / "__main__.py")],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=[],
    hiddenimports=["logitrack"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib", "numpy", "pandas", "scipy", "PIL",
        "unittest", "xmlrpc", "pydoc", "doctest",
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="LogiTrack",
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
    name="LogiTrack",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="LogiTrack.app",
        icon=None,
        bundle_identifier="com.logitrack.desktop",
        info_plist={
            "CFBundleName": "LogiTrack",
            "CFBundleDisplayName": "LogiTrack Desktop",
            "CFBundleVersion": "1.0.0",
            "CFBundleShortVersionString": "1.0.0",
            "NSHighResolutionCapable": True,
        },
    )
