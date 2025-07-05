# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['PERSONAL_organizer.py'],  # Main script
    pathex=[],
    binaries=[],
    datas=[('icon_personal.png', 'app_icons')],  # Include the icon
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PersonalFileOrganizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    icon='icon_personal.png',  # App icon
    version='file_version_info.txt',  # Version information
)
