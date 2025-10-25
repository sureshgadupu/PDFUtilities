import os
import sys
from pathlib import Path

from PyQt6.QtCore import QSize, Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QSplashScreen,
    QTabWidget,
    QTabBar,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
    QProgressBar,
    QSizePolicy,
)

import fitz  # PyMuPDF for PDF password detection

from compressor import is_ghostscript_available
from gui.custom_widgets import PasswordInputWidget
from gui.notification import NotificationWidget
from password_manager import PasswordManager
from gui.tabs import (
    CompressTab,
    ConvertTab,
    ConvertToImageTab,
    ExtractTab,
    MergeTab,
    PasswordRemovalTab,
    SplitTab,
)
from version import get_version


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


def is_pdf_password_protected(file_path):
    """Check if a PDF file is password protected"""
    try:
        doc = fitz.open(file_path)
        # Try to access the first page without password
        doc[0]
        doc.close()
        return False
    except Exception as e:
        # If we can't access the page, it's likely password protected
        # But let's be more specific about the error
        error_msg = str(e).lower()
        if 'password' in error_msg or 'encrypted' in error_msg or 'permission' in error_msg or 'closed' in error_msg:
            return True
        # For other errors, we'll assume it's not password protected
        return False


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






class StretchableTabBar(QTabBar):
    """Custom tab bar with a stretchable dummy tab at the end"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stretch_tab_index = -1
        self._setup_stretch_tab()
        
    def _setup_stretch_tab(self):
        """Add a stretchable dummy tab at the end"""
        # Add a dummy tab that will stretch
        self.stretch_tab_index = self.addTab("")
        self.setTabEnabled(self.stretch_tab_index, False)
        self.setTabTextColor(self.stretch_tab_index, QColor(0, 0, 0, 0))  # Transparent text
        
    def tabSizeHint(self, index):
        """Override to make the stretch tab expand to fill remaining space"""
        if index == self.stretch_tab_index:
            # Calculate the total width of all real tabs
            real_tabs_width = 0
            for i in range(self.count()):
                if i != self.stretch_tab_index:
                    real_tabs_width += super().tabSizeHint(i).width()
            
            # Get the available width for the tab bar
            available_width = self.width()
            
            # Calculate the stretch tab width to fill remaining space
            stretch_width = max(0, available_width - real_tabs_width)
            return QSize(stretch_width, super().tabSizeHint(index).height())
        else:
            return super().tabSizeHint(index)
    
    def resizeEvent(self, event):
        """Handle resize events to update stretch tab size"""
        super().resizeEvent(event)
        # Force a repaint to update the stretch tab size
        self.update()
        
    def mousePressEvent(self, event):
        """Prevent clicking on the stretch tab"""
        tab_index = self.tabAt(event.pos())
        if tab_index == self.stretch_tab_index:
            return  # Ignore clicks on stretch tab
        super().mousePressEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        """Prevent double-clicking on the stretch tab"""
        tab_index = self.tabAt(event.pos())
        if tab_index == self.stretch_tab_index:
            return  # Ignore double-clicks on stretch tab
        super().mouseDoubleClickEvent(event)


class PDFConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Utility App")
        self.setWindowIcon(QIcon(get_resource_path("gui/icons/tools.svg")))
        self.resize(1000, 700)

        # Initialize password manager
        self.password_manager = PasswordManager()

        # Initialize components
        self.tabs_initialized = False
        self._initialize_ui_components()

        # Set up notification widget
        self.notification_widget = NotificationWidget(self)

        # Check for Ghostscript availability (non-blocking)
        QTimer.singleShot(100, self._check_ghostscript)

    def show_notification(self, message: str, level: str = "info", duration: int = 4000):
        """Show a toast notification."""
        self.notification_widget.show_message(message, level, duration)

    def _initialize_ui_components(self):
        """Initialize UI components that don't require heavy processing"""
        self._setup_menu()
        self._setup_toolbar()
        self._setup_central_skeleton()

    def _setup_central_skeleton(self):
        """Setup the basic central widget structure without heavy tab initialization"""
        central = QWidget()
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create shared file table widget
        self._setup_shared_file_table()
        main_layout.addWidget(self.shared_file_table_container)
        
        # Create tab widget with custom tab bar
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setDocumentMode(True)
        
        # Set custom tab bar with stretchable dummy tab
        self.custom_tab_bar = StretchableTabBar()
        self.tab_widget.setTabBar(self.custom_tab_bar)
        


        self.tab_widget.setStyleSheet(
            """
            QTabWidget {
                background: #d6f0fa;
                margin: 0px;
                padding: 0px;
            }
            QTabWidget::pane {
                border: 1px solid #b2e0f7;
                background: #ffffff;
                margin: 0px;
                padding: 0px;
            }
            QTabBar {
                background: #d6f0fa;
                margin: 0px;
                padding: 0px;
                spacing: 0px;
            }
            QTabBar::tab {
                background: #d6f0fa;
                color: #000;
                padding: 8px 16px;
                border: 1px solid #b2e0f7;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom: 1px solid #ffffff;
                border-top: 1px solid #b2e0f7;
            }
            QTabBar::tab:hover {
                background: #b7d6fb;
            }
            QTabBar::tab:selected:hover {
                background: #ffffff;
                border-bottom: 1px solid #b7d6fb;
            }
            QTabBar::tab:disabled {
                background: #d6f0fa;
                border: none;
                color: transparent;
            }
            QTabBar::tab:disabled:hover {
                background: #d6f0fa;
                border: none;
            }
            QTabBar::scroller {
                background: #d6f0fa;
            }
            QTabBar QToolButton {
                background: #d6f0fa;
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
                background: #b2e0f7;
                spacing: 0px;
                margin: 0px;
                padding: 0px;
            }
            QMainWindow::separator {
                background: #b2e0f7;
                width: 0px;
                height: 0px;
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
                spacing: 0px;
                margin: 0px;
                padding: 0px;
                border: none;
                border-bottom: none;
            }
            QMenuBar::item {
                background: #b2e0f7;
                color: #000;
                spacing: 0px;
                margin: 0px;
                padding: 4px 8px;
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
            ("Remove Password", "gui/icons/x-circle.svg"),
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
        
        # The stretch tab is automatically added by the custom tab bar

    def _setup_shared_file_table(self):
        """Setup the shared file table widget"""
        # Create a container widget for the file table
        self.shared_file_table_container = QWidget()
        table_layout = QVBoxLayout(self.shared_file_table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the shared file table with password column
        self.shared_file_table = QTableWidget(0, 3)
        self.shared_file_table.setHorizontalHeaderLabels(["File Name", "Size", "Password"])
        
        # Configure column resizing with specific percentages
        header = self.shared_file_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # File Name - 70%
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)  # Size - 10%
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)  # Password - 20%
        header.setMinimumSectionSize(50)
        header.setStretchLastSection(False)
        
        # Set stretch factors to achieve the desired percentages
        # Stretch mode on column 0 with factors on others gives us control
        header.setDefaultSectionSize(100)
        
        # We'll set actual widths after the table is shown
        QTimer.singleShot(100, self._set_column_percentages)
        self.shared_file_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.shared_file_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.shared_file_table.setShowGrid(True)
        self.shared_file_table.setAlternatingRowColors(True)
        # Disable sorting for the shared table
        self.shared_file_table.setSortingEnabled(False)

        # Set minimum height for the table to ensure adequate space
        self.shared_file_table.setMinimumHeight(400)  # Adjust this value as needed

        
        # Apply table styles
        self.shared_file_table.setStyleSheet(
            """
            QTableWidget {
                background: #ffffff;
                color: #000;
                gridline-color: #b2e0f7;
                font-size: 15px;
            }
            QTableWidget::item:selected {
                background: #b7d6fb;
                color: #000;
            }
            QHeaderView::section {
                background-color: #b2e0f7;
                color: #000;
                font-weight: bold;
                border: 1px solid #a2d4ec;
                padding: 6px;
            }
        """
        )
        
        table_layout.addWidget(self.shared_file_table)

    def _format_size(self, size_bytes):
        """Format file size in bytes to human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f} KB"
        else:
            return f"{size_bytes/1024/1024:.2f} MB"

    def add_file_to_table(self, file_path):
        """Add a file to the shared table with its name, size, and password input"""
        try:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            row = self.shared_file_table.rowCount()

            # Disable sorting and updates temporarily
            self.shared_file_table.setUpdatesEnabled(False)

            # Insert row and set items
            self.shared_file_table.insertRow(row)
            name_item = QTableWidgetItem(file_name)
            name_item.setToolTip(file_path)
            size_item = QTableWidgetItem(self._format_size(file_size))

            # Check if PDF is password protected
            is_protected = False
            if file_name.lower().endswith('.pdf'):
                is_protected = is_pdf_password_protected(file_path)

            # Create password input widget
            password_widget = PasswordInputWidget(password_manager=self.password_manager)
            if is_protected:
                password_widget.password_input.setPlaceholderText("Password required")
                password_widget.password_input.setStyleSheet("""
                    QLineEdit {
                        background: #fff3cd;
                        color: #856404;
                        border: 1px solid #ffeaa7;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 12px;
                    }
                    QLineEdit:focus {
                        border: 2px solid #ffc107;
                    }
                """)
            else:
                password_widget.password_input.setPlaceholderText("No password needed")
                password_widget.password_input.setEnabled(False)
                password_widget.password_input.setStyleSheet("""
                    QLineEdit {
                        background: #d4edda;
                        color: #155724;
                        border: 1px solid #c3e6cb;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 12px;
                    }
                """)

            self.shared_file_table.setItem(row, 0, name_item)
            self.shared_file_table.setItem(row, 1, size_item)
            self.shared_file_table.setCellWidget(row, 2, password_widget)

            # Re-enable sorting and updates
            self.shared_file_table.setUpdatesEnabled(True)

        except Exception as e:
            print(f"Error adding file {file_path}: {str(e)}")

    def add_files_to_table(self, file_paths):
        """Add multiple files to the shared table efficiently"""
        try:
            # Disable sorting and updates temporarily
            self.shared_file_table.setUpdatesEnabled(False)

            # Prepare all items first
            items_to_add = []
            for file_path in file_paths:
                try:
                    file_name = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path)
                    name_item = QTableWidgetItem(file_name)
                    name_item.setToolTip(file_path)
                    size_item = QTableWidgetItem(self._format_size(file_size))
                    
                    # Check if PDF is password protected
                    is_protected = False
                    if file_name.lower().endswith('.pdf'):
                        is_protected = is_pdf_password_protected(file_path)
                    
                    # Create password input widget
                    password_widget = PasswordInputWidget(password_manager=self.password_manager)
                    if is_protected:
                        password_widget.password_input.setPlaceholderText("Password required")
                        password_widget.password_input.setStyleSheet("""
                            QLineEdit {
                                background: #fff3cd;
                                color: #856404;
                                border: 1px solid #ffeaa7;
                                border-radius: 4px;
                                padding: 4px 8px;
                                font-size: 12px;
                            }
                            QLineEdit:focus {
                                border: 2px solid #ffc107;
                            }
                        """)
                    else:
                        password_widget.password_input.setPlaceholderText("No password needed")
                        password_widget.password_input.setEnabled(False)
                        password_widget.password_input.setStyleSheet("""
                            QLineEdit {
                                background: #d4edda;
                                color: #155724;
                                border: 1px solid #c3e6cb;
                                border-radius: 4px;
                                padding: 4px 8px;
                                font-size: 12px;
                            }
                        """)
                    
                    items_to_add.append((name_item, size_item, password_widget))
                except Exception as e:
                    print(f"Error processing file {file_path}: {str(e)}")

            # Add all rows at once
            start_row = self.shared_file_table.rowCount()
            self.shared_file_table.setRowCount(start_row + len(items_to_add))

            # Set all items
            for i, (name_item, size_item, password_widget) in enumerate(items_to_add):
                self.shared_file_table.setItem(start_row + i, 0, name_item)
                self.shared_file_table.setItem(start_row + i, 1, size_item)
                self.shared_file_table.setCellWidget(start_row + i, 2, password_widget)

            # Re-enable sorting and updates
            self.shared_file_table.setUpdatesEnabled(True)

        except Exception as e:
            print(f"Error adding files: {str(e)}")
            # Make sure to re-enable updates even if there's an error
            self.shared_file_table.setUpdatesEnabled(True)

    def remove_selected_files(self):
        """Remove selected files from the shared table"""
        selected = self.shared_file_table.selectionModel().selectedRows()
        for index in sorted(selected, reverse=True):
            self.shared_file_table.removeRow(index.row())

    def clear_all_files(self):
        """Clear all files from the shared table"""
        self.shared_file_table.setRowCount(0)

    def get_selected_files(self):
        """Get list of selected file paths from the shared table"""
        selected_files = []
        for row in range(self.shared_file_table.rowCount()):
            item = self.shared_file_table.item(row, 0)
            if item:
                selected_files.append(item.toolTip())
        return selected_files

    def get_file_passwords(self):
        """Get passwords for all files in the table"""
        passwords = {}
        for row in range(self.shared_file_table.rowCount()):
            item = self.shared_file_table.item(row, 0)
            if item:
                file_path = item.toolTip()
                password_widget = self.shared_file_table.cellWidget(row, 2)
                if password_widget:
                    password = password_widget.get_password()
                    if password:  # Only store non-empty passwords
                        passwords[file_path] = password
        return passwords

    def _set_column_percentages(self):
        """Set column widths based on percentages: File Name 55%, Size 15%, Password 30%"""
        if not hasattr(self, 'shared_file_table'):
            return
        
        # Get the actual available width
        available_width = self.shared_file_table.viewport().width()
        
        # Calculate widths based on percentages
        file_name_width = int(available_width * 0.55)  # 55% (reduced by 5%)
        size_width = int(available_width * 0.15)       # 15% (increased by 5%)
        password_width = int(available_width * 0.30)   # 30%
        
        # Set the column widths
        header = self.shared_file_table.horizontalHeader()
        
        # Temporarily change resize modes to set widths
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        
        # Set the widths
        self.shared_file_table.setColumnWidth(0, file_name_width)
        self.shared_file_table.setColumnWidth(1, size_width)
        self.shared_file_table.setColumnWidth(2, password_width)
        
        # Restore resize modes - keep File Name as Stretch so it adapts to window resize
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)


    def _initialize_real_tabs(self):
        """Initialize the real tabs with all functionality"""
        if self.tabs_initialized:
            return

        # Create real tabs, passing the main window as the parent
        self.convert_tab = ConvertTab(self)
        self.compress_tab = CompressTab(self)
        self.merge_tab = MergeTab(self)
        self.split_tab = SplitTab(self)
        self.extract_tab = ExtractTab(self)
        self.convert_to_image_tab = ConvertToImageTab(self)
        self.password_removal_tab = PasswordRemovalTab(self)

        # Replace placeholder tabs with real tabs
        # Note: The stretch tab is at the end, so we need to account for it
        real_tab_count = 7  # Number of real tabs
        
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

        self.tab_widget.removeTab(6)  # Remove Remove Password placeholder
        self.tab_widget.insertTab(
            6, self.password_removal_tab, QIcon(get_resource_path("gui/icons/x-circle.svg")), "Remove Password"
        )
        
        # Update the stretch tab index after all real tabs are added
        self.custom_tab_bar.stretch_tab_index = real_tab_count

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
        self.password_removal_tab.start_btn.clicked.connect(self._start_password_removal)

        self.tabs_initialized = True

        # Set the first tab (Convert to DOCX) as the default active tab
        self.tab_widget.setCurrentIndex(0)



    def _check_ghostscript(self):
        """Check for Ghostscript availability (non-blocking)"""
        if not is_ghostscript_available():
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Ghostscript Not Found")
            msg_box.setText("Ghostscript is required for PDF compression features. Please ensure Ghostscript is installed on your system.")
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            # Set the dialog text color to black and style the button
            msg_box.setStyleSheet("""
                QMessageBox { 
                    color: black; 
                } 
                QMessageBox QLabel { 
                    color: black; 
                }
                QMessageBox QPushButton {
                    background-color: #b2e0f7;
                    color: black;
                    border: 1px solid #8fc7e6;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 12px;
                    min-width: 60px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #a2d4ec;
                    border-color: #7bb8d6;
                }
                QMessageBox QPushButton:pressed {
                    background-color: #92c8dc;
                }
            """)
            msg_box.exec()

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

        add_folder_action = QAction("Add Folder", self)
        add_folder_action.setShortcut("Ctrl+Shift+O")
        add_folder_action.triggered.connect(self._add_folder)
        file_menu.addAction(add_folder_action)

        # Add separator before Exit
        separator = QAction(self)
        separator.setSeparator(True)
        separator.setVisible(True)
        file_menu.addAction(separator)

        # Add Exit action
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        file_menu.setStyleSheet(
            """
            QMenu::item {
                background: #b2e0f7;
                color: #000000;
                padding: 4px 8px;
            }
            QMenu::item:selected {
                background: #a2d4ec;
                color: #000000;
            }
            QMenu::separator {
                background: #a2d4ec;
                height: 1px;
                margin: 2px 4px;
            }
        """
        )

        # Add Edit menu items
        delete_action = QAction("Remove", self)
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

        # Add Help menu items
        documentation_action = QAction("Documentation", self)
        documentation_action.setShortcut("F1")
        documentation_action.triggered.connect(self._show_documentation)
        help_menu.addAction(documentation_action)

        help_menu.addSeparator()

        about_action = QAction("About PDF Utilities", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        help_menu.setStyleSheet(
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
        toolbar.setStyleSheet(
            """
            QToolBar {
                background: #b2e0f7;
                color: #000;
                spacing: 0px;
                margin: 0px;
                padding: 2px;
                border: none;
                border-top: 1px solid #8fc7e6;
                border-bottom: none;
            }
            QToolBar QWidget {
                background: #b2e0f7;
            }
            QToolButton {
                background: transparent;
            }
            QToolBar::separator {
                background: #b2e0f7;
                width: 2px;
                margin: 0px;
            }
        """
        )
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
            # Use a visible color for the separator
            line.setStyleSheet("background: #8fc7e6; min-width: 2px; max-width: 2px; border: none; margin: 0px;")
            sep_action = QWidgetAction(toolbar)
            sep_action.setDefaultWidget(line)
            toolbar.addAction(sep_action)

        self.add_file_btn = add_toolbar_button("gui/icons/file-plus.svg", "Add File", self._add_file)
        add_separator()
        self.add_folder_btn = add_toolbar_button("gui/icons/folder-plus.svg", "Add Folder", self._add_folder)
        add_separator()
        self.delete_btn = add_toolbar_button("gui/icons/trash-2.svg", "Remove", self._delete_selected)
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
            6: "Remove",  # Remove Password
        }
        current_tab = self.tab_widget.widget(index)
        if current_tab and hasattr(current_tab, "start_btn"):
            current_tab.start_btn.setText(button_texts.get(index, "Start"))

    def _add_file(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files", os.path.expanduser("~"), "PDF Files (*.pdf)")
        if files:
            self.add_files_to_table(files)

    def _add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", os.path.expanduser("~"))
        if folder:
            pdf_files = []
            for entry in os.listdir(folder):
                if entry.lower().endswith(".pdf"):
                    file_path = os.path.join(folder, entry)
                    pdf_files.append(file_path)
            if pdf_files:
                self.add_files_to_table(pdf_files)

    def _delete_selected(self):
        self.remove_selected_files()

    def _clear_all(self):
        self.clear_all_files()

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

    def _start_password_removal(self):
        """Handle password removal button click"""
        if hasattr(self, "password_removal_tab"):
            self.password_removal_tab._start_password_removal()

    def _show_about(self):
        """Show About dialog"""
        current_version = get_version()
        about_text = f"""
        <div style="color: black;">
        <h2>PDF Utilities</h2>
        <p><b>Version:</b> {current_version}</p>
        <p><b>Description:</b> A comprehensive PDF processing application built with PyQt6.</p>
        <p><b>Features:</b></p>
        <ul>
            <li>Convert PDF to DOCX</li>
            <li>Compress PDF files</li>
            <li>Merge multiple PDFs</li>
            <li>Split PDF pages</li>
            <li>Extract text from PDFs</li>
            <li>Convert PDF to images</li>
            <li>Remove password protection</li>
        </ul>
        <p><b>License:</b> GNU Affero General Public License v3.0 (AGPL-3.0)</p>
        <p><b>Dependencies:</b> PyQt6, PyMuPDF, pdf2docx, Pillow, Ghostscript</p>
        </div>
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About PDF Utilities")
        msg_box.setText(about_text)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setStyleSheet("QPushButton { color: black; }")
        msg_box.exec()

    def _show_documentation(self):
        """Show documentation dialog"""
        doc_text = """
        <div style="color: black;">
        <h2>PDF Utilities Documentation</h2>
        
        <h3>Quick Start Guide</h3>
        <p><b>1. Add Files:</b> Use "Add File" or "Add Folder" to select PDF files</p>
        <p><b>2. Choose Operation:</b> Select the appropriate tab for your task</p>
        <p><b>3. Configure Settings:</b> Adjust options as needed</p>
        <p><b>4. Select Output:</b> Choose where to save results</p>
        <p><b>5. Start Processing:</b> Click the action button</p>
        
        <h3>Features</h3>
        <p><b>Convert to DOCX:</b> Convert PDF files to editable Word documents</p>
        <p><b>Compress PDF:</b> Reduce file size with quality options</p>
        <p><b>Merge PDFs:</b> Combine multiple PDFs into one file</p>
        <p><b>Split PDF:</b> Extract specific pages or ranges</p>
        <p><b>Extract Text:</b> Pull text content from PDFs</p>
        <p><b>Convert to Image:</b> Export PDF pages as images</p>
        <p><b>Remove Password:</b> Remove password protection from PDF files</p>
        
        <h3>Keyboard Shortcuts</h3>
        <p><b>Ctrl+O:</b> Add File</p>
        <p><b>Ctrl+Shift+O:</b> Add Folder</p>
        <p><b>Remove:</b> Remove selected files</p>
        <p><b>Ctrl+Shift+D:</b> Clear all files</p>
        <p><b>Ctrl+Q:</b> Exit application</p>
        <p><b>F1:</b> Show this documentation</p>
        </div>
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Documentation")
        msg_box.setText(doc_text)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setStyleSheet("QPushButton { color: black; }")
        msg_box.exec()

    def resizeEvent(self, event):
        """Ensure notification widget is repositioned on window resize."""
        super().resizeEvent(event)
        self.notification_widget.resizeEvent(event)

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
        if (
            hasattr(self, "password_removal_tab")
            and hasattr(self.password_removal_tab, "worker")
            and self.password_removal_tab.worker
            and self.password_removal_tab.worker.isRunning()
        ):
            self.password_removal_tab.worker.stop()
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
    title_font = QFont("Arial", 18, QFont.Weight.Bold)
    painter.setFont(title_font)
    painter.setPen(QColor(0, 0, 0))
    painter.drawText(0, 70, 400, 35, Qt.AlignmentFlag.AlignCenter, "PDF Utilities")

    # Draw subtitle - Updated to highlight key features
    subtitle_font = QFont("Arial", 9)
    painter.setFont(subtitle_font)
    painter.setPen(QColor(100, 100, 100))
    painter.drawText(0, 110, 400, 25, Qt.AlignmentFlag.AlignCenter, "Convert • Compress • Merge • Split • Extract • Remove Password")

    # Draw version
    version_font = QFont("Arial", 8)
    painter.setFont(version_font)
    painter.setPen(QColor(150, 150, 150))
    painter.drawText(0, 140, 400, 20, Qt.AlignmentFlag.AlignCenter, "All-in-One PDF Solution")

    # Draw loading text
    loading_font = QFont("Arial", 9)
    painter.setFont(loading_font)
    painter.setPen(QColor(80, 80, 80))
    painter.drawText(0, 180, 400, 25, Qt.AlignmentFlag.AlignCenter, "Initializing...")

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
