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

    def _fallback_notification(self, message: str, level: str = "info", duration: int = 4000):
        """A fallback in case the notification method isn't available."""
        print(f"[{level.upper()}] Notification: {message}")

    def _setup_common_ui(self):
        layout = QVBoxLayout(self)

        # File Table
        self.file_table = QTableWidget(0, 2)
        self.file_table.setHorizontalHeaderLabels(["File Name", "Size"])
        self.file_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.file_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.file_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.file_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.file_table.setShowGrid(True)
        self.file_table.setAlternatingRowColors(True)
        # Disable sorting for all tables
        self.file_table.setSortingEnabled(False)
        layout.addWidget(self.file_table)

        # Progress Bar
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

        # Start Button
        start_layout = QHBoxLayout()
        start_layout.addStretch()
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
        start_layout.addWidget(self.start_btn)
        layout.addLayout(start_layout)

        # Output Folder Label
        output_folder_label = QLabel("Output Folder")
        output_folder_label.setStyleSheet(
            "font-weight: bold; font-size: 15px; margin-top: 12px; margin-bottom: 4px;color: #000;"
        )
        layout.addWidget(output_folder_label)

        # Output Folder Selection
        output_layout = QHBoxLayout()
        output_label = QLabel("Output:")
        output_label.setStyleSheet("color: #000;")
        output_layout.addWidget(output_label)

        # Radio buttons for output folder
        self.same_folder_radio = QRadioButton("Same as input")
        self.same_folder_radio.setStyleSheet(
            """
            QRadioButton {
                color: #000;
                padding: 4px;
                margin-right: 8px;
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
        output_layout.addWidget(self.same_folder_radio)
        output_layout.addWidget(self.custom_folder_radio)
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Select output folder...")
        self.output_path.setEnabled(False)
        output_layout.addWidget(self.output_path)
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setStyleSheet(
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
        self.browse_btn.setEnabled(False)
        self.browse_btn.clicked.connect(self._browse_folder)
        output_layout.addWidget(self.browse_btn)
        layout.addLayout(output_layout)
        self.custom_folder_radio.toggled.connect(self._toggle_custom_output)

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
        """Add a file to the table with its name and size"""
        try:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            row = self.file_table.rowCount()

            # Disable sorting and updates temporarily
            self.file_table.setUpdatesEnabled(False)

            # Insert row and set items
            self.file_table.insertRow(row)
            name_item = QTableWidgetItem(file_name)
            name_item.setToolTip(file_path)
            size_item = QTableWidgetItem(self._format_size(file_size))

            self.file_table.setItem(row, 0, name_item)
            self.file_table.setItem(row, 1, size_item)

            # Re-enable sorting and updates
            self.file_table.setUpdatesEnabled(True)

        except Exception as e:
            print(f"Error adding file {file_path}: {str(e)}")

    def add_files_to_table(self, file_paths):
        """Add multiple files to the table efficiently"""
        try:
            # Disable sorting and updates temporarily
            self.file_table.setUpdatesEnabled(False)

            # Prepare all items first
            items_to_add = []
            for file_path in file_paths:
                try:
                    file_name = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path)
                    name_item = QTableWidgetItem(file_name)
                    name_item.setToolTip(file_path)
                    size_item = QTableWidgetItem(self._format_size(file_size))
                    items_to_add.append((name_item, size_item))
                except Exception as e:
                    print(f"Error processing file {file_path}: {str(e)}")

            # Add all rows at once
            start_row = self.file_table.rowCount()
            self.file_table.setRowCount(start_row + len(items_to_add))

            # Set all items
            for i, (name_item, size_item) in enumerate(items_to_add):
                self.file_table.setItem(start_row + i, 0, name_item)
                self.file_table.setItem(start_row + i, 1, size_item)

            # Re-enable sorting and updates
            self.file_table.setUpdatesEnabled(True)

        except Exception as e:
            print(f"Error adding files: {str(e)}")
            # Make sure to re-enable updates even if there's an error
            self.file_table.setUpdatesEnabled(True)

    def remove_selected_files(self):
        """Remove selected files from the table"""
        selected = self.file_table.selectionModel().selectedRows()
        for index in sorted(selected, reverse=True):
            self.file_table.removeRow(index.row())

    def clear_all_files(self):
        """Clear all files from the table"""
        self.file_table.setRowCount(0)

    def get_selected_files(self):
        """Get list of selected file paths"""
        selected_files = []
        for row in range(self.file_table.rowCount()):
            item = self.file_table.item(row, 0)
            if item:
                selected_files.append(item.toolTip())
        return selected_files

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
