"""
Version management utility for PDF Utilities.
Handles version reading from multiple sources for both development and standalone builds.
"""

import os
import sys
from pathlib import Path


def get_version():
    """
    Get the current version from multiple sources in order of preference:
    1. Build-time embedded version (for standalone executables)
    2. pyproject.toml (for development)
    3. Fallback version
    """
    # Try to get version from build-time embedded file first
    version = _get_build_version()
    if version:
        return version
    
    # Try to get version from pyproject.toml (development mode)
    version = _get_pyproject_version()
    if version:
        return version
    
    # Fallback version
    return '0.0.0'


def _get_build_version():
    """Get version from build-time embedded version file"""
    try:
        # Look for version file in the same directory as the executable
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            if hasattr(sys, '_MEIPASS'):
                # One-file mode: files are extracted to a temporary directory
                base_path = sys._MEIPASS
            else:
                # One-directory mode: files are in the same directory as the executable
                base_path = os.path.dirname(sys.executable)
        else:
            # Running as script
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        version_file = os.path.join(base_path, 'version.txt')
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                version = f.read().strip()
                if version:
                    return version
    except Exception:
        pass
    
    return None


def _get_pyproject_version():
    """Get version from pyproject.toml (development mode)"""
    try:
        import toml
        # Get the directory containing main.py
        current_dir = Path(__file__).parent
        pyproject_path = current_dir / "pyproject.toml"
        
        if pyproject_path.exists():
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                data = toml.load(f)
                return data.get('project', {}).get('version', '0.0.0')
    except Exception:
        pass
    
    return None


def create_version_file(version, output_path='version.txt'):
    """
    Create a version file for embedding in the executable.
    This is called during the build process.
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(version)
        print(f"Version file created: {output_path} with version {version}")
        return True
    except Exception as e:
        print(f"Error creating version file: {e}")
        return False


if __name__ == "__main__":
    # When run directly, print the current version
    print(get_version()) 