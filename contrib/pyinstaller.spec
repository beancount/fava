# -*- mode: python -*-

block_cipher = None

import os
import livereload
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
             hiddenimports=[],
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
