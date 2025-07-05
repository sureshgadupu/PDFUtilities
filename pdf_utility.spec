# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# Get the current directory
current_dir = Path.cwd()

# Check if version.txt exists and include it
version_file = current_dir / "version.txt"
if version_file.exists():
    datas = [('version.txt', '.')]
else:
    datas = []

# Collect all icon files
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

# Add existing icon files to datas
for icon_file in icon_files:
    if os.path.exists(icon_file):
        datas.append((icon_file, os.path.dirname(icon_file)))

# Collect Ghostscript binaries
binaries = []
gs_dir = 'bin/Ghostscript/Windows'
if os.path.exists(gs_dir):
    gs_files = [
        'gswin32.exe',
        'gswin32c.exe', 
        'gswin64.exe',
        'gswin64c.exe'
    ]
    
    for gs_file in gs_files:
        gs_path = os.path.join(gs_dir, gs_file)
        if os.path.exists(gs_path):
            size = os.path.getsize(gs_path)
            binaries.append((gs_path, gs_dir))

# macOS-specific exclusions
excludes = []
if sys.platform == 'darwin':
    excludes = [
        'tkinter', '_tkinter', 'tk', 'tcl',
        'matplotlib', 'numpy.random._pickle',
        'PIL._tkinter_finder'
    ]

# Analysis
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        'PyQt6.QtSvg',
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'PyQt6.sip'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# macOS-specific filtering - only remove truly unwanted modules
if sys.platform == 'darwin':
    # Filter out only unwanted Qt frameworks and files (keep essential ones)
    unwanted_patterns = [
        'Qt3D', 'QtQuick3D', 'QtWebEngine', 'QtWebView', 'QtQml', 'QtQuick',
        'QtScxml', 'QtSensors', 'QtPositioning', 'QtLocation', 'QtMultimedia',
        'QtBluetooth', 'QtNfc', 'QtSerialPort', 'QtSerialBus', 'QtNetwork',
        'QtSql', 'QtTest', 'QtHelp', 'QtDesigner', 'QtUiTools', 'QtXml'
    ]
    
    # Filter binaries - keep essential Qt modules
    bin_excluded_count = 0
    for pattern in unwanted_patterns:
        a.binaries = [x for x in a.binaries if pattern not in x[0]]
        bin_excluded_count += 1
    
    # Filter datas - keep essential Qt modules  
    data_excluded_count = 0
    for pattern in unwanted_patterns:
        a.datas = [x for x in a.datas if pattern not in x[0]]
        data_excluded_count += 1

# Create symlinks for macOS (if needed)
if sys.platform == 'darwin':
    try:
        # Create symlinks for Qt frameworks if they don't exist
        qt_frameworks = ['QtCore', 'QtGui', 'QtWidgets']
        for framework in qt_frameworks:
            framework_path = f'/System/Library/Frameworks/{framework}.framework'
            if os.path.exists(framework_path):
                # Create symlink if needed
                pass
    except Exception as e:
        pass

# Create PYZ archive
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Platform-specific build configuration
if sys.platform == 'win32':
    # Windows build
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='PDFUtilities',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='gui/icons/image.ico'
    )
elif sys.platform == 'darwin':
    # macOS build
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='PDFUtilities',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='gui/icons/image.ico'
    )
else:
    # Linux build
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='PDFUtilities',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='gui/icons/image.ico'
    ) 