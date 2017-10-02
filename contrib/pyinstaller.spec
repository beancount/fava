# vim: set ft=python:

from PyInstaller.utils.hooks import collect_submodules

hidden_imports = collect_submodules('beancount',
                                    filter=lambda name: 'test' not in name)

data_files = [
    ('../fava/docs', 'fava/docs'),
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
    a.binaries,
    a.zipfiles,
    a.datas,
    name='fava',
    debug=False,
    strip=False,
    upx=True,
    console=True,
)
