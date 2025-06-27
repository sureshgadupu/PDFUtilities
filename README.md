# PDF Utilities

A comprehensive PDF processing application built with PyQt6, offering multiple PDF manipulation features in a modern, user-friendly interface.

## ✨ Features

- **🔄 Convert PDF to DOCX**: High-quality conversion using `pdf2docx`
- **📦 Compress PDF**: Advanced compression with Ghostscript integration
- **🔗 Merge PDFs**: Combine multiple PDFs into a single document
- **✂️ Split PDFs**: Extract specific pages or ranges into new files
- **📝 Extract Text**: Pull text content from PDFs for easy reuse
- **🖼️ Convert to Image**: Export PDF pages as images
- **⚡ Batch Processing**: Select and process multiple files at once
- **🎨 Modern UI**: Beautiful, accessible interface with splash screen
- **🚀 Fast Startup**: Optimized loading with background initialization
- **🔒 Privacy**: All processing done locally - no internet required
- **🖥️ Cross-platform**: Works on Windows and Linux

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

#### Install Ghostscript on Linux

Ghostscript is required for PDF compression. Please install it using your distribution's package manager:

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
├── bin/                   # Binary dependencies
│   └── Ghostscript/      # Ghostscript binaries
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
- **Ghostscript**: PDF compression (**must be installed system-wide on Linux**)

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
⚠️ **Ghostscript**: Included Ghostscript is AGPL-3.0 licensed

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
