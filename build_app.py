import os
import platform
import shutil
import subprocess
import sys


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
        subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
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


def verify_ghostscript_availability():
    """Verify that Ghostscript is available on the system."""
    print("\nVerifying Ghostscript availability...")
    
    try:
        import shutil
        if os.name == "nt":
            gs_path = shutil.which("gswin64c") or shutil.which("gswin32c")
        else:
            gs_path = shutil.which("gs")
        
        if gs_path:
            print(f"+ Ghostscript found: {gs_path}")
            # Test if it can run
            try:
                import subprocess
                result = subprocess.run([gs_path, "--version"], 
                                     capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"  + Ghostscript version: {result.stdout.strip()}")
                else:
                    print(f"  - Ghostscript test failed")
            except Exception as e:
                print(f"  - Ghostscript test error: {e}")
        else:
            print("- Ghostscript not found in system PATH")
            print("  Please install Ghostscript:")
            if os.name == "nt":
                print("  - Download from: https://ghostscript.com/releases/gsdnld.html")
                print("  - Or install via: choco install ghostscript")
                print("  - Or install via: scoop install ghostscript")
            else:
                print("  - Linux: Use your package manager (apt, dnf, pacman, etc.)")
                print("  - macOS: brew install ghostscript")
    except Exception as e:
        print(f"Error checking Ghostscript: {e}")


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
    elif system == "Darwin":  # macOS
        print("Running build for macOS...")
        cleanup_dist_folder()
        # macOS-specific setup
        print("macOS build detected - ensuring proper permissions...")

        # Set environment variables to help with Qt framework issues
        os.environ["PYTHONPATH"] = os.getcwd() + ":" + os.environ.get("PYTHONPATH", "")

        # Clear any cached PyInstaller data that might cause issues
        cache_dirs = [
            os.path.expanduser("~/Library/Caches/pyinstaller"),
            os.path.join(os.getcwd(), "build"),
            os.path.join(os.getcwd(), "__pycache__"),
        ]
        for cache_dir in cache_dirs:
            if os.path.exists(cache_dir):
                try:
                    shutil.rmtree(cache_dir)
                    print(f"Cleared cache directory: {cache_dir}")
                except Exception as e:
                    print(f"Warning: Could not clear cache {cache_dir}: {e}")
    else:
        print(f"Unsupported operating system: {system}")
        sys.exit(1)

    # Build command with platform-specific options
    command = ["pyinstaller", spec_file, "--noconfirm", "--clean", "--log-level=INFO"]

    if system == "Darwin":
        print("macOS-specific build options are now handled in the spec file.")

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
            print("You can find the executable in the 'dist' folder.")

            # Platform-specific post-build steps
            if system == "Windows":
                # Verify Ghostscript availability
                verify_ghostscript_availability()
            elif system == "Darwin":  # macOS
                print("\nmacOS build completed successfully!")
                print("Note: The executable may require security permissions on first run.")
                print("Users may need to go to System Preferences > Security & Privacy to allow the app.")

                # Check if it's a universal binary
                try:
                    result = subprocess.run(
                        ["lipo", "-info", "dist/PDFUtilities/PDFUtilities"], capture_output=True, text=True, check=True
                    )
                    print(f"Binary architecture info: {result.stdout.strip()}")
                except subprocess.CalledProcessError:
                    print("Could not determine binary architecture info")
                except FileNotFoundError:
                    print("lipo command not available")
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
        elif system == "Darwin":
            print("macOS build failed. Common issues:")
            print("1. Missing system dependencies (try: brew install libpng jpeg zlib)")
            print("2. Python environment issues")
            print("3. PyInstaller configuration problems")
        sys.exit(1)


if __name__ == "__main__":
    build()
