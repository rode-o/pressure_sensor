# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller one‑dir spec  (PyQt6 + Python 3.13)

▪ dist/PressureLogger/          – folder you ship
▪ PressureLogger.exe            – double‑click to run
▪ vcruntime140.dll + msvcp140.dll included
"""

import os, pathlib, ctypes.util
block_cipher = None
app_root = pathlib.Path(os.getcwd()).resolve()

# ───────────────────────── locate VC‑runtime DLLs ───────────────────
vc_dlls = []
for name in ("vcruntime140", "msvcp140"):
    path = ctypes.util.find_library(name)
    if path:
        vc_dlls.append((path, "."))        # (source → target‑dir)

# ───────────────────────── Analysis ─────────────────────────────────
a = Analysis(
    ["main.py"],
    pathex=[str(app_root)],
    binaries=vc_dlls,                      # ← add MSVC DLLs
    datas=[
        (str(app_root / "resources" / "salvus_logo_white.ico"), "resources"),
        (str(app_root / "resources" / "VERSION.txt"),           "resources"),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ───────────────────────── EXE ──────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    [],
    name="PressureLogger",
    icon=str(app_root / "resources" / "salvus_logo_white.ico"),
    version=str(app_root / "resources" / "VERSION.txt"),
    exclude_binaries=True,     # DLLs remain external (one‑dir)
    console=False,
    upx=True,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
)

# ───────────────────────── COLLECT ──────────────────────────────────
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="PressureLogger",
)
