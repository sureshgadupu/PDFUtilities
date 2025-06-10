import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QMessageBox)
from gui.convert_tab import ConvertTab
from gui.compress_tab import CompressTab
from gui.merge_tab import MergeTab
from gui.split_tab import SplitTab
from gui.extract_text_tab import ExtractTextTab
from compressor import is_ghostscript_available
from setup_ghostscript import setup_ghostscript

class PDFConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Toolkit - Modularized")
        self.setMinimumSize(750, 550)

        # Check for Ghostscript and set up if needed
        if not is_ghostscript_available():
            reply = QMessageBox.question(
                self,
                "Ghostscript Setup",
                "Ghostscript is required for PDF compression. Would you like to download and set it up now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                if setup_ghostscript():
                    QMessageBox.information(
                        self,
                        "Success",
                        "Ghostscript has been set up successfully!"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Setup Failed",
                        "Failed to set up Ghostscript. PDF compression features may not work."
                    )

        # Create tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Convert to DOCX tab
        self.convert_tab_instance = ConvertTab(self)
        self.tabs.addTab(self.convert_tab_instance, "Convert to DOCX")

        # Add other tabs
        self.tabs.addTab(CompressTab(), "Compress PDF")
        self.tabs.addTab(MergeTab(), "Merge PDFs")
        self.tabs.addTab(SplitTab(), "Split PDF")
        self.tabs.addTab(ExtractTextTab(), "Extract Text")

    def closeEvent(self, event):
        if hasattr(self.convert_tab_instance, 'stop_active_conversion'):
            self.convert_tab_instance.stop_active_conversion()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PDFConverterApp()
    window.show()
    sys.exit(app.exec()) 