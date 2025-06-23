#!/usr/bin/env python3
"""
macOS Build Script for PDF Utilities
Creates separate builds for Intel (x86_64) and Apple Silicon (arm64) architectures
"""

import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path


def check_macos():
    """Verify we're running on macOS."""
    if platform.system() != "Darwin":
        print("Error: This script is designed for macOS only.")
        sys.exit(1)
    
    print(f"macOS build detected: {platform.machine()}")


def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    try:
        # Install PyInstaller if not present
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
        # Install other requirements
        if os.path.exists("requirements.txt"):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        sys.exit(1)


def cleanup_build_folders():
    """Clean up build and dist folders."""
    folders = ["build", "dist", "__pycache__"]
    for folder in folders:
        if os.path.exists(folder):
            print(f"Cleaning up {folder}...")
            try:
                shutil.rmtree(folder)
            except Exception as e:
                print(f"Warning: Could not remove {folder}: {e}")


def create_dummy_icon():
    """Create a dummy icon file if needed."""
    icon_path = os.path.join("gui", "icons", "image.ico")
    if not os.path.exists(icon_path):
        print(f"Creating dummy icon at {icon_path}")
        os.makedirs(os.path.dirname(icon_path), exist_ok=True)
        try:
            from PIL import Image
            img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
            img.save(icon_path, "ICO")
            print("Dummy icon created successfully.")
        except ImportError:
            print("Warning: Pillow not available, icon creation skipped.")
        except Exception as e:
            print(f"Warning: Could not create icon: {e}")


def build_for_architecture(arch):
    """Build the application for a specific architecture."""
    print(f"\n{'='*50}")
    print(f"Building for {arch} architecture...")
    print(f"{'='*50}")
    
    # Set architecture-specific environment
    env = os.environ.copy()
    env["ARCHFLAGS"] = f"-arch {arch}"
    
    # Clean up before building
    cleanup_build_folders()
    
    # Create dummy icon
    create_dummy_icon()
    
    # Build command
    command = [
        "pyinstaller",
        "pdf_utility.spec",
        "--noconfirm",
        "--clean",
        "--log-level=INFO"
    ]
    
    print(f"Running: {' '.join(command)}")
    print(f"Architecture: {arch}")
    
    try:
        # Run the build
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            env=env
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line.rstrip())
        
        process.wait()
        
        if process.returncode == 0:
            print(f"✅ {arch} build completed successfully!")
            
            # Check what was created
            src_path = "dist/PDFUtilities"
            dst_path = f"dist/PDFUtilities-{arch}"
            
            if os.path.exists(src_path):
                print(f"Build output found: {src_path}")
                
                # Check if it's a file or directory
                if os.path.isfile(src_path):
                    print(f"⚠️  Build created single file: {src_path}")
                    print("This indicates the spec file is not creating directory structure correctly")
                elif os.path.isdir(src_path):
                    print(f"✅ Build created directory: {src_path}")
                
                # Move/rename the output
                if os.path.exists(dst_path):
                    if os.path.isfile(dst_path):
                        os.remove(dst_path)
                    else:
                        shutil.rmtree(dst_path)
                
                shutil.move(src_path, dst_path)
                print(f"Moved build to: {dst_path}")
                
                # Verify architecture (handle both file and directory cases)
                try:
                    if os.path.isfile(dst_path):
                        # Single file executable
                        executable_path = dst_path
                    else:
                        # Directory with executable inside
                        executable_path = f"{dst_path}/PDFUtilities"
                    
                    if os.path.exists(executable_path):
                        result = subprocess.run(
                            ["lipo", "-info", executable_path],
                            capture_output=True,
                            text=True,
                            check=True
                        )
                        print(f"Architecture info: {result.stdout.strip()}")
                    else:
                        print(f"Executable not found at: {executable_path}")
                except Exception as e:
                    print(f"Could not verify architecture: {e}")
            else:
                print(f"❌ No build output found at: {src_path}")
                return False
            
            return True
        else:
            print(f"❌ {arch} build failed with return code: {process.returncode}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ {arch} build failed: {e}")
        return False
    except Exception as e:
        print(f"❌ {arch} build failed with exception: {e}")
        return False


def create_universal_binary():
    """Create a universal binary from the separate architecture builds."""
    print(f"\n{'='*50}")
    print("Creating universal binary...")
    print(f"{'='*50}")
    
    x86_path = "dist/PDFUtilities-x86_64/PDFUtilities"
    arm_path = "dist/PDFUtilities-arm64/PDFUtilities"
    universal_path = "dist/PDFUtilities/PDFUtilities"
    
    # Check if both architectures exist
    if not os.path.exists(x86_path):
        print(f"❌ Intel build not found: {x86_path}")
        return False
    
    if not os.path.exists(arm_path):
        print(f"❌ Apple Silicon build not found: {arm_path}")
        return False
    
    # Create universal binary directory
    os.makedirs("dist/PDFUtilities", exist_ok=True)
    
    try:
        # Create universal binary using lipo
        command = [
            "lipo",
            "-create",
            x86_path,
            arm_path,
            "-output",
            universal_path
        ]
        
        print(f"Running: {' '.join(command)}")
        subprocess.run(command, check=True)
        
        # Verify universal binary
        result = subprocess.run(
            ["lipo", "-info", universal_path],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Universal binary info: {result.stdout.strip()}")
        
        print("✅ Universal binary created successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create universal binary: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to create universal binary with exception: {e}")
        return False


def main():
    """Main build function."""
    print("🚀 PDF Utilities macOS Build Script (Apple Silicon Only)")
    print("=" * 50)
    
    # Check we're on macOS
    check_macos()
    
    # Install dependencies
    install_dependencies()
    
    # Check if spec file exists
    if not os.path.exists("pdf_utility.spec"):
        print("❌ Error: pdf_utility.spec not found!")
        sys.exit(1)
    
    # Build only for Apple Silicon (arm64)
    arch = "arm64"
    print(f"Building only for Apple Silicon ({arch}) architecture...")
    
    try:
        if build_for_architecture(arch):
            print(f"\n🎉 Apple Silicon build completed successfully!")
            
            # Move the architecture-specific build to the expected location
            src_path = f"dist/PDFUtilities-{arch}"
            dst_path = "dist/PDFUtilities"
            
            if os.path.exists(src_path):
                print(f"Moving {src_path} to {dst_path}")
                
                # Check if source is file or directory
                if os.path.isfile(src_path):
                    print("⚠️  Source is a single file - this may cause workflow issues")
                    print("The workflow expects a directory structure")
                elif os.path.isdir(src_path):
                    print("✅ Source is a directory - correct for workflow")
                
                # Remove destination if it exists
                if os.path.exists(dst_path):
                    if os.path.isfile(dst_path):
                        os.remove(dst_path)
                    else:
                        shutil.rmtree(dst_path)
                
                # Move source to destination
                shutil.move(src_path, dst_path)
                print(f"Successfully moved build from {src_path} to {dst_path}")
                
                # Verify final structure
                if os.path.isdir(dst_path):
                    print(f"✅ Final build is directory: {dst_path}")
                    print("Contents:")
                    for item in os.listdir(dst_path):
                        item_path = os.path.join(dst_path, item)
                        if os.path.isfile(item_path):
                            size = os.path.getsize(item_path)
                            print(f"  📄 {item} ({size} bytes)")
                        else:
                            print(f"  📁 {item}/")
                else:
                    print(f"⚠️  Final build is single file: {dst_path}")
                
                print("\n📦 Build Summary:")
                if os.path.isdir(dst_path):
                    print("✅ Apple Silicon (arm64) build: dist/PDFUtilities/ (directory)")
                else:
                    print("⚠️  Apple Silicon (arm64) build: dist/PDFUtilities (single file)")
            else:
                print(f"❌ Build not found: {src_path}")
                sys.exit(1)
        else:
            print("❌ Apple Silicon build failed")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Exception during Apple Silicon build: {e}")
        sys.exit(1)
    
    print("\n🎯 Build completed!")
    print("Note: Users may need to allow the app in System Preferences > Security & Privacy")


if __name__ == "__main__":
    main()
