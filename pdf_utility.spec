# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files

# Set the application name
app_name = 'PDFUtilities'

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

# Collect binaries (executables) - ALWAYS include Ghostscript for Windows
binaries = []

# Add Ghostscript binaries for Windows
if sys.platform == "win32":
    # Windows Ghostscript executables - include all versions
    gs_files = [
        ('bin/Ghostscript/Windows/gswin32.exe', 'bin/Ghostscript/Windows'),
        ('bin/Ghostscript/Windows/gswin32c.exe', 'bin/Ghostscript/Windows'),
        ('bin/Ghostscript/Windows/gswin64.exe', 'bin/Ghostscript/Windows'),
        ('bin/Ghostscript/Windows/gswin64c.exe', 'bin/Ghostscript/Windows'),
    ]
    # Add all files that exist
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

# Platform-specific excludes
mac_excludes = []
if sys.platform == "darwin":
    print("[SPEC DEBUG] Applying macOS-specific module exclusions")
    mac_excludes = [
        "QtBluetooth", "QtNfc", "QtSensors", "QtSerialPort", "QtTest",
        "QtLocation", "QtQuick", "QtQml", "QtMultimedia", "QtConcurrent"
    ]

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
    excludes=mac_excludes,
    noarchive=False,
    optimize=0,
)

# Manually filter out problematic Qt frameworks on macOS AFTER analysis.
# This is the definitive fix for the recurring "FileExistsError" with Qt frameworks.
# We must filter both a.binaries AND a.datas to remove all traces of the framework.
if sys.platform == 'darwin':
    print('[SPEC DEBUG] Manually filtering unwanted Qt frameworks from ALL collected files.')
    
    frameworks_to_exclude = {
        'QtBluetooth', 'QtNfc', 'QtSensors', 'QtSerialPort', 'QtTest',
        'QtLocation', 'QtQuick', 'QtQml', 'QtMultimedia', 'QtConcurrent'
        # Note: QtNetwork is sometimes required for basic operations, so it's removed from this list.
        # If network functionality is truly not needed and causes issues, it can be added back.
    }
    
    def filter_qt_frameworks(collected_files, frameworks_to_exclude):
        """Filters out files that are part of the specified Qt frameworks."""
        filtered_list = []
        excluded_count = 0
        for item_tuple in collected_files:
            # The source path is the second element in the tuple (dest, source, type)
            source_path = item_tuple[1]
            if any(f'/{name}.framework/' in source_path for name in frameworks_to_exclude):
                excluded_count += 1
            else:
                filtered_list.append(item_tuple)
        return filtered_list, excluded_count

    # Filter both binaries and data files
    print('[SPEC DEBUG] Filtering a.binaries...')
    a.binaries, bin_excluded_count = filter_qt_frameworks(a.binaries, frameworks_to_exclude)
    print(f'[SPEC DEBUG]   ...removed {bin_excluded_count} binary files.')

    print('[SPEC DEBUG] Filtering a.datas...')
    a.datas, data_excluded_count = filter_qt_frameworks(a.datas, frameworks_to_exclude)
    print(f'[SPEC DEBUG]   ...removed {data_excluded_count} data files.')

pyz = PYZ(a.pure)

# Create EXE with platform-specific options
print(f"[SPEC DEBUG] Platform check: sys.platform = {sys.platform}")

if sys.platform == "win32":
    print("[SPEC DEBUG] Windows build - creating single file executable")
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
elif sys.platform == "darwin":
    print("[SPEC DEBUG] macOS build - creating directory structure with macOS-specific settings")
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=app_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,  # Disable UPX on macOS to avoid framework issues
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
    print("[SPEC DEBUG] Creating COLLECT for macOS with framework handling")
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=False,  # Disable UPX on macOS
        upx_exclude=[],
        name=app_name,
    )
else:
    print(f"[SPEC DEBUG] Linux build ({sys.platform}) - creating directory structure")
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=app_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
    print("[SPEC DEBUG] Creating COLLECT for Linux directory structure")
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name=app_name,
    ) 