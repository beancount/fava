# vim: set ft=python:
"""Pyinstaller spec file for building a binary from rustfava's cli.py"""

from __future__ import annotations

from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import copy_metadata

# Data files and version info for Rustfava:
datas = collect_data_files("rustfava") + copy_metadata("rustfava")

# Hidden imports for rustledger
hiddenimports = []

# Optionally add beancount for legacy plugin support
try:
    hiddenimports += collect_submodules("beancount")
    datas += collect_data_files("beancount")
except Exception:
    pass

a = Analysis(
    ["../src/rustfava/cli.py"],
    pathex=["."],
    datas=datas,
    hiddenimports=hiddenimports,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="rustfava",
    upx=True,
)
