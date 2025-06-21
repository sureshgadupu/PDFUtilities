import os

from PyQt6.QtCore import QStandardPaths, Qt
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import (
    QButtonGroup,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from workers import CompressionWorker


class CompressTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("PDF Compression")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            """
            color: #000000;
            background-color: #f0f0f0;
            padding: 22px 0 16px 0;
            border-bottom: 1.5px solid #cccccc;
            border-radius: 8px 8px 0 0;
        """
        )
        layout.addWidget(title_label)

        # File list
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self._show_context_menu)
        self.file_list.setStyleSheet(
            """
            QListWidget {
                background-color: #ffffff;
                color: #222222;
                border: 1.5px solid #a0a0a0;
                border-radius: 4px;
                padding: 8px;
                font-size: 15px;
            }
            QListWidget::item {
                padding: 6px 2px;
            }
            QListWidget::item:selected {
                background: #b7d6fb;
                color: #222222;
            }
        """
        )
        layout.addWidget(self.file_list)

        # File selection buttons
        button_layout = QHBoxLayout()
        self.select_button = QPushButton("Select PDF Files")
        self.select_button.clicked.connect(self._select_files)
        self.select_button.setStyleSheet("color: white;")
        button_layout.addWidget(self.select_button)

        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self._remove_selected_files)
        self.remove_button.setStyleSheet("color: white;")
        self.remove_button.setEnabled(False)
        button_layout.addWidget(self.remove_button)
        layout.addLayout(button_layout)

        # Compression options
        options_group = QGroupBox("Compression Options")
        options_layout = QHBoxLayout()
        self.radio_low = QRadioButton("Low")
        self.radio_medium = QRadioButton("Medium")
        self.radio_high = QRadioButton("High")
        self.radio_medium.setChecked(True)
        self.compression_group = QButtonGroup()
        self.compression_group.addButton(self.radio_low)
        self.compression_group.addButton(self.radio_medium)
        self.compression_group.addButton(self.radio_high)
        options_layout.addWidget(self.radio_low)
        options_layout.addWidget(self.radio_medium)
        options_layout.addWidget(self.radio_high)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Target size input
        target_layout = QHBoxLayout()
        self.target_size_input = QLineEdit()
        self.target_size_input.setPlaceholderText("Target size (KB)")
        self.target_size_input.setFixedWidth(150)
        self.target_size_input.textChanged.connect(self._on_target_size_changed)
        target_label = QLabel("or Target Size:")
        target_label.setStyleSheet("color: white;")
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_size_input)

        # Unit selection radio buttons
        self.unit_kb = QRadioButton("KB")
        self.unit_mb = QRadioButton("MB")
        self.unit_kb.setChecked(True)  # Default to KB
        self.unit_kb.setStyleSheet("color: white;")
        self.unit_mb.setStyleSheet("color: white;")
        self.unit_kb.toggled.connect(self._on_unit_changed)
        self.unit_mb.toggled.connect(self._on_unit_changed)
        target_layout.addWidget(self.unit_kb)
        target_layout.addWidget(self.unit_mb)
        target_layout.addStretch()
        layout.addLayout(target_layout)

        # Start compression button
        self.compress_button = QPushButton("Start Compression")
        self.compress_button.clicked.connect(self._start_compression)
        self.compress_button.setEnabled(False)
        layout.addWidget(self.compress_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Select PDF files to begin.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: white;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self._apply_styles()

    def _apply_styles(self):
        self.setStyleSheet(
            """
            CompressTab {
                background-color: #f3f4f6;
            }
            QPushButton {
                background-color: #808080;
                color: #FFFFFF;
                border: 1px solid #606060;
                padding: 12px 20px;
                border-radius: 6px;
                font-size: 15px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #888888;
                color: #FFFFFF;
                border-color: #686868;
            }
            QPushButton:pressed {
                background-color: #707070;
                color: #FFFFFF;
                border-color: #686868;
            }
            QPushButton:disabled {
                background-color: #808080;
                color: #cccccc;
                border-color: #707070;
            }
            QProgressBar {
                border: 1px solid #b0b0b0;
                border-radius: 6px;
                text-align: center;
                background: #e0e0e0;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background-color: #606060;
                border-radius: 5px;
            }
            QLabel {
                color: #000000;
            }
        """
        )

    def _show_context_menu(self, position):
        if self.file_list.count() > 0:
            menu = QMenu()
            remove_action = QAction("Remove Selected", self)
            remove_action.triggered.connect(self._remove_selected_files)
            menu.addAction(remove_action)
            menu.exec(self.file_list.mapToGlobal(position))

    def _remove_selected_files(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            self.file_list.takeItem(self.file_list.row(item))

        remaining_files = self.file_list.count()
        if remaining_files > 0:
            self.status_label.setText(f"{remaining_files} file(s) selected. Ready to compress.")
            self.status_label.setStyleSheet("color: white;")
            self.compress_button.setEnabled(True)
        else:
            self.status_label.setText("Select PDF files to begin.")
            self.status_label.setStyleSheet("color: white;")
            self.compress_button.setEnabled(False)

    def _select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PDF Files",
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation),
            "PDF Files (*.pdf)",
        )
        if files:
            for f in files:
                item = QListWidgetItem(f)
                item.setToolTip(f)
                self.file_list.addItem(item)
            self.status_label.setText(f"{self.file_list.count()} file(s) selected. Ready to compress.")
            self.status_label.setStyleSheet("color: white;")
            self.compress_button.setEnabled(True)
            self.remove_button.setEnabled(True)
        else:
            self.compress_button.setEnabled(False)
            self.remove_button.setEnabled(False)
            self.status_label.setText("Select PDF files to begin.")
            self.status_label.setStyleSheet("color: white;")

    def _on_target_size_changed(self):
        # If target size is set, disable compression level radios
        has_target = bool(self.target_size_input.text().strip())
        for btn in [self.radio_low, self.radio_medium, self.radio_high]:
            btn.setEnabled(not has_target)

    def _on_unit_changed(self):
        if self.unit_kb.isChecked():
            self.target_size_input.setPlaceholderText("Target size (KB)")
        else:
            self.target_size_input.setPlaceholderText("Target size (MB)")

    def _start_compression(self):
        pdf_files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        if not pdf_files:
            self.status_label.setText("No files to compress. Please select PDF files first.")
            self.status_label.setStyleSheet("color: orange;")
            return
        # Output directory
        output_dir_name = "CompressedPDFs_from_App"
        documents_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        output_directory = os.path.join(documents_path, output_dir_name)
        # Compression mode or target size
        target_size = self.target_size_input.text().strip()
        if target_size:
            try:
                target_size_value = float(target_size)
                if target_size_value <= 0:
                    raise ValueError
                # Convert to KB if MB is selected
                if self.unit_mb.isChecked():
                    target_size_value *= 1024  # Convert MB to KB
            except ValueError:
                self.status_label.setText("Invalid target size. Enter a positive number.")
                self.status_label.setStyleSheet("color: red;")
                return
            compression_mode = None
        else:
            target_size_value = None
            if self.radio_low.isChecked():
                compression_mode = "low"
            elif self.radio_medium.isChecked():
                compression_mode = "medium"
            else:
                compression_mode = "high"
        # Start worker
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Starting compression...")
        self.status_label.setStyleSheet("color: white;")
        self.worker = CompressionWorker(
            pdf_files, output_directory, compression_mode=compression_mode, target_size_kb=target_size_value, parent=self
        )
        self.worker.progress.connect(self._update_progress_bar)
        self.worker.status_update.connect(self._update_status_label)
        self.worker.finished.connect(self._handle_compression_finished)
        self.worker.error.connect(self._handle_compression_error)
        self.worker.start()
        self.compress_button.setEnabled(False)
        self.select_button.setEnabled(False)

    def _update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def _update_status_label(self, message):
        self.status_label.setText(message)
        if "Error" in message or "Failed" in message:
            self.status_label.setStyleSheet("color: red;")
        elif "Compressed" in message or "Created output directory" in message:
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setStyleSheet("color: white;")

    def _handle_compression_finished(self, successes, failures):
        self.progress_bar.setValue(100)
        num_success = len(successes)
        num_failed = len(failures)
        if num_failed == 0 and num_success > 0:
            final_message = f"All {num_success} files compressed successfully."
            self.status_label.setStyleSheet("color: green;")
        elif num_success > 0 and num_failed > 0:
            final_message = f"Partial success: {num_success} succeeded, {num_failed} failed."
            self.status_label.setStyleSheet("color: orange;")
        elif num_failed > 0 and num_success == 0:
            final_message = f"All {num_failed} compressions failed."
            self.status_label.setStyleSheet("color: red;")
        else:
            final_message = "Compression process finished."
            self.status_label.setStyleSheet("color: white;")
        self.status_label.setText(final_message)
        self.worker = None
        self.compress_button.setEnabled(True)
        self.select_button.setEnabled(True)

    def _handle_compression_error(self, error_message):
        self.status_label.setText(f"Critical Error: {error_message}")
        self.status_label.setStyleSheet("color: red;")
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Compression Error", error_message)
        self.worker = None
        self.compress_button.setEnabled(True)
        self.select_button.setEnabled(True)
