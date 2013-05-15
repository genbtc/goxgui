# -*- mode: python -*-
from distutils.sysconfig import get_python_lib
a = Analysis(['goxgui\\application.py'],
             pathex=['goxtool\\', os.path.join(get_python_lib(), 'Crypto')])
a.datas += [('bitcoin.png', 'goxgui\\bitcoin.png',  'DATA')]
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          a.dependencies,
          name=os.path.join('dist', 'goxgui.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=False)