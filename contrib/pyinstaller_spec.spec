# vim: set ft=python:
"""Pyinstaller spec file for building a binary from fava's cli.py"""

from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import copy_metadata

# Data files and version info for Fava:
datas = collect_data_files("fava") + copy_metadata("fava")

# Add all Beancount code (for plugins) and the version file:
hiddenimports = collect_submodules("beancount")
datas += collect_data_files("beancount")

a = Analysis(
    ["../src/fava/cli.py"],
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
    name="fava",
    upx=True,
)
