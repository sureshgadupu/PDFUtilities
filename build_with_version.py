#!/usr/bin/env python3
"""
Build script for PDF Utilities with dynamic version embedding.
This script extracts the version from the git tag and embeds it in the executable.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from version import create_version_file


def get_version_from_git():
    """Extract version from git tag"""
    try:
        # Get the current git tag
        result = subprocess.run(
            ['git', 'describe', '--tags', '--abbrev=0'],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        
        # Remove 'v' prefix if present
        if version.startswith('v'):
            version = version[1:]
        
        return version
    except subprocess.CalledProcessError:
        print("Warning: Could not get version from git tag")
        return None
    except FileNotFoundError:
        print("Warning: Git not found, cannot get version from tag")
        return None


def get_version_from_env():
    """Get version from environment variable (for CI/CD)"""
    return os.environ.get('VERSION') or os.environ.get('GITHUB_REF_NAME')


def get_version_from_pyproject():
    """Get version from pyproject.toml"""
    try:
        import toml
        pyproject_path = Path("pyproject.toml")
        if pyproject_path.exists():
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                data = toml.load(f)
                return data.get('project', {}).get('version')
    except Exception as e:
        print(f"Warning: Could not read version from pyproject.toml: {e}")
    return None


def main():
    parser = argparse.ArgumentParser(description='Build PDF Utilities with version embedding')
    parser.add_argument('--version', help='Override version (if not provided, will try to detect)')
    parser.add_argument('--pyinstaller-args', nargs='*', default=[], help='Additional PyInstaller arguments')
    args = parser.parse_args()

    # Determine version
    version = args.version
    if not version:
        version = get_version_from_env()
    if not version:
        version = get_version_from_git()
    if not version:
        version = get_version_from_pyproject()
    if not version:
        print("Error: Could not determine version. Please provide --version or ensure git tag/pyproject.toml is available.")
        sys.exit(1)

    print(f"Building PDF Utilities version: {version}")

    # Create version file
    if not create_version_file(version):
        print("Error: Failed to create version file")
        sys.exit(1)

    # Build with PyInstaller
    pyinstaller_cmd = [
        'pyinstaller',
        'pdf_utility.spec',
        '--clean',
        '--noconfirm'
    ] + args.pyinstaller_args

    print(f"Running: {' '.join(pyinstaller_cmd)}")
    
    try:
        result = subprocess.run(pyinstaller_cmd, check=True)
        print("Build completed successfully!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Build failed with exit code: {e.returncode}")
        return e.returncode


if __name__ == "__main__":
    sys.exit(main()) 