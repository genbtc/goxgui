# -*- mode: python -*-
a = Analysis(['C:\\Users\\EOFL\\My Documents\\GitHub\\goxgui\\goxgui\\application.py'],
             pathex=['C:\\Users\\EOFL\\My Documents\\GitHub\\goxgui\\goxtool', 'C:\\Python27\\Lib\\site-packages\\Crypto\\Cipher\\'],
             )
a.datas += [('bitcoin.png', 'C:\\Users\\EOFL\\My Documents\\GitHub\\goxgui\\goxgui\\bitcoin.png',  'DATA')]
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