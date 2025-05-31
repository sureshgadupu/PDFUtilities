import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QProgressBar, QListWidgetItem, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QStandardPaths
from PyQt6.QtGui import QFont

from .custom_widgets import ToggleListWidget # Assuming custom_widgets.py is in the same gui directory
from workers import ConversionWorker # Assuming workers.py is in the parent directory

class ConvertTab(QWidget):
    # Optional: Signals to notify the main window if needed, though most logic will be internal.
    # conversion_process_started = pyqtSignal()
    # conversion_process_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None # To hold the conversion worker thread
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("PDF to DOCX Converter") # Corrected from title_label
        title_label.setFont(QFont('Arial', 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Styles for title, warning, etc. are kept from previous version
        title_label.setStyleSheet("""
            color: #000000;
            background-color: #f0f0f0;
            padding: 22px 0 16px 0;
            border-bottom: 1.5px solid #cccccc;
            border-radius: 8px 8px 0 0;
        """)
        layout.addWidget(title_label)

        # Warning
        warning_label = QLabel("Note: Image and graphic elements in PDFs may be lost or altered during conversion.")
        warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_label.setStyleSheet("""
            color: #505050;
            background: #fffbe7; /* Cream color for highlight */
            border: 1px solid #ffe0b2;
            border-radius: 6px;
            padding: 8px 0 8px 0;
            font-size: 14px;
            margin-bottom: 10px;
        """)
        layout.addWidget(warning_label)

        # File list using ToggleListWidget
        self.file_list_widget = ToggleListWidget() # Renamed from file_list for clarity
        self.file_list_widget.setSelectionMode(ToggleListWidget.SelectionMode.ExtendedSelection)
        self.file_list_widget.setStyleSheet("""
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
        """)
        self.file_list_widget.itemSelectionChanged.connect(self._update_button_states)
        layout.addWidget(self.file_list_widget)

        # Remove Selected button
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self._remove_selected_files)
        self.remove_button.setEnabled(False)
        layout.addWidget(self.remove_button)

        # Select and Convert buttons
        self.select_button = QPushButton("Select PDF Files")
        self.select_button.clicked.connect(self._select_files)
        layout.addWidget(self.select_button)

        self.convert_button = QPushButton("Convert to DOCX")
        self.convert_button.clicked.connect(self._start_conversion_process)
        self.convert_button.setEnabled(False)
        layout.addWidget(self.convert_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Select PDF files to begin.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout) # Set the layout for the QWidget
        self._apply_general_styles()

    def _apply_general_styles(self):
        # Styles for tab, buttons, progress bar, general labels are kept from previous version
        self.setStyleSheet("""
            ConvertTab { /* Target the widget itself for background */
                 background-color: #f3f4f6; /* Soft gray */
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
                color: #000000; /* Default for labels not specifically styled */
            }
        """)

    def _select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PDF Files",
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation),
            "PDF Files (*.pdf)"
        )
        if files:
            self.file_list_widget.clear()
            for f_path in files:
                item = QListWidgetItem(f_path)
                item.setToolTip(f_path) # Show full path on hover
                self.file_list_widget.addItem(item)
            self.status_label.setText(f"{len(files)} file(s) selected. Ready to convert.")
            self.status_label.setStyleSheet("color: black;")
        self._update_button_states()

    def _remove_selected_files(self):
        selected_items = self.file_list_widget.selectedItems()
        if not selected_items: return
        for item in selected_items:
            self.file_list_widget.takeItem(self.file_list_widget.row(item))
        
        if self.file_list_widget.count() == 0:
            self.status_label.setText("No files selected.")
        else:
            self.status_label.setText(f"{self.file_list_widget.count()} file(s) remaining.")
        self.status_label.setStyleSheet("color: black;")
        self._update_button_states()

    def _update_button_states(self):
        has_files = self.file_list_widget.count() > 0
        has_selection = len(self.file_list_widget.selectedItems()) > 0
        is_converting = self.worker is not None and self.worker.isRunning()

        self.select_button.setEnabled(not is_converting)
        self.convert_button.setEnabled(has_files and not is_converting)
        self.remove_button.setEnabled(has_selection and not is_converting)

    def _start_conversion_process(self):
        pdf_files = [self.file_list_widget.item(i).text() for i in range(self.file_list_widget.count())]
        if not pdf_files:
            self.status_label.setText("No files to convert. Please select PDF files first.")
            self.status_label.setStyleSheet("color: orange;")
            return

        output_dir_name = "ConvertedPDFs_from_App"
        documents_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        output_directory = os.path.join(documents_path, output_dir_name)

        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Initializing conversion...")
        self.status_label.setStyleSheet("color: black;")
        # if self.conversion_process_started:
        #     self.conversion_process_started.emit()

        self.worker = ConversionWorker(pdf_files, output_directory, self) # Pass self as parent
        self.worker.progress.connect(self._update_progress_bar)
        self.worker.status_update.connect(self._update_status_label)
        self.worker.finished.connect(self._handle_conversion_finished)
        self.worker.error.connect(self._handle_conversion_error)
        self.worker.start()
        self._update_button_states() # Disable buttons while worker is running

    def _update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def _update_status_label(self, message):
        self.status_label.setText(message)
        if "Error" in message or "Failed" in message:
            self.status_label.setStyleSheet("color: red;")
        elif "Successfully" in message or "Created output directory" in message : # also color green for directory creation
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setStyleSheet("color: black;")

    def _handle_conversion_finished(self, successful_messages, failed_messages):
        self.progress_bar.setValue(100)
        num_success = len(successful_messages)
        num_failed = len(failed_messages)

        if num_failed == 0 and num_success > 0:
            final_message = f"All {num_success} files converted successfully to: {self.worker.output_directory}"
            self.status_label.setStyleSheet("color: green;")
        elif num_success > 0 and num_failed > 0:
            final_message = f"Partial success: {num_success} succeeded, {num_failed} failed. Check: {self.worker.output_directory}"
            self.status_label.setStyleSheet("color: orange;")
        elif num_failed > 0 and num_success == 0:
            final_message = f"All {num_failed} conversions failed."
            # If output directory creation failed, it might be in failed_messages[0]
            if "Failed to create output directory" in failed_messages[0]:
                 final_message = failed_messages[0] # Show the more specific error from worker
            self.status_label.setStyleSheet("color: red;")
        elif num_success == 0 and num_failed == 0 and self.worker and self.worker.pdf_files: 
            final_message = "Conversion process completed, but no files were processed or an issue occurred."
            self.status_label.setStyleSheet("color: orange;")
        else: # No files were selected initially, or worker didn't run
            final_message = "Conversion process finished or was not started."
            self.status_label.setStyleSheet("color: black;")
            
        self.status_label.setText(final_message)
        QMessageBox.information(self, "Conversion Complete", final_message)

        self.worker = None # Clear the worker
        self._update_button_states() # Re-enable buttons
        # if self.conversion_process_finished:
        #     self.conversion_process_finished.emit()

    def _handle_conversion_error(self, error_message):
        self.status_label.setText(f"Critical Error: {error_message}")
        self.status_label.setStyleSheet("color: red;")
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Conversion Error", error_message)
        self.worker = None # Clear the worker
        self._update_button_states() # Re-enable buttons

    def stop_active_conversion(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop() # Tell the worker to stop
            # Optionally wait a bit for it to finish, or rely on signals
            self.status_label.setText("Conversion cancelled by user.")
            self.status_label.setStyleSheet("color: orange;")
            self.progress_bar.setVisible(False) # Or set to 0
            self.worker = None
            self._update_button_states() 