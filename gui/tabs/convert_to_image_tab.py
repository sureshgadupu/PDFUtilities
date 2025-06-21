from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from workers import ConvertToImageWorker


class ConvertToImageTab(QWidget):
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

        # Image options
        options_group = QGroupBox("Image Options")
        options_layout = QVBoxLayout()

        # Format selection and DPI in a single row
        format_dpi_layout = QHBoxLayout()

        # Image Format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Image Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG"])
        format_layout.addWidget(self.format_combo)
        format_dpi_layout.addLayout(format_layout)

        # Add some space between format and DPI
        format_dpi_layout.addSpacing(20)

        # DPI settings
        dpi_layout = QHBoxLayout()
        dpi_layout.addWidget(QLabel("DPI:"))
        self.dpi_combo = QComboBox()
        self.dpi_combo.addItems(["72", "100", "150", "300", "600"])
        self.dpi_combo.setCurrentText("100")
        dpi_layout.addWidget(self.dpi_combo)
        format_dpi_layout.addLayout(dpi_layout)

        options_layout.addLayout(format_dpi_layout)

        # Image Result Type and Color Type in a single row
        result_color_layout = QHBoxLayout()

        # Image Result Type
        result_type_layout = QHBoxLayout()
        result_type_layout.addWidget(QLabel("Image Result Type:"))
        self.result_type_combo = QComboBox()
        self.result_type_combo.addItems(["Multiple Images", "Single Big Image"])
        result_type_layout.addWidget(self.result_type_combo)
        result_color_layout.addLayout(result_type_layout)

        # Add some space between result type and color type
        result_color_layout.addSpacing(20)

        # Color Type
        color_type_layout = QHBoxLayout()
        color_type_layout.addWidget(QLabel("Color Type:"))
        self.color_type_combo = QComboBox()
        self.color_type_combo.addItems(["Color", "Gray Scale"])
        color_type_layout.addWidget(self.color_type_combo)
        result_color_layout.addLayout(color_type_layout)

        options_layout.addLayout(result_color_layout)

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

        # Convert button
        self.convert_btn = QPushButton("Convert to Image")
        self.convert_btn.clicked.connect(self.start_conversion)
        self.convert_btn.setEnabled(False)

        # Add all groups to main layout
        layout.addWidget(file_group)
        layout.addWidget(options_group)
        layout.addWidget(dir_group)
        layout.addWidget(progress_group)
        layout.addWidget(self.convert_btn)

        self.setLayout(layout)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files", "", "PDF Files (*.pdf)")
        if files:
            self.file_list.addItems(files)
            self.update_convert_button()

    def remove_files(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))
        self.update_convert_button()

    def clear_files(self):
        self.file_list.clear()
        self.update_convert_button()

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory", "")
        if directory:
            self.output_directory = directory
            self.dir_label.setText(directory)
            self.update_convert_button()

    def update_convert_button(self):
        self.convert_btn.setEnabled(self.file_list.count() > 0 and self.output_directory is not None)

    def start_conversion(self):
        if not self.file_list.count() or not self.output_directory:
            return

        # Get selected files
        pdf_files = [self.file_list.item(i).text() for i in range(self.file_list.count())]

        # Get conversion options
        image_format = self.format_combo.currentText().lower()
        dpi = int(self.dpi_combo.currentText())
        result_type = self.result_type_combo.currentText()
        color_type = self.color_type_combo.currentText()

        # Create and start worker
        self.worker = ConvertToImageWorker(pdf_files, self.output_directory, image_format, dpi, result_type, color_type)

        # Connect signals
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.status_update.connect(self.status_label.setText)
        self.worker.finished.connect(self.on_conversion_finished)
        self.worker.error.connect(self.on_error)

        # Update UI
        self.convert_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting conversion...")

        # Start worker
        self.worker.start()

    def on_conversion_finished(self, success):
        self.convert_btn.setEnabled(True)
        if success:
            self.status_label.setText("Conversion completed successfully!")
        else:
            self.status_label.setText("Conversion completed with errors. Check the status messages above.")

    def on_error(self, message):
        self.status_label.setText(f"Error: {message}")
