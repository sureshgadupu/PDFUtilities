import os
import platform
import shutil
import subprocess
import sys
import time


def install_pyinstaller():
    """Installs PyInstaller using pip."""
    print("Installing PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install PyInstaller: {e}")
        sys.exit(1)


def check_pyinstaller():
    """Checks if PyInstaller is installed."""
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller is not installed.")
        install_pyinstaller()


def create_dummy_icon():
    """Creates a valid dummy icon file to prevent build errors on Windows, overwriting if it exists."""
    icon_path = os.path.join("gui", "icons", "image.ico")
    print(f"Ensuring dummy icon file is valid at {icon_path}")
    os.makedirs(os.path.dirname(icon_path), exist_ok=True)
    try:
        from PIL import Image

        # Create a 16x16 transparent pixel icon, overwriting any existing file
        img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        img.save(icon_path, "ICO")
        print("Dummy .ico file created/updated successfully.")
    except ImportError:
        print("Pillow library not found. Cannot create a dummy icon.")
        print("The build will likely fail. Please install Pillow (`pip install Pillow`) or provide a valid 'image.ico' file.")
    except Exception as e:
        print(f"Failed to create dummy icon: {e}")


def cleanup_dist_folder():
    """Clean up the dist folder to avoid permission errors."""
    dist_path = "dist"
    if os.path.exists(dist_path):
        print(f"Cleaning up {dist_path} folder...")
        try:
            # Try to remove the entire dist folder
            shutil.rmtree(dist_path)
            print(f"Successfully removed {dist_path} folder.")
        except PermissionError:
            print(f"Warning: Could not remove {dist_path} folder. The executable might be running.")
            print("Please close any running instances of the application and try again.")
            return False
        except Exception as e:
            print(f"Warning: Error cleaning up {dist_path}: {e}")
            return False
    return True


def verify_ghostscript_inclusion():
    """Verify that Ghostscript files are included in the built executable."""
    print("\nVerifying Ghostscript inclusion in built executable...")

    dist_path = os.path.join("dist", "PDFUtilities")
    if not os.path.exists(dist_path):
        print(f"Warning: Dist folder not found at {dist_path}")
        return

    # Check for Ghostscript files in the dist folder
    gs_dir = os.path.join(dist_path, "bin", "Ghostscript", "Windows")
    if os.path.exists(gs_dir):
        print(f"+ Ghostscript directory found: {gs_dir}")
        files = os.listdir(gs_dir)
        print(f"  Files in directory: {files}")

        # Check specific files
        expected_files = ["gswin32.exe", "gswin32c.exe", "gswin64.exe", "gswin64c.exe"]
        for file in expected_files:
            file_path = os.path.join(gs_dir, file)
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"  + {file}: {size} bytes")
            else:
                print(f"  - {file}: MISSING")
    else:
        print(f"- Ghostscript directory NOT found: {gs_dir}")

        # Let's see what's actually in the dist folder
        print("Contents of dist folder:")
        try:
            for root, dirs, files in os.walk(dist_path):
                level = root.replace(dist_path, "").count(os.sep)
                indent = " " * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                subindent = " " * 2 * (level + 1)
                for file in files:
                    print(f"{subindent}{file}")
        except Exception as e:
            print(f"Error listing dist contents: {e}")


def build():
    """Builds the application using PyInstaller."""
    check_pyinstaller()

    system = platform.system()
    spec_file = "pdf_utility.spec"

    if not os.path.exists(spec_file):
        print(f"Error: {spec_file} not found!")
        sys.exit(1)

    if system == "Windows":
        print("Running build for Windows...")
        create_dummy_icon()
        # Clean up dist folder to avoid permission errors
        if not cleanup_dist_folder():
            print("Build aborted due to cleanup issues.")
            sys.exit(1)
    elif system == "Linux":
        print("Running build for Linux...")
        cleanup_dist_folder()
    else:
        print(f"Unsupported operating system: {system}")
        sys.exit(1)

    # Common build command with verbose output
    command = ["pyinstaller", spec_file, "--noconfirm", "--clean", "--log-level=INFO"]  # Add verbose logging

    print(f"Running command: {' '.join(command)}")

    try:
        # Run with real-time output
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1
        )

        # Print output in real-time
        for line in process.stdout:
            print(line.rstrip())

        process.wait()

        if process.returncode == 0:
            print("Build completed successfully.")
            print(f"You can find the executable in the 'dist' folder.")

            # Verify Ghostscript inclusion
            verify_ghostscript_inclusion()
        else:
            print(f"Build failed with return code: {process.returncode}")
            sys.exit(1)

    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        if system == "Windows":
            print("If you see permission errors, make sure:")
            print("1. The application is not currently running")
            print("2. No other process is using the executable")
            print("3. You have write permissions to the project directory")
        sys.exit(1)


if __name__ == "__main__":
    build()
