# vim: set ft=python:

from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import copy_metadata

hidden_imports = collect_submodules('beancount',
                                    filter=lambda name: 'test' not in name)

data_files = [
    ('../src/fava/help', 'fava/help'),
    ('../src/fava/static', 'fava/static'),
    ('../src/fava/templates', 'fava/templates'),
    ('../src/fava/translations', 'fava/translations'),
]

# add fava version information:
data_files += copy_metadata('fava')

# add beancount version file:
import os
import importlib
beancount_dir = os.path.dirname(importlib.import_module('beancount').__file__)
beancount_version_file = os.path.join(beancount_dir, 'VERSION')
data_files += [(beancount_version_file, 'beancount')]

a = Analysis(
    ['../src/fava/cli.py'],
    pathex=['.'],
    binaries=None,
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name='cli',
    debug=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='fava',
)
