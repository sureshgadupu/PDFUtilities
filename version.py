"""
Version management utility for PDF Utilities.
Handles version reading from multiple sources for both development and standalone builds.
"""

import os
import sys
from pathlib import Path


def get_version():
    """Get the current version of the application"""
    try:
        # Try to read from pyproject.toml first (development mode)
        import toml
        try:
            with open("pyproject.toml", "r", encoding="utf-8") as f:
                data = toml.load(f)
                return data["tool"]["poetry"]["version"]
        except (FileNotFoundError, KeyError, toml.TomlDecodeError):
            pass

        # Try to read from version.txt (production mode)
        import sys
        import os

        # Determine the base path for the executable
        if getattr(sys, "frozen", False):
            # Running as compiled executable
            base_path = os.path.dirname(sys.executable)
            if hasattr(sys, "_MEIPASS"):
                # One-file mode
                base_path = sys._MEIPASS
            else:
                # One-directory mode
                base_path = os.path.dirname(sys.executable)
        else:
            # Running as script
            base_path = os.path.dirname(os.path.abspath(__file__))

        # Look for version.txt in the base path
        version_file = os.path.join(base_path, "version.txt")
        
        if os.path.exists(version_file):
            with open(version_file, "r", encoding="utf-8") as f:
                version = f.read().strip()
                if version:
                    return version

        # Fallback to hardcoded version
        return "0.0.6"

    except Exception as e:
        # Final fallback
        return "0.0.6"


def _get_build_version():
    """Get version from build-time embedded version file"""
    try:
        # Look for version file in the same directory as the executable
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            if hasattr(sys, '_MEIPASS'):
                # One-file mode: files are extracted to a temporary directory
                base_path = sys._MEIPASS
                print(f"[DEBUG] One-file mode, looking in: {base_path}")
            else:
                # One-directory mode: files are in the same directory as the executable
                base_path = os.path.dirname(sys.executable)
                print(f"[DEBUG] One-directory mode, looking in: {base_path}")
        else:
            # Running as script
            base_path = os.path.dirname(os.path.abspath(__file__))
            print(f"[DEBUG] Script mode, looking in: {base_path}")
        
        version_file = os.path.join(base_path, 'version.txt')
        print(f"[DEBUG] Looking for version file: {version_file}")
        
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                version = f.read().strip()
                if version:
                    print(f"[DEBUG] Found version in version.txt: {version}")
                    return version
                else:
                    print("[DEBUG] version.txt is empty")
        else:
            print(f"[DEBUG] version.txt not found at: {version_file}")
    except Exception as e:
        print(f"[DEBUG] Error reading version.txt: {e}")
    
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