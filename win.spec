# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['C:\\git\\analytics_assist\\analytics_assist.py'],
             pathex=['C:\\git\\analytics_assist', 'C:\\git\\analytics_assist'],
             binaries=[],
             datas=[('icon.png', '.')],
             hiddenimports=['pkg_resources.py2_warn'],
             hookspath=['c:\\git\\analytics_assist\\venv\\lib\\site-packages\\pyupdater\\hooks'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='win',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='win')
