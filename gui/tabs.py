from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QSpinBox, QCheckBox, QProgressBar, QPushButton, QMessageBox, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from .base_tab import BaseTab
from workers import ConversionWorker, CompressionWorker, MergeWorker, SplitWorker, ExtractWorker
import os

class ConvertTab(BaseTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None

    def add_files_to_table(self, file_paths):
        """Override to clear status when new files are added"""
        super().add_files_to_table(file_paths)
        self.status_label.setText("")
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

    def _start_conversion_process(self):
        """Start the PDF to DOCX conversion process"""
        pdf_files = self.get_selected_files()
        if not pdf_files:
            self.status_label.setText("Please select PDF files to convert.")
            return

        output_dir = self.get_output_directory()
        if not output_dir:
            self.status_label.setText("Please select an output directory.")
            return

        # Create and start worker
        self.worker = ConversionWorker(pdf_files, output_dir, parent=self)
        self.worker.progress.connect(self._update_progress)
        self.worker.status_update.connect(self._update_status)
        self.worker.finished.connect(self._handle_conversion_finished)
        self.worker.error.connect(self._handle_conversion_error)
        self.worker.start()

        # Update UI
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting conversion...")

    def _update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def _update_status(self, message):
        """Update status label"""
        self.status_label.setText(message)

    def _handle_conversion_finished(self, successful_messages, failed_messages):
        """Handle conversion completion"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if successful_messages and not failed_messages:
            self.status_label.setText("Conversion completed successfully!")
        elif successful_messages and failed_messages:
            self.status_label.setText(f"Conversion completed with {len(failed_messages)} errors.")
        else:
            self.status_label.setText("Conversion failed.")

    def _handle_conversion_error(self, error_message):
        """Handle conversion error"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Error: {error_message}")

    def stop_active_conversion(self):
        """Stop any active conversion process"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
            self.start_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
            self.status_label.setText("Conversion stopped.")

class CompressTab(BaseTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_compress_ui()
        self.worker = None
        self.generated_files = []  # Track generated files

    def _setup_compress_ui(self):
        # Add compress-specific controls
        compress_layout = QVBoxLayout()
        
        # Compression Level
        level_layout = QHBoxLayout()
        level_label = QLabel("Compression Level:")
        level_label.setStyleSheet("color: #000;")
        self.level_combo = QComboBox()
        self.level_combo.setStyleSheet("color: #000;")
        self.level_combo.addItems(["High", "Medium", "Low"])
        self.level_combo.setCurrentText("Medium")
        level_layout.addWidget(level_label)
        level_layout.addWidget(self.level_combo)
        level_layout.addStretch()
        compress_layout.addLayout(level_layout)

        # Target File Size
        target_layout = QHBoxLayout()
        target_label = QLabel("Target file size:")
        target_label.setStyleSheet("color: #000;")
        self.target_size_input = QLineEdit()
        self.target_size_input.setPlaceholderText("Enter target size...")
        self.target_size_input.setStyleSheet("""
            QLineEdit {
                color: #000;
                background: #fff;
                border: 1px solid #b2e0f7;
                border-radius: 4px;
                padding: 4px 8px;
                max-width: 130px;
            }
        """)
        self.target_size_combo = QComboBox()
        self.target_size_combo.setStyleSheet("color: #000;")
        self.target_size_combo.addItems(["KB", "MB"])
        self.target_size_combo.setCurrentText("KB")
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_size_input)
        target_layout.addWidget(self.target_size_combo)
        target_layout.addStretch()
        compress_layout.addLayout(target_layout)

        # Add compress-specific layout after the table
        self.layout().addLayout(compress_layout)

    def add_files_to_table(self, file_paths):
        """Override to clear status when new files are added"""
        super().add_files_to_table(file_paths)
        self.status_label.setText("")
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.generated_files = []  # Clear tracked files

    def _start_compression(self):
        """Start the PDF compression process"""
        pdf_files = self.get_selected_files()
        if not pdf_files:
            self.status_label.setText("Please select PDF files to compress.")
            return

        output_dir = self.get_output_directory()
        if not output_dir:
            self.status_label.setText("Please select an output directory.")
            return

        # Get compression settings
        compression_mode = self.level_combo.currentText().lower()
        
        # Get target size if specified
        target_size_kb = None
        target_size_text = self.target_size_input.text().strip()
        if target_size_text:
            try:
                target_size = float(target_size_text)
                if self.target_size_combo.currentText() == "MB":
                    target_size *= 1024  # Convert MB to KB
                target_size_kb = int(target_size)
            except ValueError:
                self.status_label.setText("Invalid target size value.")
                return
        
        # Create and start worker
        self.worker = CompressionWorker(
            pdf_files, 
            output_dir, 
            compression_mode=compression_mode,
            target_size_kb=target_size_kb,
            parent=self
        )
        self.worker.progress.connect(self._update_progress)
        self.worker.status_update.connect(self._update_status)
        self.worker.finished.connect(self._handle_compression_finished)
        self.worker.error.connect(self._handle_compression_error)
        self.worker.start()

        # Update UI
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting compression...")
        self.generated_files = []  # Reset tracked files

    def _update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def _update_status(self, message):
        """Update status label"""
        self.status_label.setText(message)
        # Track generated files from status messages
        if "Saved compressed file:" in message:
            file_path = message.split("Saved compressed file:")[1].strip()
            self.generated_files.append(file_path)

    def _handle_compression_finished(self, successful_messages, failed_messages):
        """Handle compression completion"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if successful_messages and not failed_messages:
            self.status_label.setText("Compression completed successfully!")
        elif successful_messages and failed_messages:
            self.status_label.setText(f"Compression completed with {len(failed_messages)} errors.")
            self._cleanup_generated_files()  # Clean up on partial failure
        else:
            self.status_label.setText("Compression failed.")
            self._cleanup_generated_files()  # Clean up on complete failure

    def _handle_compression_error(self, error_message):
        """Handle compression error"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Error: {error_message}")
        self._cleanup_generated_files()  # Clean up on error

    def _cleanup_generated_files(self):
        """Remove any generated files if compression failed"""
        for file_path in self.generated_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error removing file {file_path}: {str(e)}")
        self.generated_files = []

class MergeTab(BaseTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None

    def add_files_to_table(self, file_paths):
        """Override to clear status when new files are added"""
        super().add_files_to_table(file_paths)
        self.status_label.setText("")
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

    def _start_merge(self):
        """Start the PDF merging process"""
        pdf_files = self.get_selected_files()
        if not pdf_files:
            self.status_label.setText("Please select PDF files to merge.")
            return

        if len(pdf_files) < 2:
            self.status_label.setText("Please select at least 2 PDF files to merge.")
            return

        output_dir = self.get_output_directory()
        if not output_dir:
            self.status_label.setText("Please select an output directory.")
            return

        # Get first filename and create merged filename
        first_file = os.path.basename(pdf_files[0])
        base_name = os.path.splitext(first_file)[0]
        output_file = os.path.join(output_dir, f"{base_name}_merged.pdf")
        
        # Create and start worker
        self.worker = MergeWorker(pdf_files, output_file, parent=self)
        self.worker.progress.connect(self._update_progress)
        self.worker.status_update.connect(self._update_status)
        self.worker.finished.connect(self._handle_merge_finished)
        self.worker.error.connect(self._handle_merge_error)
        self.worker.start()

        # Update UI
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting merge...")

    def _update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def _update_status(self, message):
        """Update status label"""
        self.status_label.setText(message)

    def _handle_merge_finished(self, success):
        """Handle merge completion"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText("PDFs merged successfully!")
        else:
            self.status_label.setText("Merge failed.")

    def _handle_merge_error(self, error_message):
        """Handle merge error"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Error: {error_message}")

class SplitTab(BaseTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_split_ui()
        self.worker = None

    def _setup_split_ui(self):
        # Add split-specific controls
        split_layout = QVBoxLayout()
        
        # Split Mode and Range Input in same row
        mode_layout = QHBoxLayout()
        
        # Split Mode
        mode_label = QLabel("Split Mode:")
        mode_label.setStyleSheet("color: #000;")
        self.mode_combo = QComboBox()
        self.mode_combo.setStyleSheet("color: #000;")
        self.mode_combo.addItems(["Every Page", "Custom Range", "Size Based"])
        self.mode_combo.setCurrentText("Every Page")
        self.mode_combo.currentTextChanged.connect(self._on_split_mode_changed)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)

        # Add some spacing between mode and range
        mode_layout.addSpacing(20)

        # Custom Range Input
        range_label = QLabel("Page Range:")
        range_label.setStyleSheet("color: #000;")
        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("e.g., 1,3,5-7,9")
        self.range_input.setStyleSheet("""
            QLineEdit {
                color: #000;
                background: #fff;
                border: 1px solid #b2e0f7;
                border-radius: 4px;
                padding: 4px 8px;
                max-width: 200px;
            }
        """)
        mode_layout.addWidget(range_label)
        mode_layout.addWidget(self.range_input)
        mode_layout.addStretch()

        # Add the combined layout
        split_layout.addLayout(mode_layout)

        # Add split-specific layout after the table
        self.layout().addLayout(split_layout)

        # Initially hide range input
        range_label.setVisible(False)
        self.range_input.setVisible(False)

    def _on_split_mode_changed(self, mode):
        """Show/hide range input based on selected mode"""
        is_custom_range = mode == "Custom Range"
        # Find and update visibility of range label and input
        for widget in self.findChildren(QLabel):
            if widget.text() == "Page Range:":
                widget.setVisible(is_custom_range)
        for widget in self.findChildren(QLineEdit):
            if widget.placeholderText() == "e.g., 1,3,5-7,9":
                widget.setVisible(is_custom_range)

    def _parse_page_ranges(self, range_str):
        """Parse comma-separated page ranges into a list of page numbers"""
        try:
            pages = []
            ranges = range_str.replace(" ", "").split(",")
            
            for r in ranges:
                if "-" in r:
                    start, end = map(int, r.split("-"))
                    if start > end:
                        raise ValueError("Invalid range: start > end")
                    pages.extend(range(start, end + 1))
                else:
                    pages.append(int(r))
            
            return sorted(set(pages))  # Remove duplicates and sort
        except ValueError as e:
            raise ValueError(f"Invalid page range format: {str(e)}")

    def _start_split(self):
        """Start the PDF splitting process"""
        pdf_files = self.get_selected_files()
        if not pdf_files:
            self.status_label.setText("Please select PDF files to split.")
            return

        output_dir = self.get_output_directory()
        if not output_dir:
            self.status_label.setText("Please select an output directory.")
            return

        # Get split mode and validate custom range if needed
        split_mode = self.mode_combo.currentText()
        page_ranges = None
        
        if split_mode == "Custom Range":
            range_str = self.range_input.text().strip()
            if not range_str:
                self.status_label.setText("Please enter page ranges.")
                return
            try:
                page_ranges = self._parse_page_ranges(range_str)
                if not page_ranges:
                    self.status_label.setText("No valid page numbers found.")
                    return
            except ValueError as e:
                self.status_label.setText(f"Invalid page range: {str(e)}")
                return
        
        # Create and start worker
        self.worker = SplitWorker(
            pdf_files=pdf_files,
            output_directory=output_dir,
            split_mode=split_mode,
            page_ranges=page_ranges,
            parent=self
        )
        self.worker.progress.connect(self._update_progress)
        self.worker.status_update.connect(self._update_status)
        self.worker.finished.connect(self._handle_split_finished)
        self.worker.error.connect(self._handle_split_error)
        self.worker.start()

        # Update UI
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting split...")

    def _update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def _update_status(self, message):
        """Update status label"""
        self.status_label.setText(message)

    def _handle_split_finished(self, success):
        """Handle split completion"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        if success:
            self.status_label.setText("PDF files have been split successfully.")
        else:
            self.status_label.setText("Some files could not be split.")

    def _handle_split_error(self, error_message):
        """Handle split error"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Error: {error_message}")

    def add_files_to_table(self, file_paths):
        """Override to clear status when new files are added"""
        super().add_files_to_table(file_paths)
        self.status_label.setText("")
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        if self.mode_combo.currentText() == "Custom Range":
            self.range_input.clear()

class ExtractTab(BaseTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_extract_ui()
        self.worker = None

    def _setup_extract_ui(self):
        # Add extract-specific controls
        extract_layout = QVBoxLayout()
        
        # Extract Mode
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Extract Mode:")
        mode_label.setStyleSheet("color: #000;")
        self.mode_combo = QComboBox()
        self.mode_combo.setStyleSheet("color: #000;")
        self.mode_combo.addItems(["Text Only", "Text with Images", "Images Only"])
        self.mode_combo.setCurrentText("Text Only")
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        extract_layout.addLayout(mode_layout)

        # Page Range
        range_layout = QHBoxLayout()
        range_label = QLabel("Page Range:")
        range_label.setStyleSheet("color: #000;")
        self.range_combo = QComboBox()
        self.range_combo.setStyleSheet("color: #000;")
        self.range_combo.addItems(["All Pages", "Custom Range"])
        self.range_combo.setCurrentText("All Pages")
        range_layout.addWidget(range_label)
        range_layout.addWidget(self.range_combo)
        range_layout.addStretch()
        extract_layout.addLayout(range_layout)

        # Add extract-specific layout after the table
        self.layout().addLayout(extract_layout)

    def _start_extract(self):
        """Start the PDF extraction process"""
        pdf_files = self.get_selected_files()
        if not pdf_files:
            QMessageBox.warning(self, "No Files", "Please select PDF files to extract from.")
            return

        output_dir = self.get_output_directory()
        if not output_dir:
            QMessageBox.warning(self, "No Output Directory", "Please select an output directory.")
            return

        # Get extraction settings
        extract_mode = self.mode_combo.currentText()
        page_range = self.range_combo.currentText()
        
        # Create and start worker
        self.worker = ExtractWorker(pdf_files, output_dir, extract_mode, page_range, parent=self)
        self.worker.progress.connect(self._update_progress)
        self.worker.status_update.connect(self._update_status)
        self.worker.finished.connect(self._handle_extract_finished)
        self.worker.error.connect(self._handle_extract_error)
        self.worker.start()

        # Update UI
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

    def _update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def _update_status(self, message):
        """Update status label"""
        self.status_label.setText(message)

    def _handle_extract_finished(self, success):
        """Handle extraction completion"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        if success:
            QMessageBox.information(self, "Success", "Content has been extracted successfully.")
        else:
            QMessageBox.warning(self, "Error", "Some files could not be processed.")

    def _handle_extract_error(self, error_message):
        """Handle extraction error"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}") 