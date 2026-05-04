# dl_mongoose.spec
# Run with: pyinstaller dl_mongoose.spec

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all yt-dlp data
yt_dlp_datas   = collect_data_files('yt_dlp')
ctk_datas      = collect_data_files('customtkinter')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=yt_dlp_datas + ctk_datas,
    hiddenimports=[
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.postprocessor',
        'customtkinter',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'pystray',
        'pystray._win32',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'threading',
        'queue',
        'socket',
        'json',
    ] + collect_submodules('yt_dlp'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DLMongoose',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/mongoose.ico',   # Put your icon here
    version='version_info.txt',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DLMongoose',
)
