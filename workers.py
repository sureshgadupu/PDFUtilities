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

class SplitWorker(QThread):
    progress = pyqtSignal(int)
    status_update = pyqtSignal(str)
    finished = pyqtSignal(bool)
    error = pyqtSignal(str)

    def __init__(self, pdf_files, output_directory, split_mode, page_ranges=None, parent=None):
        super().__init__(parent)
        self.pdf_files = pdf_files
        self.output_directory = output_directory
        self.split_mode = split_mode
        self.page_ranges = page_ranges
        self._is_running = True

    def run(self):
        try:
            self._is_running = True
            total_files = len(self.pdf_files)
            success = True  # Track overall success
            
            for i, pdf_file in enumerate(self.pdf_files):
                if not self._is_running:
                    break

                try:
                    self.status_update.emit(f"Processing {os.path.basename(pdf_file)}...")
                    doc = fitz.open(pdf_file)
                    total_pages = len(doc)

                    if self.split_mode == "Every Page":
                        # Split each page into a separate PDF
                        for page_num in range(total_pages):
                            if not self._is_running:
                                break
                            new_doc = fitz.open()
                            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                            output_file = os.path.join(
                                self.output_directory,
                                f"{os.path.splitext(os.path.basename(pdf_file))[0]}_page_{page_num + 1}.pdf"
                            )
                            new_doc.save(output_file)
                            new_doc.close()
                            self.status_update.emit(f"Created page {page_num + 1} of {total_pages}")

                    elif self.split_mode == "Custom Range":
                        if not self.page_ranges:
                            self.error.emit("No page ranges specified")
                            success = False
                            continue
                            
                        # Validate all page numbers first
                        invalid_pages = [p for p in self.page_ranges if p > total_pages]
                        if invalid_pages:
                            self.error.emit(f"Invalid page numbers: {', '.join(map(str, invalid_pages))}. Document has only {total_pages} pages.")
                            success = False
                            continue
                            
                        # Create a new PDF for each range
                        for range_idx, page_num in enumerate(self.page_ranges):
                            if not self._is_running:
                                break
                                
                            new_doc = fitz.open()
                            new_doc.insert_pdf(doc, from_page=page_num-1, to_page=page_num-1)  # Convert to 0-based index
                            output_file = os.path.join(
                                self.output_directory,
                                f"{os.path.splitext(os.path.basename(pdf_file))[0]}_page_{page_num}.pdf"
                            )
                            new_doc.save(output_file)
                            new_doc.close()
                            self.status_update.emit(f"Created page {page_num}")

                    elif self.split_mode == "Size Based":
                        # Split into parts of approximately equal size
                        target_size = 5 * 1024 * 1024  # 5MB target size
                        current_size = 0
                        current_part = 1
                        new_doc = fitz.open()
                        
                        for page_num in range(total_pages):
                            if not self._is_running:
                                break
                            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                            # Save to temporary file to check size
                            temp_file = os.path.join(self.output_directory, "temp.pdf")
                            new_doc.save(temp_file)
                            current_size = os.path.getsize(temp_file)
                            
                            if current_size >= target_size:
                                output_file = os.path.join(
                                    self.output_directory,
                                    f"{os.path.splitext(os.path.basename(pdf_file))[0]}_part{current_part}.pdf"
                                )
                                new_doc.save(output_file)
                                new_doc.close()
                                new_doc = fitz.open()
                                current_size = 0
                                current_part += 1
                                self.status_update.emit(f"Created part {current_part - 1}")
                        
                        # Save remaining pages
                        if new_doc.page_count > 0:
                            output_file = os.path.join(
                                self.output_directory,
                                f"{os.path.splitext(os.path.basename(pdf_file))[0]}_part{current_part}.pdf"
                            )
                            new_doc.save(output_file)
                            new_doc.close()
                        
                        # Clean up temp file
                        if os.path.exists(temp_file):
                            os.remove(temp_file)

                    doc.close()
                    progress = int((i + 1) / total_files * 100)
                    self.progress.emit(progress)

                except Exception as e:
                    self.error.emit(f"Error processing {os.path.basename(pdf_file)}: {str(e)}")
                    success = False
                    continue

            if self._is_running:
                self.finished.emit(success)

        except Exception as e:
            if self._is_running:
                self.error.emit(f"Critical error in split worker: {str(e)}")
                self.finished.emit(False)
        finally:
            self._is_running = False

    def stop(self):
        self._is_running = False

class ExtractWorker(QThread):
    progress = pyqtSignal(int)
    status_update = pyqtSignal(str)
    finished = pyqtSignal(bool)
    error = pyqtSignal(str)

    def __init__(self, pdf_files, output_directory, extract_mode, page_range, parent=None):
        super().__init__(parent)
        self.pdf_files = pdf_files
        self.output_directory = output_directory
        self.extract_mode = extract_mode
        self.page_range = page_range
        self._is_running = True

    def run(self):
        try:
            self._is_running = True
            total_files = len(self.pdf_files)
            
            for i, pdf_file in enumerate(self.pdf_files):
                if not self._is_running:
                    break

                try:
                    self.status_update.emit(f"Processing {os.path.basename(pdf_file)}...")
                    doc = fitz.open(pdf_file)
                    total_pages = len(doc)

                    # Determine page range
                    if self.page_range == "All Pages":
                        start_page = 0
                        end_page = total_pages - 1
                    else:
                        # For custom range, use first and last page for now
                        # TODO: Add UI for custom page range input
                        start_page = 0
                        end_page = total_pages - 1

                    # Create output directory for this file
                    file_base = os.path.splitext(os.path.basename(pdf_file))[0]
                    file_output_dir = os.path.join(self.output_directory, file_base)
                    os.makedirs(file_output_dir, exist_ok=True)

                    if self.extract_mode in ["Text Only", "Text with Images"]:
                        # Extract text
                        text_file = os.path.join(file_output_dir, "extracted_text.txt")
                        with open(text_file, "w", encoding="utf-8") as f:
                            for page_num in range(start_page, end_page + 1):
                                if not self._is_running:
                                    break
                                page = doc[page_num]
                                text = page.get_text()
                                f.write(f"\n--- Page {page_num + 1} ---\n")
                                f.write(text)
                                self.status_update.emit(f"Extracted text from page {page_num + 1}")

                    if self.extract_mode in ["Text with Images", "Images Only"]:
                        # Extract images
                        for page_num in range(start_page, end_page + 1):
                            if not self._is_running:
                                break
                            page = doc[page_num]
                            image_list = page.get_images()
                            
                            for img_index, img in enumerate(image_list):
                                if not self._is_running:
                                    break
                                xref = img[0]
                                base_image = doc.extract_image(xref)
                                image_bytes = base_image["image"]
                                
                                # Save image
                                image_filename = f"page_{page_num + 1}_image_{img_index + 1}.{base_image['ext']}"
                                image_path = os.path.join(file_output_dir, image_filename)
                                with open(image_path, "wb") as img_file:
                                    img_file.write(image_bytes)
                                self.status_update.emit(f"Extracted image {img_index + 1} from page {page_num + 1}")

                    doc.close()
                    progress = int((i + 1) / total_files * 100)
                    self.progress.emit(progress)

                except Exception as e:
                    self.error.emit(f"Error processing {os.path.basename(pdf_file)}: {str(e)}")
                    continue

            if self._is_running:
                self.finished.emit(True)

        except Exception as e:
            if self._is_running:
                self.error.emit(f"Critical error in extract worker: {str(e)}")
                self.finished.emit(False)
        finally:
            self._is_running = False

    def stop(self):
        self._is_running = False 