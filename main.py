import os
import sys

from PyQt6.QtCore import QSize, Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QSplashScreen,
    QTabWidget,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)

from compressor import is_ghostscript_available
from gui.tabs import (
    CompressTab,
    ConvertTab,
    ConvertToImageTab,
    ExtractTab,
    MergeTab,
    SplitTab,
)


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if getattr(sys, "frozen", False):
        # Running as compiled executable
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        if hasattr(sys, "_MEIPASS"):
            # One-file mode: files are extracted to a temporary directory
            base_path = sys._MEIPASS
        else:
            # One-directory mode: files are in the same directory as the executable
            base_path = os.path.dirname(sys.executable)
    else:
        # Running as script
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


class InitializationThread(QThread):
    """Thread for handling heavy initialization tasks"""

    progress_updated = pyqtSignal(str)
    initialization_complete = pyqtSignal()

    def run(self):
        """Run initialization tasks"""
        # Simulate initialization steps with feature-focused messages
        self.progress_updated.emit("Loading PDF conversion engine...")
        self.msleep(200)

        self.progress_updated.emit("Initializing compression tools...")
        self.msleep(300)

        self.progress_updated.emit("Setting up merge & split functionality...")
        self.msleep(250)

        self.progress_updated.emit("Preparing text extraction tools...")
        self.msleep(200)

        self.progress_updated.emit("Ready to process your PDFs!")
        self.msleep(100)

        self.initialization_complete.emit()


class PDFConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Utility App")
        self.resize(1000, 700)

        # Initialize components
        self.tabs_initialized = False
        self._initialize_ui_components()

        # Check for Ghostscript availability (non-blocking)
        QTimer.singleShot(100, self._check_ghostscript)

    def _initialize_ui_components(self):
        """Initialize UI components that don't require heavy processing"""
        self._setup_menu()
        self._setup_toolbar()
        self._setup_central_skeleton()

    def _setup_central_skeleton(self):
        """Setup the basic central widget structure without heavy tab initialization"""
        central = QWidget()
        main_layout = QVBoxLayout(central)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setStyleSheet(
            """
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
        """
        )

        # Add placeholder tabs
        self._add_placeholder_tabs()

        main_layout.addWidget(self.tab_widget)
        self.setCentralWidget(central)

        # Apply main window and central widget background
        self.setStyleSheet(
            """
            QMainWindow {
                background: #d6f0fa;
            }
            QWidget {
                background: #d6f0fa;
            }
        """
        )

        # Style menu bar and menu items
        self.menuBar().setStyleSheet(
            """
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
        """
        )

    def _add_placeholder_tabs(self):
        """Add placeholder tabs that will be replaced with real tabs"""
        placeholder_tabs = [
            ("Convert to DOCX", "gui/icons/file-text.svg"),
            ("Compress PDF", "gui/icons/archive.svg"),
            ("Merge PDFs", "gui/icons/layers.svg"),
            ("Split PDF", "gui/icons/scissors.svg"),
            ("Extract Text", "gui/icons/file-text.svg"),
            ("Convert to Image", "gui/icons/image.svg"),
        ]

        for title, icon_path in placeholder_tabs:
            placeholder = QWidget()
            placeholder_layout = QVBoxLayout(placeholder)

            # Add loading label
            loading_label = QLabel("Loading...")
            loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            loading_label.setStyleSheet("font-size: 16px; color: #666; padding: 50px;")
            placeholder_layout.addWidget(loading_label)

            self.tab_widget.addTab(placeholder, QIcon(get_resource_path(icon_path)), title)

    def _initialize_real_tabs(self):
        """Initialize the real tabs with all functionality"""
        if self.tabs_initialized:
            return

        # Create real tabs
        self.convert_tab = ConvertTab()
        self.compress_tab = CompressTab()
        self.merge_tab = MergeTab()
        self.split_tab = SplitTab()
        self.extract_tab = ExtractTab()
        self.convert_to_image_tab = ConvertToImageTab()

        # Replace placeholder tabs with real tabs
        self.tab_widget.removeTab(0)  # Remove Convert to DOCX placeholder
        self.tab_widget.insertTab(0, self.convert_tab, QIcon(get_resource_path("gui/icons/file-text.svg")), "Convert to DOCX")

        self.tab_widget.removeTab(1)  # Remove Compress PDF placeholder
        self.tab_widget.insertTab(1, self.compress_tab, QIcon(get_resource_path("gui/icons/archive.svg")), "Compress PDF")

        self.tab_widget.removeTab(2)  # Remove Merge PDFs placeholder
        self.tab_widget.insertTab(2, self.merge_tab, QIcon(get_resource_path("gui/icons/layers.svg")), "Merge PDFs")

        self.tab_widget.removeTab(3)  # Remove Split PDF placeholder
        self.tab_widget.insertTab(3, self.split_tab, QIcon(get_resource_path("gui/icons/scissors.svg")), "Split PDF")

        self.tab_widget.removeTab(4)  # Remove Extract Text placeholder
        self.tab_widget.insertTab(4, self.extract_tab, QIcon(get_resource_path("gui/icons/file-text.svg")), "Extract Text")

        self.tab_widget.removeTab(5)  # Remove Convert to Image placeholder
        self.tab_widget.insertTab(
            5, self.convert_to_image_tab, QIcon(get_resource_path("gui/icons/image.svg")), "Convert to Image"
        )

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

        self.tabs_initialized = True

        # Set the first tab (Convert to DOCX) as the default active tab
        self.tab_widget.setCurrentIndex(0)

    def _check_ghostscript(self):
        """Check for Ghostscript availability (non-blocking)"""
        if not is_ghostscript_available():
            QMessageBox.warning(
                self,
                "Ghostscript Not Found",
                "Ghostscript is required for PDF compression features. Please ensure Ghostscript is installed on your system.",
            )

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

        file_menu.setStyleSheet(
            """
            QMenu::item {
                background: #b2e0f7;
                color: #000000;
            }
            QMenu::item:selected {
                background: #a2d4ec;
                color: #000000;
            }
        """
        )

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

        edit_menu.setStyleSheet(
            """
            QMenu::item {
                background: #b2e0f7;
                color: #000000;
            }
            QMenu::item:selected {
                background: #a2d4ec;
                color: #000000;
            }
        """
        )

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

        self.add_file_btn = add_toolbar_button("gui/icons/file-plus.svg", "Add File", self._add_file)
        add_separator()
        self.add_folder_btn = add_toolbar_button("gui/icons/folder-plus.svg", "Add Folder", self._add_folder)
        add_separator()
        self.delete_btn = add_toolbar_button("gui/icons/trash-2.svg", "Delete", self._delete_selected)
        add_separator()
        self.clear_btn = add_toolbar_button("gui/icons/x-circle.svg", "Clear All", self._clear_all)
        add_separator()

    def _update_start_button_text(self, index):
        """Update the start button text based on the selected tab"""
        if not self.tabs_initialized:
            return

        button_texts = {
            0: "Convert",  # Convert to DOCX
            1: "Compress",  # Compress PDF
            2: "Merge",  # Merge PDFs
            3: "Split",  # Split PDF
            4: "Extract",  # Extract Text
            5: "Convert",  # Convert to Image
        }
        current_tab = self.tab_widget.widget(index)
        if current_tab and hasattr(current_tab, "start_btn"):
            current_tab.start_btn.setText(button_texts.get(index, "Start"))

    def _add_file(self):
        if not self.tabs_initialized:
            return
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files", os.path.expanduser("~"), "PDF Files (*.pdf)")
        if files:
            current_tab = self.tab_widget.currentWidget()
            if hasattr(current_tab, "add_files_to_table"):
                current_tab.add_files_to_table(files)

    def _add_folder(self):
        if not self.tabs_initialized:
            return
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", os.path.expanduser("~"))
        if folder:
            current_tab = self.tab_widget.currentWidget()
            if hasattr(current_tab, "add_files_to_table"):
                pdf_files = []
                for entry in os.listdir(folder):
                    if entry.lower().endswith(".pdf"):
                        file_path = os.path.join(folder, entry)
                        pdf_files.append(file_path)
                if pdf_files:
                    current_tab.add_files_to_table(pdf_files)

    def _delete_selected(self):
        if not self.tabs_initialized:
            return
        current_tab = self.tab_widget.currentWidget()
        if hasattr(current_tab, "remove_selected_files"):
            current_tab.remove_selected_files()

    def _clear_all(self):
        if not self.tabs_initialized:
            return
        current_tab = self.tab_widget.currentWidget()
        if hasattr(current_tab, "clear_all_files"):
            current_tab.clear_all_files()

    def _start_convert(self):
        """Handle convert button click"""
        if hasattr(self, "convert_tab"):
            self.convert_tab._start_conversion_process()

    def _start_compress(self):
        """Handle compress button click"""
        if hasattr(self, "compress_tab"):
            self.compress_tab._start_compression()

    def _start_merge(self):
        """Handle merge button click"""
        if hasattr(self, "merge_tab"):
            self.merge_tab._start_merge()

    def _start_split(self):
        """Handle split button click"""
        if hasattr(self, "split_tab"):
            self.split_tab._start_split()

    def _start_extract(self):
        """Handle extract button click"""
        if hasattr(self, "extract_tab"):
            self.extract_tab._start_extract()

    def _start_convert_to_image(self):
        """Handle convert to image button click"""
        if hasattr(self, "convert_to_image_tab"):
            self.convert_to_image_tab._start_convert_to_image()

    def closeEvent(self, event):
        # Stop any active workers
        if hasattr(self, "convert_tab") and hasattr(self.convert_tab, "stop_active_conversion"):
            self.convert_tab.stop_active_conversion()
        if (
            hasattr(self, "compress_tab")
            and hasattr(self.compress_tab, "worker")
            and self.compress_tab.worker
            and self.compress_tab.worker.isRunning()
        ):
            self.compress_tab.worker.stop()
        if (
            hasattr(self, "merge_tab")
            and hasattr(self.merge_tab, "worker")
            and self.merge_tab.worker
            and self.merge_tab.worker.isRunning()
        ):
            self.merge_tab.worker.stop()
        if (
            hasattr(self, "split_tab")
            and hasattr(self.split_tab, "worker")
            and self.split_tab.worker
            and self.split_tab.worker.isRunning()
        ):
            self.split_tab.worker.stop()
        if (
            hasattr(self, "extract_tab")
            and hasattr(self.extract_tab, "worker")
            and self.extract_tab.worker
            and self.extract_tab.worker.isRunning()
        ):
            self.extract_tab.worker.stop()
        super().closeEvent(event)


def create_splash_screen():
    """Create a beautiful splash screen"""
    # Create a custom splash screen with gradient background
    splash_pixmap = QPixmap(400, 300)
    splash_pixmap.fill(QColor(214, 240, 250))  # Light blue background

    # Create painter for custom drawing
    painter = QPainter(splash_pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw gradient background
    gradient = QColor(178, 224, 247)  # Lighter blue
    painter.fillRect(0, 0, 400, 300, gradient)

    # Draw title
    title_font = QFont("Arial", 24, QFont.Weight.Bold)
    painter.setFont(title_font)
    painter.setPen(QColor(0, 0, 0))
    painter.drawText(0, 80, 400, 40, Qt.AlignmentFlag.AlignCenter, "PDF Utilities")

    # Draw subtitle - Updated to highlight key features
    subtitle_font = QFont("Arial", 11)
    painter.setFont(subtitle_font)
    painter.setPen(QColor(100, 100, 100))
    painter.drawText(0, 120, 400, 30, Qt.AlignmentFlag.AlignCenter, "Convert • Compress • Merge • Split • Extract")

    # Draw version
    version_font = QFont("Arial", 10)
    painter.setFont(version_font)
    painter.setPen(QColor(150, 150, 150))
    painter.drawText(0, 150, 400, 20, Qt.AlignmentFlag.AlignCenter, "All-in-One PDF Solution")

    # Draw loading text
    loading_font = QFont("Arial", 11)
    painter.setFont(loading_font)
    painter.setPen(QColor(80, 80, 80))
    painter.drawText(0, 200, 400, 30, Qt.AlignmentFlag.AlignCenter, "Initializing...")

    painter.end()

    # Create splash screen
    splash = QSplashScreen(splash_pixmap)
    splash.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

    return splash


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and show splash screen
    splash = create_splash_screen()
    splash.show()

    # Process events to show splash screen immediately
    app.processEvents()

    # Create main window
    window = PDFConverterApp()

    # Create initialization thread
    init_thread = InitializationThread()

    def on_progress_update(message):
        """Update splash screen with progress message"""
        splash.showMessage(message, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, QColor(0, 0, 0))
        app.processEvents()

    def on_initialization_complete():
        """Handle initialization completion"""
        # Initialize real tabs
        window._initialize_real_tabs()

        # Close splash screen and show main window
        splash.finish(window)
        window.show()

    # Connect signals
    init_thread.progress_updated.connect(on_progress_update)
    init_thread.initialization_complete.connect(on_initialization_complete)

    # Start initialization thread
    init_thread.start()

    # Show main window after a short delay (for better UX)
    QTimer.singleShot(500, lambda: window.show() if not window.isVisible() else None)

    sys.exit(app.exec())
