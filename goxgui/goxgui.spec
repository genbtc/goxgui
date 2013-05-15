# -*- mode: python -*-
from distutils.sysconfig import get_python_lib
import os
a = Analysis(['application.py'],
            pathex=['..\\goxtool', os.path.join(get_python_lib(), 'Crypto\\Cipher')],
            hiddenimports=['AES','goxapi'],
            hookspath=None)
a.datas += [('bitcoin.png', '..\\goxgui\\bitcoin.png',  'DATA')]
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          a.dependencies,
          name='goxgui.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False)