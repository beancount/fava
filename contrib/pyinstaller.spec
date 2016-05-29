# -*- mode: python -*-
import os
import pkgutil

import livereload
import beancount.ops
import beancount.plugins

hidden_import = []
for _, name, __ in pkgutil.iter_modules(beancount.plugins.__path__):
    if 'test' not in name:
        hidden_import.append('beancount.plugins.' + name)
for _, name, __ in pkgutil.iter_modules(beancount.ops.__path__):
    if 'test' not in name:
        hidden_import.append('beancount.ops.' + name)

block_cipher = None

livereload_js_path = os.path.join(os.path.dirname(livereload.__file__), 'vendors/livereload.js')

data_files = [
    ('../fava/default-settings.conf', '.'),
    ('../fava/docs', 'docs'),
    ('../fava/static/gen', 'static/gen'),
    ('../fava/templates', 'templates'),
    (livereload_js_path, 'livereload/vendors'),
]

a = Analysis(['../fava/cli.py'],
             pathex=['.'],
             binaries=None,
             datas=data_files,
             hiddenimports=hidden_import,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
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
