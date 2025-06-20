from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QSpinBox, QCheckBox, QProgressBar, QPushButton, QMessageBox, QLineEdit, QTableWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from PyQt6.QtGui import QKeySequence, QShortcut
from .base_tab import BaseTab
from workers import ConversionWorker, CompressionWorker, MergeWorker, SplitWorker, ExtractWorker, ConvertToImageWorker, ExtractTextWorker
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
        self._install_shortcuts()
        # Disable sorting permanently for merge tab since order matters
        self.file_table.setSortingEnabled(False)

    def _install_shortcuts(self):
        shortcut_up = QShortcut(QKeySequence('Ctrl+Up'), self)
        shortcut_down = QShortcut(QKeySequence('Ctrl+Down'), self)
        shortcut_up.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        shortcut_down.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        shortcut_up.activated.connect(self._move_selected_up)
        shortcut_down.activated.connect(self._move_selected_down)

    def _move_selected_up(self):
        selected = self.file_table.selectionModel().selectedRows()
        if len(selected) != 1:
            return
        row = selected[0].row()
        if row == 0:
            return
        self._swap_rows(row, row - 1)
        self.file_table.clearSelection()
        self.file_table.selectRow(row - 1)

    def _move_selected_down(self):
        selected = self.file_table.selectionModel().selectedRows()
        if len(selected) != 1:
            return
        row = selected[0].row()
        if row >= self.file_table.rowCount() - 1:
            return
        self._swap_rows(row, row + 1)
        self.file_table.clearSelection()
        self.file_table.selectRow(row + 1)

    def _swap_rows(self, row1, row2):
        self.file_table.blockSignals(True)

        for col in range(self.file_table.columnCount()):
            # Take items from both rows
            item1 = self.file_table.takeItem(row1, col)
            item2 = self.file_table.takeItem(row2, col)
            
            # Set items in swapped positions
            self.file_table.setItem(row1, col, item2)
            self.file_table.setItem(row2, col, item1)

        self.file_table.blockSignals(False)
        self.file_table.viewport().update()

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
        self.range_combo.currentTextChanged.connect(self._on_range_mode_changed)
        range_layout.addWidget(range_label)
        range_layout.addWidget(self.range_combo)
        range_layout.addStretch()
        extract_layout.addLayout(range_layout)

        # Custom Range Input
        custom_range_layout = QHBoxLayout()
        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("e.g., 1,3,5-7,9")
        self.range_input.setStyleSheet("color: #000;")
        self.range_input.setVisible(False)
        custom_range_layout.addWidget(self.range_input)
        custom_range_layout.addStretch()
        extract_layout.addLayout(custom_range_layout)

        # Add extract-specific layout after the table
        self.layout().addLayout(extract_layout)

    def _on_range_mode_changed(self, mode):
        """Show/hide range input based on selected mode"""
        is_custom_range = mode == "Custom Range"
        self.range_input.setVisible(is_custom_range)
        if not is_custom_range:
            self.range_input.clear()

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
        
        # Handle custom page range
        page_ranges = None
        if page_range == "Custom Range":
            range_str = self.range_input.text().strip()
            if not range_str:
                QMessageBox.warning(self, "Invalid Range", "Please enter page ranges.")
                return
            try:
                page_ranges = self._parse_page_ranges(range_str)
                if not page_ranges:
                    QMessageBox.warning(self, "Invalid Range", "No valid page numbers found.")
                    return
            except ValueError as e:
                QMessageBox.warning(self, "Invalid Range", str(e))
                return
        
        # Create and start worker
        self.worker = ExtractWorker(
            pdf_files=pdf_files,
            output_directory=output_dir,
            extract_mode=extract_mode,
            page_range=page_range,
            page_ranges=page_ranges,
            parent=self
        )
        self.worker.progress.connect(self._update_progress)
        self.worker.status_update.connect(self._update_status)
        self.worker.finished.connect(self._handle_extract_finished)
        self.worker.error.connect(self._handle_extract_error)
        self.worker.start()

        # Update UI
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting extraction...")

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
            self.status_label.setText("Extraction completed successfully!")
        else:
            self.status_label.setText("Extraction completed with errors. Check the status messages above.")

    def _handle_extract_error(self, error_message):
        """Handle extraction error"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Error: {error_message}")

    def add_files_to_table(self, file_paths):
        """Override to clear status when new files are added"""
        super().add_files_to_table(file_paths)
        self.status_label.setText("")
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        if self.range_combo.currentText() == "Custom Range":
            self.range_input.clear()

class ConvertToImageTab(BaseTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_convert_to_image_ui()
        self.worker = None

    def _setup_convert_to_image_ui(self):
        # Add convert to image specific controls
        convert_layout = QVBoxLayout()
        
        # Image Format and DPI in a single row
        format_dpi_layout = QHBoxLayout()
        
        # Image Format
        format_layout = QHBoxLayout()
        format_label = QLabel("Image Format:")
        format_label.setStyleSheet("color: #000;")
        self.format_combo = QComboBox()
        self.format_combo.setStyleSheet("color: #000;")
        self.format_combo.addItems(["PNG", "JPEG"])
        self.format_combo.setCurrentText("PNG")
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        format_dpi_layout.addLayout(format_layout)
        
        # Add some space between format and DPI
        format_dpi_layout.addSpacing(20)
        
        # DPI Setting
        dpi_layout = QHBoxLayout()
        dpi_label = QLabel("DPI:")
        dpi_label.setStyleSheet("color: #000;")
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setStyleSheet("color: #000;")
        self.dpi_spin.setRange(72, 600)
        self.dpi_spin.setValue(100)
        dpi_layout.addWidget(dpi_label)
        dpi_layout.addWidget(self.dpi_spin)
        format_dpi_layout.addLayout(dpi_layout)
        
        format_dpi_layout.addStretch()
        convert_layout.addLayout(format_dpi_layout)

        # Image Result Type and Color Type in a single row
        result_color_layout = QHBoxLayout()
        
        # Image Result Type
        result_type_layout = QHBoxLayout()
        result_type_label = QLabel("Image Result Type:")
        result_type_label.setStyleSheet("color: #000;")
        self.result_type_combo = QComboBox()
        self.result_type_combo.setStyleSheet("color: #000;")
        self.result_type_combo.addItems(["Multiple Images", "Single Big Image"])
        result_type_layout.addWidget(result_type_label)
        result_type_layout.addWidget(self.result_type_combo)
        result_color_layout.addLayout(result_type_layout)
        
        # Add some space between result type and color type
        result_color_layout.addSpacing(20)
        
        # Color Type
        color_type_layout = QHBoxLayout()
        color_type_label = QLabel("Color Type:")
        color_type_label.setStyleSheet("color: #000;")
        self.color_type_combo = QComboBox()
        self.color_type_combo.setStyleSheet("color: #000;")
        self.color_type_combo.addItems(["Color", "Gray Scale"])
        color_type_layout.addWidget(color_type_label)
        color_type_layout.addWidget(self.color_type_combo)
        result_color_layout.addLayout(color_type_layout)
        
        result_color_layout.addStretch()
        convert_layout.addLayout(result_color_layout)

        # Add convert-specific layout after the table
        self.layout().addLayout(convert_layout)

    def _start_convert_to_image(self):
        """Start the PDF to image conversion process"""
        pdf_files = self.get_selected_files()
        if not pdf_files:
            QMessageBox.warning(self, "No Files", "Please select PDF files to convert.")
            return

        output_dir = self.get_output_directory()
        if not output_dir:
            QMessageBox.warning(self, "No Output Directory", "Please select an output directory.")
            return

        # Get conversion settings
        image_format = self.format_combo.currentText().lower()
        dpi = self.dpi_spin.value()
        result_type = self.result_type_combo.currentText()
        color_type = self.color_type_combo.currentText()
        
        # Create and start worker
        self.worker = ConvertToImageWorker(
            pdf_files=pdf_files,
            output_directory=output_dir,
            image_format=image_format,
            dpi=dpi,
            result_type=result_type,
            color_type=color_type,
            parent=self
        )
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

    def _handle_conversion_finished(self, success):
        """Handle conversion completion"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        if success:
            self.status_label.setText("Conversion completed successfully!")
        else:
            self.status_label.setText("Conversion completed with errors. Check the status messages above.")

    def _handle_conversion_error(self, error_message):
        """Handle conversion error"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Error: {error_message}")

    def add_files_to_table(self, file_paths):
        """Override to clear status when new files are added"""
        super().add_files_to_table(file_paths)
        self.status_label.setText("")
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0) 

class ExtractTextTab(BaseTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_extract_text_ui()
        self.worker = None

    def _setup_extract_text_ui(self):
        # Add extract text specific controls
        extract_layout = QVBoxLayout()
        
        # Mode selection
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Extraction Mode:")
        mode_label.setStyleSheet("color: #000;")
        self.mode_combo = QComboBox()
        self.mode_combo.setStyleSheet("color: #000;")
        self.mode_combo.addItems(["All Pages", "Selected Pages", "Page Range"])
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        extract_layout.addLayout(mode_layout)
        
        # Page range input
        range_layout = QHBoxLayout()
        range_label = QLabel("Page Range:")
        range_label.setStyleSheet("color: #000;")
        self.page_range = QLineEdit()
        self.page_range.setStyleSheet("color: #000;")
        self.page_range.setPlaceholderText("e.g., 1-3,5,7-9")
        self.page_range.setEnabled(False)
        range_layout.addWidget(range_label)
        range_layout.addWidget(self.page_range)
        range_layout.addStretch()
        extract_layout.addLayout(range_layout)
        
        # Output format
        format_layout = QHBoxLayout()
        format_label = QLabel("Output Format:")
        format_label.setStyleSheet("color: #000;")
        self.format_combo = QComboBox()
        self.format_combo.setStyleSheet("color: #000;")
        self.format_combo.addItems(["Text", "Word"])
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        extract_layout.addLayout(format_layout)
        
        # Add extract-specific layout after the table
        self.layout().addLayout(extract_layout)

    def on_mode_changed(self, index):
        self.page_range.setEnabled(index == 2)  # Enable only for "Page Range" mode

    def _start_extract_text(self):
        """Start the text extraction process"""
        pdf_files = self.get_selected_files()
        if not pdf_files:
            self.status_label.setText("Please select PDF files to extract text from.")
            return

        output_dir = self.get_output_directory()
        if not output_dir:
            self.status_label.setText("Please select an output directory.")
            return

        # Get extraction options
        mode = self.mode_combo.currentText()
        page_range = self.page_range.text() if mode == "Page Range" else None
        output_format = self.format_combo.currentText().lower()
        
        # Create and start worker
        self.worker = ExtractTextWorker(
            pdf_files=pdf_files,
            output_directory=output_dir,
            mode=mode,
            page_range=page_range,
            output_format=output_format,
            parent=self
        )
        self.worker.progress.connect(self._update_progress)
        self.worker.status_update.connect(self._update_status)
        self.worker.finished.connect(self._handle_extraction_finished)
        self.worker.error.connect(self._handle_extraction_error)
        self.worker.start()

        # Update UI
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting extraction...")

    def _update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def _update_status(self, message):
        """Update status label"""
        self.status_label.setText(message)

    def _handle_extraction_finished(self, success):
        """Handle extraction completion"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        if success:
            self.status_label.setText("Extraction completed successfully!")
        else:
            self.status_label.setText("Extraction completed with errors. Check the status messages above.")

    def _handle_extraction_error(self, error_message):
        """Handle extraction error"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Error: {error_message}")

    def add_files_to_table(self, file_paths):
        """Override to clear status when new files are added"""
        super().add_files_to_table(file_paths)
        self.status_label.setText("")
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0) 