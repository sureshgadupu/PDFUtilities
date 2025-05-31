import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget)
from gui.convert_tab import ConvertTab
from gui.compress_tab import CompressTab
from gui.merge_tab import MergeTab
from gui.split_tab import SplitTab
from gui.extract_text_tab import ExtractTextTab

class PDFConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Toolkit - Modularized")
        self.setMinimumSize(750, 550)

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