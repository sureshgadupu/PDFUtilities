import os
from PyQt6.QtCore import QThread, pyqtSignal
from converter import convert_multiple_pdfs_to_docx # Ensure converter.py is in the same directory or accessible via PYTHONPATH

class ConversionWorker(QThread):
    progress = pyqtSignal(int) # Percentage progress (0-100)
    status_update = pyqtSignal(str) # For individual file status messages
    finished = pyqtSignal(list, list) # (successful_messages, failed_messages)
    error = pyqtSignal(str) # For critical errors in the thread itself

    def __init__(self, pdf_files, output_directory, parent=None):
        super().__init__(parent)
        self.pdf_files = pdf_files
        self.output_directory = output_directory
        self._is_running = True

    def run(self):
        try:
            self._is_running = True
            # Define callbacks for the converter module
            def progress_reporter(current_value, max_value):
                if not self._is_running: return
                if max_value > 0:
                    percentage = int((current_value / max_value) * 100)
                    self.progress.emit(percentage)
                else:
                    self.progress.emit(0)

            def status_reporter(message):
                if not self._is_running: return
                self.status_update.emit(message)
            
            if not self.pdf_files: # Check moved here to avoid issues if run with no files
                status_reporter("No files selected for conversion.")
                self.finished.emit([],[])
                return
            
            if not os.path.exists(self.output_directory):
                try:
                    os.makedirs(self.output_directory)
                    status_reporter(f"Created output directory: {self.output_directory}")
                except OSError as e:
                    status_reporter(f"Error creating output directory {self.output_directory}: {e}")
                    self.error.emit(f"Failed to create output directory: {e}")
                    self.finished.emit([], [f"Failed to create output directory: {e}"])
                    return

            successful_messages, failed_messages = convert_multiple_pdfs_to_docx(
                self.pdf_files,
                self.output_directory,
                progress_callback=progress_reporter,
                status_callback=status_reporter
            )
            if self._is_running:
                self.finished.emit(successful_messages, failed_messages)

        except Exception as e:
            if self._is_running:
                self.error.emit(f"Critical error in conversion worker: {str(e)}")
        finally:
            self._is_running = False

    def stop(self):
        self._is_running = False 