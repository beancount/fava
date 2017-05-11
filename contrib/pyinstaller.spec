# -*- mode: python -*-
import os
import pkgutil

import beancount

hidden_imports = []
for _, name, __ in pkgutil.walk_packages(beancount.__path__, beancount.__name__ + '.'):
    if 'test' not in name:
        hidden_imports.append(name)

data_files = [
    ('../fava/docs', 'docs'),
    ('../fava/static/gen', 'static/gen'),
    ('../fava/templates', 'templates'),
]

a = Analysis(['../fava/cli.py'],
             pathex=['.'],
             binaries=None,
             datas=data_files,
             hiddenimports=hidden_imports,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=None)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=None)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='fava',
          debug=False,
          strip=False,
          upx=True,
          console=True )
