# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files

# Set the application name
app_name = 'PDFUtilityApp'

print(f"[SPEC DEBUG] Building for platform: {sys.platform}")

# Collect data files
datas = []
datas += collect_data_files('PyQt6')
datas += [('gui/icons', 'gui/icons')]

# Add all the specific icons that are referenced in the code
icon_files = [
    'gui/icons/file-plus.svg',
    'gui/icons/folder-plus.svg', 
    'gui/icons/trash-2.svg',
    'gui/icons/x-circle.svg',
    'gui/icons/file-text.svg',
    'gui/icons/archive.svg',
    'gui/icons/layers.svg',
    'gui/icons/scissors.svg',
    'gui/icons/image.svg'
]

# Add each icon file individually to ensure they're included
print("[SPEC DEBUG] Checking icon files:")
for icon_file in icon_files:
    if os.path.exists(icon_file):
        datas += [(icon_file, 'gui/icons')]
        print(f"[SPEC DEBUG]   + Including icon: {icon_file}")
    else:
        print(f"[SPEC DEBUG]   - Missing icon: {icon_file}")

# Collect binaries (executables)
binaries = []

# Add Ghostscript binaries based on platform
print("[SPEC DEBUG] Checking Ghostscript binaries:")
if sys.platform == "win32":
    # Windows Ghostscript executables - include all versions
    gs_files = [
        ('bin/Ghostscript/Windows/gswin32.exe', 'bin/Ghostscript/Windows'),
        ('bin/Ghostscript/Windows/gswin32c.exe', 'bin/Ghostscript/Windows'),
        ('bin/Ghostscript/Windows/gswin64.exe', 'bin/Ghostscript/Windows'),
        ('bin/Ghostscript/Windows/gswin64c.exe', 'bin/Ghostscript/Windows'),
    ]
    # Only add files that exist
    for gs_file, gs_dir in gs_files:
        if os.path.exists(gs_file):
            binaries += [(gs_file, gs_dir)]
            size = os.path.getsize(gs_file)
            print(f"[SPEC DEBUG]   + Including Ghostscript: {gs_file} ({size} bytes) -> {gs_dir}")
        else:
            print(f"[SPEC DEBUG]   - Missing Ghostscript: {gs_file}")
elif sys.platform.startswith("linux"):
    # Linux Ghostscript binary
    gs_file = 'bin/Ghostscript/Linux/gs'
    if os.path.exists(gs_file):
        binaries += [(gs_file, 'bin/Ghostscript/Linux')]
        size = os.path.getsize(gs_file)
        print(f"[SPEC DEBUG]   + Including Ghostscript: {gs_file} ({size} bytes)")
    else:
        print(f"[SPEC DEBUG]   - Missing Ghostscript: {gs_file}")

print(f"[SPEC DEBUG] Total binaries to include: {len(binaries)}")
print(f"[SPEC DEBUG] Total data files to include: {len(datas)}")

# Basic Analysis
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        'PyQt6.sip',
        'pdf2docx.main',
        'fitz.fitz',
        'PyQt6.QtSvg',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'compressor',
        'workers',
        'converter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

# Create EXE with platform-specific options
if sys.platform == "win32":
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name=app_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,  # Disable console for final build
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='gui/icons/image.ico'
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name=app_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,  # Disable console for final build
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    ) 