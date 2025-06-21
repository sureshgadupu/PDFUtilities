# PDF Utilities

A modern, all-in-one application for professional PDF processing: **Convert, Compress, Merge, Split, and Extract**. Built with PyQt6 for a stunning, responsive user interface with optimized startup and beautiful splash screen.

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

### Prerequisites

- Python 3.8 or higher
- Git (for cloning)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/sureshgadupu/PDFUtilities.git
   cd PDFUtilities
   ```

2. **Create and activate virtual environment:**

   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

## 📦 Build Standalone Executable

To create a standalone executable (Windows):

```bash
# Activate virtual environment
.\venv\Scripts\activate

# Build the application
python build_app.py
```

The executable will be created in the `dist` folder as `PDFUtilities.exe`.

## 🛠️ Dependencies

- **PyQt6**: Modern GUI framework
- **pdf2docx**: PDF to DOCX conversion
- **PyMuPDF**: PDF processing and manipulation
- **Pillow**: Image processing
- **Ghostscript**: Advanced PDF compression (bundled)

## 📋 Requirements

- Python 3.8+
- See `requirements.txt` for complete dependency list

## 🔧 Development

### Project Structure

```
PDFUtilities/
├── main.py              # Main application entry point
├── compressor.py        # PDF compression functionality
├── converter.py         # PDF conversion utilities
├── workers.py           # Background processing workers
├── gui/                 # User interface components
│   ├── tabs/           # Individual tab implementations
│   ├── icons/          # Application icons
│   └── ...
├── bin/                # Bundled binaries (Ghostscript)
└── build_app.py        # Build script for PyInstaller
```

### Key Features Implementation

- **Splash Screen**: Custom-drawn splash screen with progress updates
- **Background Initialization**: Heavy operations run in background threads
- **Ghostscript Integration**: Bundled Ghostscript for advanced compression
- **Modern UI**: Tabbed interface with consistent styling

## 📄 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

### What this means:

- ✅ You can use, modify, and distribute this software
- ✅ You can use it for commercial purposes
- ⚠️ You must provide the complete source code when distributing
- ⚠️ Any modifications must also be AGPL-licensed
- ⚠️ Network use requires source code access

**Note:** The AGPL-3.0 license is required due to the inclusion of Ghostscript (AGPL-licensed) for PDF compression features.

For more details, see the [LICENSE](LICENSE) file.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Made with ❤️ for the PDF processing community**
