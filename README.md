# PDF Utilities

A comprehensive PDF processing application built with PyQt6, offering multiple PDF manipulation features in a modern, user-friendly interface.

## ✨ Features

- **🔄 Convert PDF to DOCX**: High-quality conversion using `pdf2docx`
- **📦 Compress PDF**: Advanced compression with Ghostscript integration
- **🔗 Merge PDFs**: Combine multiple PDFs into a single document
- **✂️ Split PDFs**: Extract specific pages or ranges into new files
- **📝 Extract Text**: Pull text content from PDFs for easy reuse
- **🖼️ Convert to Image**: Export PDF pages as images
- **🔐 Password Manager**: Store frequently used PDF passwords with descriptive names
- **⚡ Batch Processing**: Select and process multiple files at once
- **🎨 Modern UI**: Beautiful, accessible interface with splash screen
- **🚀 Fast Startup**: Optimized loading with background initialization
- **🔒 Privacy**: All processing done locally - no internet required
- **🖥️ Cross-platform**: Works on Windows and Linux

## 📋 Changelog

### Version 0.0.9 (Latest)

- **🔐 Added**: Password Manager feature - store frequently used PDF passwords with descriptive names
- **✨ Enhanced**: Password input fields now include save (💾), dropdown (▼), and visibility toggle (👁) buttons
- **⚙️ Added**: Full password management dialog with add, edit, remove, and clear all functions
- **📁 Storage**: Passwords saved locally in `~/.pdf_utilities/saved_passwords.json`
- **🎯 Improved**: Better UX for handling password-protected PDFs in batch operations
- **📖 Added**: Comprehensive PASSWORD_MANAGER_GUIDE.md documentation

### Version 0.0.8

- **🔧 Fixed**: Password removal functionality now intelligently detects encrypted PDFs
- **✨ Enhanced**: Non-encrypted PDFs no longer require password prompts
- **🧹 Cleaned**: Removed duplicate PasswordRemovalTab classes from codebase
- **📁 Added**: New password_remover.py module with improved PDF encryption detection
- **⚡ Improved**: Better user experience for password removal operations
- **🎯 Enhanced**: More accurate password validation logic

### Version 0.0.7

- **🔧 Fixed**: Import errors for worker classes (CompressionWorker, ConvertToImageWorker, ExtractTextWorker)
- **🧹 Cleaned**: Removed debug print statements and notifications
- **📁 Organized**: Consolidated all worker classes into workers.py for better maintainability
- **🐛 Fixed**: Indentation errors in CompressTab cleanup methods
- **⚡ Improved**: Error handling consistency across all worker classes
- **🎯 Enhanced**: Code organization and structure for better development experience

### Version 0.0.6

- **🐛 Fixed**: Notification system reliability issues
- **🔧 Improved**: Error message handling in Convert to DOCX tab
- **⚡ Enhanced**: Status message consistency across all tabs
- **🎯 Better UX**: More reliable error feedback when no files are selected

### Version 0.0.5

- **✨ Added**: Initial release with all core PDF processing features
- **🎨 Added**: Modern PyQt6-based user interface
- **🔄 Added**: PDF to DOCX conversion
- **📦 Added**: PDF compression with quality options
- **🔗 Added**: PDF merging functionality
- **✂️ Added**: PDF splitting with custom page ranges
- **📝 Added**: Text extraction from PDFs
- **🖼️ Added**: PDF to image conversion
- **🚀 Added**: Batch processing capabilities

## 🚀 Quick Start

### Download

- **Windows**: Download the latest release from [GitHub Releases](https://github.com/yourusername/PDFUtilities/releases)
- **Linux**: Download the Linux executable from releases
- **macOS**: Download the macOS executable (works on both Intel and Apple Silicon)
- **Source**: Clone the repository and follow development setup

### Run

```bash
# Windows
PDFUtilities.exe

# Linux
./PDFUtilities

# macOS
./PDFUtilities

# From source
python main.py
```

## 🖥️ Minimum Supported OS Versions

- **Windows:** Windows 10 or newer
- **Linux:** Ubuntu 22.04 or newer, Fedora 40 or newer, Arch Linux 2024.05.01 or newer
- **macOS:** macOS 12 (Monterey) or newer (both Intel and Apple Silicon)

## 🛠️ Development Setup

### Prerequisites

- Python 3.11+
- Git
- **Linux:** Ghostscript must be installed system-wide. See instructions below.
- **macOS:** Homebrew (for system dependencies)

#### Install Ghostscript

Ghostscript is required for PDF compression. Please install it using your system's package manager:

**Windows:**

- Download and install from the official website: https://ghostscript.com/releases/gsdnld.html
- Or install via Chocolatey: `choco install ghostscript`
- Or install via Scoop: `scoop install ghostscript`
- Make sure to add Ghostscript to your system PATH

**Linux:**

- **Ubuntu/Debian:**
  ```bash
  sudo apt update
  sudo apt install ghostscript
  ```
- **Fedora:**
  ```bash
  sudo dnf install ghostscript
  ```
- **Arch Linux:**
  ```bash
  sudo pacman -S ghostscript
  ```
- **openSUSE:**
  ```bash
  sudo zypper install ghostscript
  ```

**macOS:**

```bash
brew install ghostscript
```

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/PDFUtilities.git
cd PDFUtilities

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Build Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build the application
# Windows/Linux/macOS
python build_app.py
```

## 📁 Project Structure

```
PDFUtilities/
├── main.py                 # Main application entry point
├── build_app.py           # Build script for PyInstaller
├── pdf_utility.spec       # PyInstaller specification
├── requirements.txt       # Python dependencies
├── gui/                   # GUI components
│   ├── tabs/             # Individual tab implementations
│   ├── icons/            # Application icons
│   └── custom_widgets.py # Custom UI components
└── .github/              # GitHub Actions workflows
    └── workflows/        # CI/CD automation
```

## 🔄 CI/CD Pipeline

This project uses GitHub Actions for automated builds and releases:

### **Build Workflow** (`.github/workflows/build.yml`)

- **Triggers**: Push to `main`/`develop` branches, Pull Requests
- **Platforms**: Windows, Linux, and macOS
- **Actions**:
  - ✅ Install dependencies
  - ✅ Build executables with PyInstaller
  - ✅ Run basic tests
  - ✅ Upload build artifacts
  - ✅ Create release assets for main branch

### **Release Workflow** (`.github/workflows/release.yml`)

- **Triggers**: Push tags (e.g., `v1.0.0`)
- **Actions**:
  - ✅ Build Windows executable
  - ✅ Build Linux executable
  - ✅ Build macOS executable
  - ✅ Create GitHub release
  - ✅ Upload all platform executables and source code

### **Code Quality** (`.github/workflows/code-quality.yml`)

- **Triggers**: Push to `main`/`develop`, Pull Requests
- **Actions**:
  - ✅ Code formatting (Black)
  - ✅ Import sorting (isort)
  - ✅ Linting (flake8)
  - ✅ Security checks (bandit, safety)

### **How to Use**

1. **Push to main**: Automatically builds and tests
2. **Create PR**: Runs quality checks and builds
3. **Create release**: Tag with `v1.0.0` format
4. **Download**: Get executables from GitHub Actions artifacts or releases

## 📋 Dependencies

### Core Dependencies

- **PyQt6**: Modern GUI framework
- **PyMuPDF (fitz)**: PDF processing and manipulation
- **pdf2docx**: PDF to DOCX conversion
- **Pillow**: Image processing
- **Ghostscript**: PDF compression (**must be installed system-wide on all platforms**)

### Development Dependencies

- **PyInstaller**: Executable creation
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **bandit**: Security analysis

## 📄 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

### **License Requirements:**

✅ **Source Code**: Must provide complete source code  
✅ **Network Use**: Source access required for network interactions  
✅ **Derivative Works**: Modifications must also be AGPL-3.0  
⚠️ **Ghostscript**: System Ghostscript dependency is AGPL-3.0 licensed

### **Why AGPL-3.0?**

This license is required because the application includes Ghostscript binaries, which are licensed under AGPL-3.0. The copyleft provisions ensure that:

- Users have access to the complete source code
- Any modifications remain open source
- Network use triggers source code distribution requirements

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### **Development Guidelines**

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Ensure all CI checks pass

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/PDFUtilities/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/PDFUtilities/discussions)
- **Releases**: [GitHub Releases](https://github.com/yourusername/PDFUtilities/releases)

---

**Made with ❤️ using PyQt6 and modern Python practices**
