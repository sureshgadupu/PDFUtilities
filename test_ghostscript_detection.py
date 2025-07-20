#!/usr/bin/env python3
"""
Test script to verify Ghostscript detection after removing bundled executables.
"""

import os
import sys
import shutil
import subprocess

def test_ghostscript_detection():
    """Test Ghostscript detection functionality."""
    print("=== Testing Ghostscript Detection ===")
    print(f"OS: {os.name}")
    print(f"Platform: {sys.platform}")
    
    if os.name == "nt":
        print("\n--- Windows Detection ---")
        gs64 = shutil.which("gswin64c")
        gs32 = shutil.which("gswin32c")
        print(f"System gswin64c: {gs64}")
        print(f"System gswin32c: {gs32}")
        
        # Test if any Ghostscript is available
        gs_available = gs64 is not None or gs32 is not None
        print(f"Ghostscript available: {gs_available}")
        
        if gs_available:
            # Test if it can run
            gs_path = gs64 or gs32
            try:
                result = subprocess.run([gs_path, "--version"], 
                                     capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"Ghostscript version: {result.stdout.strip()}")
                    print("✅ Ghostscript is working correctly")
                else:
                    print("❌ Ghostscript test failed")
            except Exception as e:
                print(f"❌ Ghostscript test error: {e}")
        else:
            print("❌ No Ghostscript found in system PATH")
            print("Please install Ghostscript:")
            print("- Download from: https://ghostscript.com/releases/gsdnld.html")
            print("- Or install via: choco install ghostscript")
            print("- Or install via: scoop install ghostscript")
    else:
        print("\n--- Unix Detection ---")
        gs_path = shutil.which("gs")
        print(f"System gs: {gs_path}")
        
        if gs_path:
            try:
                result = subprocess.run([gs_path, "--version"], 
                                     capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"Ghostscript version: {result.stdout.strip()}")
                    print("✅ Ghostscript is working correctly")
                else:
                    print("❌ Ghostscript test failed")
            except Exception as e:
                print(f"❌ Ghostscript test error: {e}")
        else:
            print("❌ No Ghostscript found in system PATH")
            print("Please install Ghostscript using your package manager")

if __name__ == "__main__":
    test_ghostscript_detection() 