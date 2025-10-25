import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
    QFileDialog,
)

from workers import (
    CompressionWorker,
    ConversionWorker,
    ConvertToImageWorker,
    ExtractTextWorker,
    ExtractWorker,
    MergeWorker,
    PasswordRemovalWorker,
    SplitWorker,
)

from .base_tab import BaseTab


class ConvertTab(BaseTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        # Add output folder controls at the end
        self.add_output_folder_controls()

    def add_files_to_table(self, file_paths):
        """Override to clear status when new files are added"""
        super().add_files_to_table(file_paths)
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

    def _start_conversion_process(self):
        """Start the PDF to DOCX conversion process"""
        pdf_files = self.get_selected_files()
        if not pdf_files:
            self.show_notification("Please select PDF files to convert.", "error", duration=2000)
            return

        output_dir = self.get_output_directory()
        if not output_dir:
            self.show_notification("Please select an output directory.", "error", duration=2000)
            return

        # Get passwords for the files
        passwords = self.get_file_passwords()

        # Create and start worker
        self.worker = ConversionWorker(pdf_files, output_dir, passwords=passwords, parent=self)
        self.worker.progress.connect(self._update_progress)
        self.worker.status_update.connect(self.show_notification)
        self.worker.finished.connect(self._handle_conversion_finished)
        self.worker.error.connect(self._handle_conversion_error)
        self.worker.start()

        # Update UI
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.show_notification("Starting conversion...", "info")

    def _update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def _handle_conversion_finished(self, successful_messages, failed_messages):
        """Handle conversion completion"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if successful_messages:
            self.show_notification(f"Conversion completed! {len(successful_messages)} file(s) converted successfully.", "success", duration=3000)
        
        if failed_messages:
            self.show_notification(f"Conversion failed for {len(failed_messages)} file(s). Check console for details.", "error", duration=3000)

    def _handle_conversion_error(self, error_message):
        """Handle conversion error"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.show_notification(f"Conversion error: {error_message}", "error", duration=3000)

    def stop_active_conversion(self):
        """Stop active conversion worker"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()


class PasswordRemovalTab(BaseTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_password_removal_ui()
        self.worker = None
        # Add output folder controls at the end
        self.add_output_folder_controls()

    def _setup_password_removal_ui(self):
        """Setup password removal specific controls"""
        # Add password removal specific controls
        password_layout = QVBoxLayout()
        password_layout.setSpacing(6)

        # Information label
        info_label = QLabel("Remove password protection from PDF files. Unlocked files will be saved with '_unlocked' suffix.")
        info_label.setStyleSheet("color: #000; font-size: 12px; padding: 8px; background: #f0f8ff; border: 1px solid #b2e0f7; border-radius: 4px;")
        info_label.setWordWrap(True)
        password_layout.addWidget(info_label)

        # Add password removal specific controls to the dedicated container
        self.add_tab_controls(password_layout)

    def add_files_to_table(self, file_paths):
        """Override to clear status when new files are added"""
        super().add_files_to_table(file_paths)
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

    def _start_password_removal(self):
        """Start the password removal process"""
        pdf_files = self.get_selected_files()
        if not pdf_files:
            self.show_notification("Please select PDF files to remove passwords from.", "error", duration=2000)
            return

        output_dir = self.get_output_directory()
        if not output_dir:
            self.show_notification("Please select an output directory.", "error", duration=2000)
            return

        # Get passwords for the files
        passwords = self.get_file_passwords()
        
        # Check which files are actually password-protected and require passwords
        missing_passwords = []
        for file_path in pdf_files:
            # Check if the PDF is password-protected
            try:
                from password_remover import is_pdf_password_protected
                if is_pdf_password_protected(file_path):
                    # Only require password if the file is actually password-protected
                    if file_path not in passwords or not passwords[file_path]:
                        missing_passwords.append(os.path.basename(file_path))
            except Exception as e:
                # If we can't check, assume it might be protected and require password
                if file_path not in passwords or not passwords[file_path]:
                    missing_passwords.append(os.path.basename(file_path))
        
        if missing_passwords:
            self.show_notification(f"Please provide passwords for encrypted files: {', '.join(missing_passwords)}", "error", duration=3000)
            return

        # Create and start worker
        self.worker = PasswordRemovalWorker(pdf_files, output_dir, passwords=passwords, parent=self)
        self.worker.progress.connect(self._update_progress)
        self.worker.status_update.connect(self.show_notification)
        self.worker.finished.connect(self._handle_password_removal_finished)
        self.worker.error.connect(self._handle_password_removal_error)
        self.worker.start()

        # Update UI
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.show_notification("Starting password removal...", "info")

    def _update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def _update_status(self, message):
        """Update status label"""
        self.show_notification(message, "info")

    def _handle_password_removal_finished(self, successful_messages, failed_messages):
        """Handle password removal completion"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        if successful_messages and not failed_messages:
            self.show_notification("Password removal completed successfully!", "success")
        elif successful_messages and failed_messages:
            self.show_notification(f"Password removal completed with {len(failed_messages)} errors.", "warning", duration=2000)
        else:
            self.show_notification("Password removal failed.", "error", duration=2000)

    def _handle_password_removal_error(self, error_message):
        """Handle password removal error"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.show_notification(f"Error: {error_message}", "error", duration=2000)


class CompressTab(BaseTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_compress_ui()
        self.worker = None
        self.generated_files = []  # Track generated files

    def _setup_compress_ui(self):
        # Add compress-specific controls
        compress_layout = QVBoxLayout()
        compress_layout.setSpacing(6)

        # Compression Level
        level_layout = QHBoxLayout()
        level_label = QLabel("Compression Level:")
        level_label.setStyleSheet("color: #000;")
        self.level_combo = QComboBox()
        self.level_combo.setStyleSheet("color: #000;")
        self.level_combo.addItems(["Smallest (Low Quality)", "Balanced (Medium Quality)", "Largest (High Quality)"])
        self.level_combo.setCurrentText("Balanced (Medium Quality)")
        self.level_combo.setToolTip(
            "Smallest: Maximum compression, smallest file size, lowest quality\n"
            "Balanced: Medium compression and quality\n"
            "Largest: Minimum compression, largest file size, highest quality"
        )
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
        self.target_size_input.setStyleSheet(
            """
            QLineEdit {
                color: #000;
                background: #fff;
                border: 1px solid #b2e0f7;
                border-radius: 4px;
                padding: 4px 8px;
                max-width: 130px;
            }
        """
        )
        self.target_size_combo = QComboBox()
        self.target_size_combo.setStyleSheet("color: #000;")
        self.target_size_combo.addItems(["KB", "MB"])
        self.target_size_combo.setCurrentText("KB")
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_size_input)
        target_layout.addWidget(self.target_size_combo)
        target_layout.addStretch()
        compress_layout.addLayout(target_layout)

        # Add compress-specific controls to the dedicated container
        self.add_tab_controls(compress_layout)
        
        # Add output folder controls at the end
        self.add_output_folder_controls()

    def add_files_to_table(self, file_paths):
        """Override to clear status when new files are added"""
        super().add_files_to_table(file_paths)
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

    def _start_compression(self):
        """Start the PDF compression process"""
        pdf_files = self.get_selected_files()
        if not pdf_files:
            self.show_notification("Please select PDF files to compress.", "error", duration=2000)
            return

        output_dir = self.get_output_directory()
        if not output_dir:
            self.show_notification("Please select an output directory.", "error", duration=2000)
            return

        # Get compression settings
        compression_level = self.level_combo.currentText()
        if compression_level == "Smallest (Low Quality)":
            compression_mode = "low"  # /screen
        elif compression_level == "Balanced (Medium Quality)":
            compression_mode = "medium"  # /ebook
        else:  # "Largest (High Quality)"
            compression_mode = "high"  # /printer

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
                self.show_notification("Invalid target size value.", "error", duration=2000)
                return

        # Get passwords for the files
        passwords = self.get_file_passwords()
        
        # Create and start worker
        self.worker = CompressionWorker(
            pdf_files, output_dir, compression_mode=compression_mode, target_size_kb=target_size_kb, passwords=passwords, parent=self
        )
        self.worker.progress.connect(self._update_progress)
        self.worker.status_update.connect(self.show_notification)
        self.worker.finished.connect(self._handle_compression_finished)
        self.worker.error.connect(self._handle_compression_error)
        self.worker.start()

        # Update UI
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.show_notification("Starting compression...", "info")
        self.generated_files = []  # Reset tracked files

    def _update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def _update_status(self, message):
        """Update status label"""
        self.show_notification(message, "info")
        # Track generated files from status messages
        if "Saved compressed file:" in message:
            file_path = message.split("Saved compressed file:")[1].strip()
            self.generated_files.append(file_path)

    def _handle_compression_finished(self, successful_messages, failed_messages):
        """Handle compression completion"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        if successful_messages and not failed_messages:
            self.show_notification("Compression completed successfully!", "success")
        elif successful_messages and failed_messages:
            # Check if failures are actual failures or just target size not achieved
            actual_failures = [msg for msg in failed_messages if "Failed to compress file" in msg]
            if actual_failures:
                self.show_notification(f"Compression completed with {len(actual_failures)} errors.", "warning", duration=2000)
                self._cleanup_generated_files()  # Clean up on actual failures
            else:
                # All "failures" are just target size not achieved, but files were compressed
                self.show_notification("Compression completed! Some files could not reach target size.", "warning", duration=2000)
        else:
            self.show_notification("Compression failed.", "error", duration=2000)
            self._cleanup_generated_files()  # Clean up on complete failure

    def _handle_compression_error(self, error_message):
        """Handle compression error"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.show_notification(f"Error: {error_message}", "error", duration=2000)
        
        # Only clean up on critical errors, not on target size issues
        if "target size" not in error_message.lower():
            self._cleanup_generated_files()

    def _cleanup_generated_files(self):
        """Remove any generated files if compression failed"""
        for file_path in self.generated_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                # Log error but continue with cleanup
                pass
        self.generated_files = []


class MergeTab(BaseTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self._install_shortcuts()
        # Disable sorting permanently for merge tab since order matters
        if self.main_window and hasattr(self.main_window, 'shared_file_table'):
            self.main_window.shared_file_table.setSortingEnabled(False)
        # Add output folder controls at the end
        self.add_output_folder_controls()

    def _install_shortcuts(self):
        shortcut_up = QShortcut(QKeySequence("Ctrl+Up"), self)
        shortcut_down = QShortcut(QKeySequence("Ctrl+Down"), self)
        shortcut_up.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        shortcut_down.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        shortcut_up.activated.connect(self._move_selected_up)
        shortcut_down.activated.connect(self._move_selected_down)

    def _move_selected_up(self):
        if not self.main_window or not hasattr(self.main_window, 'shared_file_table'):
            return
        table = self.main_window.shared_file_table
        selected = table.selectionModel().selectedRows()
        if len(selected) != 1:
            return
        row = selected[0].row()
        if row == 0:
            return
        self._swap_rows(row, row - 1)
        table.clearSelection()
        table.selectRow(row - 1)

    def _move_selected_down(self):
        if not self.main_window or not hasattr(self.main_window, 'shared_file_table'):
            return
        table = self.main_window.shared_file_table
        selected = table.selectionModel().selectedRows()
        if len(selected) != 1:
            return
        row = selected[0].row()
        if row >= table.rowCount() - 1:
            return
        self._swap_rows(row, row + 1)
        table.clearSelection()
        table.selectRow(row + 1)

    def _swap_rows(self, row1, row2):
        if not self.main_window or not hasattr(self.main_window, 'shared_file_table'):
            return
        table = self.main_window.shared_file_table
        table.blockSignals(True)

        for col in range(table.columnCount()):
            # Take items from both rows
            item1 = table.takeItem(row1, col)
            item2 = table.takeItem(row2, col)

            # Set items in swapped positions
            table.setItem(row1, col, item2)
            table.setItem(row2, col, item1)

        table.blockSignals(False)
        table.viewport().update()

    def add_files_to_table(self, file_paths):
        """Override to clear status when new files are added"""
        super().add_files_to_table(file_paths)
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

    def _start_merge(self):
        """Start the PDF merge process"""
        pdf_files = self.get_selected_files()
        if not pdf_files:
            self.show_notification("Please select PDF files to merge.", "error", duration=2000)
            return

        if len(pdf_files) < 2:
            self.show_notification("Please select at least 2 PDF files to merge.", "error", duration=2000)
            return

        output_dir = self.get_output_directory()
        if not output_dir:
            self.show_notification("Please select an output directory.", "error", duration=2000)
            return

        # Let user choose output filename
        output_filename, _ = QFileDialog.getSaveFileName(
            self, "Save Merged PDF", os.path.join(output_dir, "merged_document.pdf"), "PDF Files (*.pdf)"
        )
        if not output_filename:
            return

        # Get passwords for the files
        passwords = self.get_file_passwords()
        
        # Create and start worker
        self.worker = MergeWorker(pdf_files, output_filename, passwords=passwords, parent=self)
        self.worker.progress.connect(self._update_progress)
        self.worker.status_update.connect(self.show_notification)
        self.worker.finished.connect(self._handle_merge_finished)
        self.worker.error.connect(self._handle_merge_error)
        self.worker.start()

        # Update UI
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.show_notification("Starting merge...", "info")

    def _update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def _update_status(self, message):
        """Update status label"""
        self.show_notification(message, "info")

    def _handle_merge_finished(self, success):
        """Handle merge completion"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        if success:
            self.show_notification("PDFs merged successfully!", "success")
        else:
            self.show_notification("Merge failed.", "error", duration=2000)

    def _handle_merge_error(self, error_message):
        """Handle merge error"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.show_notification(f"Error: {error_message}", "error", duration=2000)


class SplitTab(BaseTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_split_ui()
        self.worker = None

    def _setup_split_ui(self):
        # Add split-specific controls
        split_layout = QVBoxLayout()
        split_layout.setSpacing(6)

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
        self.range_input.setStyleSheet(
            """
            QLineEdit {
                color: #000;
                background: #fff;
                border: 1px solid #b2e0f7;
                border-radius: 4px;
                padding: 4px 8px;
                max-width: 200px;
            }
        """
        )
        mode_layout.addWidget(range_label)
        mode_layout.addWidget(self.range_input)
        mode_layout.addStretch()

        # Add the combined layout
        split_layout.addLayout(mode_layout)

        # Add split-specific controls to the dedicated container
        self.add_tab_controls(split_layout)
        
        # Add output folder controls at the end
        self.add_output_folder_controls()

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
        """Start the PDF split process"""
        pdf_files = self.get_selected_files()
        if not pdf_files:
            self.show_notification("Please select PDF files to split.", "error", duration=2000)
            return

        output_dir = self.get_output_directory()
        if not output_dir:
            self.show_notification("Please select an output directory.", "error", duration=2000)
            return

        split_mode = self.mode_combo.currentText()
        page_ranges = []

        if split_mode == "Custom Range":
            range_str = self.range_input.text().strip()
            if not range_str:
                self.show_notification("Please enter page ranges.", "error", duration=2000)
                return
            try:
                page_ranges = self._parse_page_ranges(range_str)
                if not page_ranges:
                    self.show_notification("No valid page numbers found.", "error", duration=2000)
                    return
            except ValueError as e:
                self.show_notification(f"Invalid page range: {str(e)}", "error", duration=2000)
                return

        # Get passwords for the files
        passwords = self.get_file_passwords()
        
        # Create and start worker
        self.worker = SplitWorker(
            pdf_files=pdf_files, output_directory=output_dir, split_mode=split_mode, page_ranges=page_ranges, passwords=passwords, parent=self
        )
        self.worker.progress.connect(self._update_progress)
        self.worker.status_update.connect(self.show_notification)
        self.worker.finished.connect(self._handle_split_finished)
        self.worker.error.connect(self._handle_split_error)
        self.worker.start()

        # Update UI
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.show_notification("Starting split...", "info")

    def _update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def _update_status(self, message):
        """Update status label"""
        self.show_notification(message, "info")

    def _handle_split_finished(self, success):
        """Handle split completion"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        if success:
            self.show_notification("PDF files have been split successfully.", "success")
        else:
            self.show_notification("Some files could not be split.", "error", duration=2000)

    def _handle_split_error(self, error_message):
        """Handle split error"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.show_notification(f"Error: {error_message}", "error", duration=2000)

    def add_files_to_table(self, file_paths):
        """Override to clear status when new files are added"""
        super().add_files_to_table(file_paths)
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)


class ExtractTab(BaseTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_extract_ui()
        self.worker = None

    def _setup_extract_ui(self):
        # Add extract-specific controls
        extract_layout = QVBoxLayout()
        extract_layout.setSpacing(6)

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

        # Add extract-specific controls to the dedicated container
        self.add_tab_controls(extract_layout)
        
        # Add output folder controls at the end
        self.add_output_folder_controls()

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
            self.show_notification("Please select PDF files to extract text from.", "error", duration=2000)
            return

        output_dir = self.get_output_directory()
        if not output_dir:
            self.show_notification("Please select an output directory.", "error", duration=2000)
            return

        # Get extraction settings
        extract_mode = self.mode_combo.currentText()
        page_range = self.range_combo.currentText()

        # Handle custom page range
        page_ranges = None
        if page_range == "Custom Range":
            range_str = self.range_input.text().strip()
            if not range_str:
                self.show_notification("Please enter page ranges.", "error", duration=2000)
                return
            try:
                page_ranges = self._parse_page_ranges(range_str)
                if not page_ranges:
                    self.show_notification("No valid page numbers found.", "error", duration=2000)
                    return
            except ValueError as e:
                self.show_notification(f"Invalid page range: {str(e)}", "error", duration=2000)
                return

        # Get passwords for the files
        passwords = self.get_file_passwords()
        
        # Create and start worker
        self.worker = ExtractWorker(
            pdf_files=pdf_files,
            output_directory=output_dir,
            extract_mode=extract_mode,
            page_range=page_range,
            page_ranges=page_ranges,
            passwords=passwords,
            parent=self,
        )
        self.worker.progress.connect(self._update_progress)
        self.worker.status_update.connect(self.show_notification)
        self.worker.finished.connect(self._handle_extract_finished)
        self.worker.error.connect(self._handle_extract_error)
        self.worker.start()

        # Update UI
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.show_notification("Starting extraction...", "info")

    def _update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def _update_status(self, message):
        """Update status label"""
        self.show_notification(message, "info")

    def _handle_extract_finished(self, success):
        """Handle extraction completion"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        if success:
            self.show_notification("Extraction completed successfully!", "success")
        else:
            self.show_notification("Extraction completed with errors. Check the status messages above.", "error", duration=2000)

    def _handle_extract_error(self, error_message):
        """Handle extraction error"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.show_notification(f"Error: {error_message}", "error", duration=2000)

    def add_files_to_table(self, file_paths):
        """Override to clear status when new files are added"""
        super().add_files_to_table(file_paths)
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)


class ConvertToImageTab(BaseTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_convert_to_image_ui()
        self.worker = None
        # Connect the start button to the conversion method
        self.start_btn.clicked.connect(self._start_convert_to_image)

    def _setup_convert_to_image_ui(self):
        # Add convert to image specific controls
        convert_layout = QVBoxLayout()
        convert_layout.setSpacing(6)

        # Image Format and DPI in a single row
        format_dpi_layout = QHBoxLayout()

        # Image Format
        format_layout = QHBoxLayout()
        format_label = QLabel("Image Format:")
        format_label.setStyleSheet("color: #000; font-weight: bold;")
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
        result_type_label.setStyleSheet("color: #000; font-weight: bold;")
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

        # Add convert-specific controls to the dedicated container
        self.add_tab_controls(convert_layout)
        
        # Add output folder controls at the end
        self.add_output_folder_controls()

    def _start_convert_to_image(self):
        """Start the PDF to image conversion process"""
        pdf_files = self.get_selected_files()
        if not pdf_files:
            self.show_notification("Please select PDF files to convert.", "error", duration=2000)
            return

        output_dir = self.get_output_directory()
        if not output_dir:
            self.show_notification("Please select an output directory.", "error", duration=2000)
            return

        # Get settings
        image_format = self.format_combo.currentText().lower()
        dpi = self.dpi_spin.value()
        result_type = self.result_type_combo.currentText()
        color_type = self.color_type_combo.currentText()

        # Get passwords for the files
        passwords = self.get_file_passwords()
        
        # Create and start worker
        self.worker = ConvertToImageWorker(
            pdf_files=pdf_files,
            output_directory=output_dir,
            image_format=image_format,
            dpi=dpi,
            result_type=result_type,
            color_type=color_type,
            passwords=passwords,
            parent=self,
        )
        self.worker.progress.connect(self._update_progress)
        self.worker.status_update.connect(self.show_notification)
        self.worker.finished.connect(self._handle_conversion_finished)
        self.worker.error.connect(self._handle_conversion_error)
        self.worker.start()

        # Update UI
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.show_notification("Starting conversion...", "info")

    def _update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def _update_status(self, message):
        """Update status label"""
        self.show_notification(message, "info")

    def _handle_conversion_finished(self, success):
        """Handle conversion completion"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        if success:
            self.show_notification("Conversion completed successfully!", "success")
        else:
            self.show_notification("Conversion completed with errors. Check the status messages above.", "error", duration=2000)

    def _handle_conversion_error(self, error_message):
        """Handle conversion error"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.show_notification(f"Error: {error_message}", "error", duration=2000)

    def add_files_to_table(self, file_paths):
        """Override to clear status when new files are added"""
        super().add_files_to_table(file_paths)
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
        extract_layout.setSpacing(6)

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

        # Add extract-specific controls to the dedicated container
        self.add_tab_controls(extract_layout)
        
        # Add output folder controls at the end
        self.add_output_folder_controls()

    def on_mode_changed(self, index):
        self.page_range.setEnabled(index == 2)  # Enable only for "Page Range" mode

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

    def _start_extract_text(self):
        """Start the text extraction process"""
        pdf_files = self.get_selected_files()
        if not pdf_files:
            self.show_notification("Please select PDF files to extract text from.", "error", duration=2000)
            return

        output_dir = self.get_output_directory()
        if not output_dir:
            self.show_notification("Please select an output directory.", "error", duration=2000)
            return

        # Get settings
        mode_index = self.mode_combo.currentIndex()
        if mode_index == 0:  # All Pages
            mode = "all"
            page_range = None
        elif mode_index == 1:  # Selected Pages
            mode = "selected"
            page_range = None
        else:  # Page Range
            mode = "range"
            range_str = self.page_range.text().strip()
            if not range_str:
                self.show_notification("Please enter page ranges.", "error", duration=2000)
                return
            try:
                page_range = self._parse_page_ranges(range_str)
                if not page_range:
                    self.show_notification("No valid page numbers found.", "error", duration=2000)
                    return
            except ValueError as e:
                self.show_notification(f"Invalid page range: {str(e)}", "error", duration=2000)
                return

        output_format = self.format_combo.currentText().lower()

        # Get passwords for the files
        passwords = self.get_file_passwords()
        
        # Create and start worker
        self.worker = ExtractTextWorker(
            pdf_files=pdf_files,
            output_directory=output_dir,
            mode=mode,
            page_range=page_range,
            output_format=output_format,
            passwords=passwords,
            parent=self,
        )
        self.worker.progress.connect(self._update_progress)
        self.worker.status_update.connect(self.show_notification)
        self.worker.finished.connect(self._handle_extraction_finished)
        self.worker.error.connect(self._handle_extraction_error)
        self.worker.start()

        # Update UI
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.show_notification("Starting extraction...", "info")

    def _update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def _update_status(self, message):
        """Update status label"""
        self.show_notification(message, "info")

    def _handle_extraction_finished(self, success):
        """Handle extraction completion"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        if success:
            self.show_notification("Extraction completed successfully!", "success")
        else:
            self.show_notification("Extraction completed with errors. Check the status messages above.", "error", duration=2000)

    def _handle_extraction_error(self, error_message):
        """Handle extraction error"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.show_notification(f"Error: {error_message}", "error", duration=2000)

    def add_files_to_table(self, file_paths):
        """Override to clear status when new files are added"""
        super().add_files_to_table(file_paths)
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
