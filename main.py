import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QMessageBox, QWidget, 
    QVBoxLayout, QHBoxLayout, QMenuBar, QMenu, QToolBar, QPushButton, 
    QLabel, QFileDialog, QSizePolicy, QToolButton, QFrame, QWidgetAction
)
from PyQt6.QtGui import QAction, QIcon, QPixmap, QPainter, QFont
from PyQt6.QtCore import Qt, QSize
from gui.tabs import ConvertTab, CompressTab, MergeTab, SplitTab, ExtractTab, ConvertToImageTab
from compressor import is_ghostscript_available

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        if hasattr(sys, '_MEIPASS'):
            # One-file mode: files are extracted to a temporary directory
            base_path = sys._MEIPASS
        else:
            # One-directory mode: files are in the same directory as the executable
            base_path = os.path.dirname(sys.executable)
    else:
        # Running as script
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

class PDFConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Utility App")
        self.resize(1000, 700)
        
        # Check for Ghostscript availability
        if not is_ghostscript_available():
            QMessageBox.warning(
                self,
                "Ghostscript Not Found",
                "Ghostscript is required for PDF compression features. Please ensure Ghostscript is installed on your system."
            )

        self._setup_menu()
        self._setup_toolbar()
        self._setup_central()

    def _setup_menu(self):
        menubar = QMenuBar(self)
        file_menu = QMenu("File", self)
        edit_menu = QMenu("Edit", self)
        help_menu = QMenu("Help", self)

        # Add File menu items
        add_file_action = QAction("Add File", self)
        add_file_action.setShortcut("Ctrl+O")
        add_file_action.triggered.connect(self._add_file)
        file_menu.addAction(add_file_action)

        file_menu.setStyleSheet("""
            QMenu::item {
                background: #b2e0f7;
                color: #000000;                
            }
            QMenu::item:selected {
                background: #a2d4ec;
                color: #000000;
            }
        """)

        add_folder_action = QAction("Add Folder", self)
        add_folder_action.setShortcut("Ctrl+Shift+O")
        add_folder_action.triggered.connect(self._add_folder)
        file_menu.addAction(add_folder_action)

        # Add Edit menu items
        delete_action = QAction("Delete", self)
        delete_action.setShortcut("Delete")
        delete_action.triggered.connect(self._delete_selected)
        edit_menu.addAction(delete_action)

        clear_all_action = QAction("Clear All", self)
        clear_all_action.setShortcut("Ctrl+Shift+D")
        clear_all_action.triggered.connect(self._clear_all)
        edit_menu.addAction(clear_all_action)

        edit_menu.setStyleSheet("""
            QMenu::item {
                background: #b2e0f7;
                color: #000000;               
            }
            QMenu::item:selected {
                background: #a2d4ec;
                color: #000000;
            }
        """)

        menubar.addMenu(file_menu)
        menubar.addMenu(edit_menu)
        menubar.addMenu(help_menu)
        self.setMenuBar(menubar)

    def _setup_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        def add_toolbar_button(icon_path, text, callback):
            btn = QToolButton()
            # Use the resource path function to get the correct icon path
            full_icon_path = get_resource_path(icon_path)
            btn.setIcon(QIcon(full_icon_path))
            btn.setText(text)
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            btn.clicked.connect(callback)
            btn.setStyleSheet("color: #000; font-size: 14px; padding: 2px 8px;")
            action = QWidgetAction(toolbar)
            action.setDefaultWidget(btn)
            toolbar.addAction(action)
            return btn

        def add_separator():
            line = QFrame()
            line.setFrameShape(QFrame.Shape.VLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            line.setStyleSheet("background: #a2d4ec; min-width: 2px; max-width: 2px;")
            sep_action = QWidgetAction(toolbar)
            sep_action.setDefaultWidget(line)
            toolbar.addAction(sep_action)

        self.add_file_btn = add_toolbar_button('gui/icons/file-plus.svg', 'Add File', self._add_file)
        add_separator()
        self.add_folder_btn = add_toolbar_button('gui/icons/folder-plus.svg', 'Add Folder', self._add_folder)
        add_separator()
        self.delete_btn = add_toolbar_button('gui/icons/trash-2.svg', 'Delete', self._delete_selected)
        add_separator()
        self.clear_btn = add_toolbar_button('gui/icons/x-circle.svg', 'Clear All', self._clear_all)
        add_separator()

    def _setup_central(self):
        central = QWidget()
        main_layout = QVBoxLayout(central)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #b2e0f7;
                background: #ffffff;
            }
            QTabBar::tab {
                background: #d6f0fa;
                color: #000;
                padding: 8px 16px;
                border: 1px solid #b2e0f7;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom: 1px solid #ffffff;
            }
            QTabBar::tab:hover {
                background: #b7d6fb;
            }
        """)

        # Create tabs
        self.convert_tab = ConvertTab()
        self.compress_tab = CompressTab()
        self.merge_tab = MergeTab()
        self.split_tab = SplitTab()
        self.extract_tab = ExtractTab()
        self.convert_to_image_tab = ConvertToImageTab()

        # Add tabs to widget with proper icon paths
        self.tab_widget.addTab(self.convert_tab, QIcon(get_resource_path('gui/icons/file-text.svg')), "Convert to DOCX")
        self.tab_widget.addTab(self.compress_tab, QIcon(get_resource_path('gui/icons/archive.svg')), "Compress PDF")
        self.tab_widget.addTab(self.merge_tab, QIcon(get_resource_path('gui/icons/layers.svg')), "Merge PDFs")
        self.tab_widget.addTab(self.split_tab, QIcon(get_resource_path('gui/icons/scissors.svg')), "Split PDF")
        self.tab_widget.addTab(self.extract_tab, QIcon(get_resource_path('gui/icons/file-text.svg')), "Extract Text")
        self.tab_widget.addTab(self.convert_to_image_tab, QIcon(get_resource_path('gui/icons/image.svg')), "Convert to Image")

        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self._update_start_button_text)
        
        # Set initial button text for the default selected tab (Convert to DOCX)
        self._update_start_button_text(0)

        # Connect start button click for each tab
        self.convert_tab.start_btn.clicked.connect(self._start_convert)
        self.compress_tab.start_btn.clicked.connect(self._start_compress)
        self.merge_tab.start_btn.clicked.connect(self._start_merge)
        self.split_tab.start_btn.clicked.connect(self._start_split)
        self.extract_tab.start_btn.clicked.connect(self._start_extract)
        self.convert_to_image_tab.start_btn.clicked.connect(self._start_convert_to_image)

        main_layout.addWidget(self.tab_widget)
        self.setCentralWidget(central)

        # Apply main window and central widget background
        self.setStyleSheet("""
            QMainWindow {
                background: #d6f0fa;
            }
            QWidget {
                background: #d6f0fa;
            }
        """)

        # Style menu bar and menu items
        self.menuBar().setStyleSheet("""
            QMenuBar {
                background: #b2e0f7;
                color: #000;
                font-size: 15px;
            }
            QMenuBar::item {
                background: transparent;
                color: #000;
            }
            QMenuBar::item:selected {
                background: #a2d4ec;
                color: #000;
            }
            QMenu {
                background: #b2e0f7;
                color: #000;
                font-size: 15px;
            }
            QMenu::item:selected {
                background: #a2d4ec;
                color: #000;
            }
        """)

    def _update_start_button_text(self, index):
        """Update the start button text based on the selected tab"""
        button_texts = {
            0: "Convert",  # Convert to DOCX
            1: "Compress", # Compress PDF
            2: "Merge",    # Merge PDFs
            3: "Split",    # Split PDF
            4: "Extract",  # Extract Text
            5: "Convert"   # Convert to Image
        }
        current_tab = self.tab_widget.widget(index)
        if current_tab:
            current_tab.start_btn.setText(button_texts.get(index, "Start"))

    def _add_file(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files", os.path.expanduser("~"), "PDF Files (*.pdf)")
        if files:
            current_tab = self.tab_widget.currentWidget()
            current_tab.add_files_to_table(files)

    def _add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", os.path.expanduser("~"))
        if folder:
            current_tab = self.tab_widget.currentWidget()
            pdf_files = []
            for entry in os.listdir(folder):
                if entry.lower().endswith('.pdf'):
                    file_path = os.path.join(folder, entry)
                    pdf_files.append(file_path)
            if pdf_files:
                current_tab.add_files_to_table(pdf_files)

    def _delete_selected(self):
        current_tab = self.tab_widget.currentWidget()
        current_tab.remove_selected_files()

    def _clear_all(self):
        current_tab = self.tab_widget.currentWidget()
        current_tab.clear_all_files()

    def _start_convert(self):
        """Handle convert button click"""
        self.convert_tab._start_conversion_process()

    def _start_compress(self):
        """Handle compress button click"""
        self.compress_tab._start_compression()

    def _start_merge(self):
        """Handle merge button click"""
        self.merge_tab._start_merge()

    def _start_split(self):
        """Handle split button click"""
        self.split_tab._start_split()

    def _start_extract(self):
        """Handle extract button click"""
        self.extract_tab._start_extract()

    def _start_convert_to_image(self):
        """Handle convert to image button click"""
        self.convert_to_image_tab._start_convert_to_image()

    def closeEvent(self, event):
        # Stop any active workers
        if hasattr(self.convert_tab, 'stop_active_conversion'):
            self.convert_tab.stop_active_conversion()
        if hasattr(self.compress_tab, 'worker') and self.compress_tab.worker and self.compress_tab.worker.isRunning():
            self.compress_tab.worker.stop()
        if hasattr(self.merge_tab, 'worker') and self.merge_tab.worker and self.merge_tab.worker.isRunning():
            self.merge_tab.worker.stop()
        if hasattr(self.split_tab, 'worker') and self.split_tab.worker and self.split_tab.worker.isRunning():
            self.split_tab.worker.stop()
        if hasattr(self.extract_tab, 'worker') and self.extract_tab.worker and self.extract_tab.worker.isRunning():
            self.extract_tab.worker.stop()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PDFConverterApp()
    window.show()
    sys.exit(app.exec()) 