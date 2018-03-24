# vim: set ft=python:

from PyInstaller.utils.hooks import collect_submodules

hidden_imports = collect_submodules('beancount',
                                    filter=lambda name: 'test' not in name)

data_files = [
    ('../fava/help', 'fava/help'),
    ('../fava/static/css', 'fava/static/css'),
    ('../fava/static/gen', 'fava/static/gen'),
    ('../fava/templates', 'fava/templates'),
    ('../fava/translations', 'fava/translations'),
]

a = Analysis(
    ['../fava/cli.py'],
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
