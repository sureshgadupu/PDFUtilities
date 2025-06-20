from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QProgressBar, QFileDialog, QListWidget,
    QGroupBox, QComboBox, QLineEdit
)
from PyQt6.QtCore import Qt
from workers import ExtractTextWorker

class ExtractTextTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.worker = None
        self.output_directory = None

    def init_ui(self):
        layout = QVBoxLayout()
        
        # File selection
        file_group = QGroupBox("PDF Files")
        file_layout = QVBoxLayout()
        
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.ExtendedSelection)
        file_layout.addWidget(self.file_list)
        
        file_buttons = QHBoxLayout()
        self.add_file_btn = QPushButton("Add Files")
        self.add_file_btn.clicked.connect(self.add_files)
        self.remove_file_btn = QPushButton("Remove Selected")
        self.remove_file_btn.clicked.connect(self.remove_files)
        self.clear_files_btn = QPushButton("Clear All")
        self.clear_files_btn.clicked.connect(self.clear_files)
        
        file_buttons.addWidget(self.add_file_btn)
        file_buttons.addWidget(self.remove_file_btn)
        file_buttons.addWidget(self.clear_files_btn)
        file_layout.addLayout(file_buttons)
        file_group.setLayout(file_layout)
        
        # Extraction options
        options_group = QGroupBox("Extraction Options")
        options_layout = QVBoxLayout()
        
        # Mode selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Extraction Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["All Pages", "Selected Pages", "Page Range"])
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        options_layout.addLayout(mode_layout)
        
        # Page range input
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("Page Range:"))
        self.page_range = QLineEdit()
        self.page_range.setPlaceholderText("e.g., 1-3,5,7-9")
        self.page_range.setEnabled(False)
        range_layout.addWidget(self.page_range)
        options_layout.addLayout(range_layout)
        
        # Output format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Output Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Text", "Word"])
        format_layout.addWidget(self.format_combo)
        options_layout.addLayout(format_layout)
        
        options_group.setLayout(options_layout)
        
        # Output directory
        dir_group = QGroupBox("Output Directory")
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel("No directory selected")
        self.dir_label.setStyleSheet("color: #666;")
        self.select_dir_btn = QPushButton("Select Directory")
        self.select_dir_btn.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.dir_label)
        dir_layout.addWidget(self.select_dir_btn)
        dir_group.setLayout(dir_layout)
        
        # Progress
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666;")
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        progress_group.setLayout(progress_layout)
        
        # Extract button
        self.extract_btn = QPushButton("Extract Text")
        self.extract_btn.clicked.connect(self.start_extraction)
        self.extract_btn.setEnabled(False)
        
        # Add all groups to main layout
        layout.addWidget(file_group)
        layout.addWidget(options_group)
        layout.addWidget(dir_group)
        layout.addWidget(progress_group)
        layout.addWidget(self.extract_btn)
        
        self.setLayout(layout)

    def on_mode_changed(self, index):
        self.page_range.setEnabled(index == 2)  # Enable only for "Page Range" mode

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PDF Files",
            "",
            "PDF Files (*.pdf)"
        )
        if files:
            self.file_list.addItems(files)
            self.update_extract_button()

    def remove_files(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))
        self.update_extract_button()

    def clear_files(self):
        self.file_list.clear()
        self.update_extract_button()

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            ""
        )
        if directory:
            self.output_directory = directory
            self.dir_label.setText(directory)
            self.update_extract_button()

    def update_extract_button(self):
        self.extract_btn.setEnabled(
            self.file_list.count() > 0 and
            self.output_directory is not None
        )

    def start_extraction(self):
        if not self.file_list.count() or not self.output_directory:
            return

        # Get selected files
        pdf_files = [
            self.file_list.item(i).text()
            for i in range(self.file_list.count())
        ]

        # Get extraction options
        mode = self.mode_combo.currentText()
        page_range = self.page_range.text() if mode == "Page Range" else None
        output_format = self.format_combo.currentText().lower()

        # Create and start worker
        self.worker = ExtractTextWorker(
            pdf_files,
            self.output_directory,
            mode,
            page_range,
            output_format
        )
        
        # Connect signals
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.status_update.connect(self.status_label.setText)
        self.worker.finished.connect(self.on_extraction_finished)
        self.worker.error.connect(self.on_error)
        
        # Update UI
        self.extract_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting extraction...")
        
        # Start worker
        self.worker.start()

    def on_extraction_finished(self, success):
        self.extract_btn.setEnabled(True)
        if success:
            self.status_label.setText("Extraction completed successfully!")
        else:
            self.status_label.setText("Extraction completed with errors. Check the status messages above.")

    def on_error(self, message):
        self.status_label.setText(f"Error: {message}") 