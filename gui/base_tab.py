import os

from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class BaseTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_common_ui()
        self._apply_common_styles()
        # Store a reference to the main window's notification method
        self.show_notification = getattr(parent, "show_notification", self._fallback_notification)
        # Store reference to the main window for accessing shared table
        self.main_window = parent

    def _fallback_notification(self, message: str, level: str = "info", duration: int = 4000):
        """A fallback in case the notification method isn't available."""
        print(f"[{level.upper()}] Notification: {message}")

    def _setup_common_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        # Section 1: Action Button (Fixed position at top)
        start_layout = QHBoxLayout()
        start_layout.addStretch()
        self._create_start_button()
        start_layout.addWidget(self.start_btn)
        layout.addLayout(start_layout)

        # Section 2: Tab-specific controls container (Fixed middle section)
        self.tab_controls_container = QWidget()
        self.tab_controls_layout = QVBoxLayout(self.tab_controls_container)
        self.tab_controls_layout.setSpacing(6)
        layout.addWidget(self.tab_controls_container)

        # Section 3: Output folder controls (Fixed position)
        self._setup_output_folder_section()
        layout.addLayout(self.output_folder_layout)

        # Section 4: Progress bar (Fixed position at bottom)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #b2e0f7;
                border-radius: 4px;
                text-align: center;
                background: #ffffff;
                color: #000;
            }
            QProgressBar::chunk {
                background: #00bfff;
                border-radius: 3px;
            }
        """
        )
        layout.addWidget(self.progress_bar)

        # Store layout reference for adding controls later
        self.main_layout = layout

    def _create_start_button(self):
        """Create the Start button with consistent styling"""
        self.start_btn = QPushButton("Start")
        self.start_btn.setStyleSheet(
            """
            QPushButton {
                background: #00bfff;
                color: #000;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                padding: 4px 16px;
                min-width: 80px;
                min-height: 24px;
            }
            QPushButton:hover {
                background: #009fd6;
            }
            QPushButton:pressed {
                background: #007fa3;
            }
        """
        )
        return self.start_btn

    def _setup_output_folder_section(self):
        """Setup output folder controls in a separate method"""
        self.output_folder_layout = QHBoxLayout()
        
        # Output Folder Label
        output_folder_label = QLabel("Output Folder:")
        output_folder_label.setStyleSheet(
            "font-weight: bold; font-size: 11px; margin-top: 6px; margin-bottom: 3px;color: #000;"
        )
        self.output_folder_layout.addWidget(output_folder_label)

        # Radio buttons for output folder
        self.same_folder_radio = QRadioButton("Same as input")
        self.same_folder_radio.setStyleSheet(
            """
            QRadioButton {
                color: #000;
                padding: 4px;
                margin-right: 8px;
                font-size: 11px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #000;
                border-radius: 8px;
            }
            QRadioButton::indicator:checked {
                background-color: #00bfff;
                border: 1px solid #000;
            }
            QRadioButton::indicator:unchecked {
                background-color: white;
            }
        """
        )
        self.custom_folder_radio = QRadioButton("Custom folder")
        self.custom_folder_radio.setStyleSheet(
            """
            QRadioButton {
                color: #000;
                padding: 4px;
                margin-right: 8px;
                font-size: 11px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #000;
                border-radius: 8px;
            }
            QRadioButton::indicator:checked {
                background-color: #00bfff;
                border: 1px solid #000;
            }
            QRadioButton::indicator:unchecked {
                background-color: white;
            }
        """
        )
        self.same_folder_radio.setChecked(True)
        self.output_folder_layout.addWidget(self.same_folder_radio)
        self.output_folder_layout.addWidget(self.custom_folder_radio)
        
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Select output folder...")
        self.output_path.setEnabled(False)
        self.output_path.setStyleSheet(
            """
            QLineEdit {
                background: #fff;
                color: #000;
                border: 1px solid #b2e0f7;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 11px;
            }
        """
        )
        self.output_folder_layout.addWidget(self.output_path)
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setStyleSheet(
            """
            QPushButton {
                background: #00bfff;
                color: #000;
                border: none;
                border-radius: 4px;
                font-size: 11px;
                padding: 4px 12px;
                min-width: 60px;
                min-height: 20px;
            }
            QPushButton:hover {
                background: #009fd6;
            }
            QPushButton:pressed {
                background: #007fa3;
            }
        """
        )
        self.browse_btn.setEnabled(False)
        self.browse_btn.clicked.connect(self._browse_folder)
        self.output_folder_layout.addWidget(self.browse_btn)
        
        # Connect radio button toggle
        self.custom_folder_radio.toggled.connect(self._toggle_custom_output)

    def add_output_folder_controls(self):
        """This method is now handled in _setup_common_ui() for consistent layout"""
        pass

    def add_tab_controls(self, controls_layout):
        """Add tab-specific controls to the dedicated container"""
        self.tab_controls_layout.addLayout(controls_layout)

    def _apply_common_styles(self):
        # Apply the same styles from main_window.py
        self.setStyleSheet(
            """
            QWidget {
                background: #d6f0fa;
            }
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
            QPushButton {
                background: #00bfff;
                color: #000;
                border: none;
                border-radius: 20px;
                font-size: 20px;
                font-weight: bold;
                min-width: 160px;
                min-height: 48px;
                padding: 8px 32px;
            }
            QPushButton:hover {
                background: #009fd6;
            }
            QPushButton:pressed {
                background: #007fa3;
            }
            QRadioButton {
                color: #000;
                font-size: 14px;
            }
            QLineEdit {
                background: #fff;
                color: #000;
                border: 1px solid #b2e0f7;
                border-radius: 6px;
                padding: 4px 8px;
            }
        """
        )

    def _toggle_custom_output(self, checked):
        self.output_path.setEnabled(checked)
        self.browse_btn.setEnabled(checked)

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", os.path.expanduser("~"))
        if folder:
            self.output_path.setText(folder)

    def _format_size(self, size_bytes):
        """Format file size in bytes to human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f} KB"
        else:
            return f"{size_bytes/1024/1024:.2f} MB"

    def add_file_to_table(self, file_path):
        """Add a file to the shared table with its name and size"""
        if self.main_window:
            self.main_window.add_file_to_table(file_path)

    def add_files_to_table(self, file_paths):
        """Add multiple files to the shared table efficiently"""
        if self.main_window:
            self.main_window.add_files_to_table(file_paths)

    def remove_selected_files(self):
        """Remove selected files from the shared table"""
        if self.main_window:
            self.main_window.remove_selected_files()

    def clear_all_files(self):
        """Clear all files from the shared table"""
        if self.main_window:
            self.main_window.clear_all_files()

    def get_selected_files(self):
        """Get list of selected file paths from the shared table"""
        if self.main_window:
            return self.main_window.get_selected_files()
        return []

    def get_output_directory(self):
        """Get the selected output directory"""
        if self.same_folder_radio.isChecked():
            # Return the directory of the first file
            files = self.get_selected_files()
            if files:
                return os.path.dirname(files[0])
            return None
        else:
            return self.output_path.text() if self.output_path.text() else None
