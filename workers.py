import os
from PyQt6.QtCore import QThread, pyqtSignal
from converter import convert_multiple_pdfs_to_docx # Ensure converter.py is in the same directory or accessible via PYTHONPATH
from compressor import compress_multiple_pdfs # New import for compression
import fitz  # PyMuPDF

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

class CompressionWorker(QThread):
    progress = pyqtSignal(int)
    status_update = pyqtSignal(str)
    finished = pyqtSignal(list, list)  # (successes, failures)
    error = pyqtSignal(str)

    def __init__(self, pdf_files, output_directory, compression_mode="medium", target_size_kb=None, parent=None):
        super().__init__(parent)
        self.pdf_files = pdf_files
        self.output_directory = output_directory
        self.compression_mode = compression_mode
        self.target_size_kb = target_size_kb
        self._is_running = True

    def run(self):
        try:
            self._is_running = True
            def progress_reporter(current, total):
                if not self._is_running: return
                percent = int((current / total) * 100) if total > 0 else 0
                self.progress.emit(percent)
            def status_reporter(msg):
                if not self._is_running: return
                self.status_update.emit(msg)
            if not self.pdf_files:
                status_reporter("No files selected for compression.")
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
            successes, failures = compress_multiple_pdfs(
                self.pdf_files,
                self.output_directory,
                compression_mode=self.compression_mode,
                target_size_kb=self.target_size_kb,
                progress_callback=progress_reporter,
                status_callback=status_reporter
            )
            if self._is_running:
                self.finished.emit(successes, failures)
        except Exception as e:
            if self._is_running:
                self.error.emit(f"Critical error in compression worker: {str(e)}")
        finally:
            self._is_running = False

    def stop(self):
        self._is_running = False

class MergeWorker(QThread):
    progress = pyqtSignal(int)
    status_update = pyqtSignal(str)
    finished = pyqtSignal(bool)
    error = pyqtSignal(str)

    def __init__(self, pdf_files, output_file, parent=None):
        super().__init__(parent)
        self.pdf_files = pdf_files
        self.output_file = output_file

    def run(self):
        try:
            total_files = len(self.pdf_files)
            if total_files < 2:
                self.error.emit("At least 2 PDF files are required for merging.")
                return

            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(self.output_file)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                self.status_update.emit(f"Created output directory: {output_dir}")

            # Create a new PDF document
            merged_pdf = fitz.open()
            
            # Process each PDF file
            for i, pdf_file in enumerate(self.pdf_files):
                try:
                    self.status_update.emit(f"Processing {os.path.basename(pdf_file)}...")
                    pdf_document = fitz.open(pdf_file)
                    
                    # Insert all pages from the current PDF
                    merged_pdf.insert_pdf(pdf_document)
                    pdf_document.close()
                    
                    # Update progress
                    progress = int((i + 1) / total_files * 100)
                    self.progress.emit(progress)
                    
                except Exception as e:
                    self.error.emit(f"Error processing {os.path.basename(pdf_file)}: {str(e)}")
                    return

            # Save the merged PDF
            self.status_update.emit("Saving merged PDF...")
            merged_pdf.save(self.output_file)
            merged_pdf.close()

            self.status_update.emit(f"Merged PDF saved to: {self.output_file}")
            self.finished.emit(True)

        except Exception as e:
            self.error.emit(f"Error during merge: {str(e)}")
            self.finished.emit(False) 