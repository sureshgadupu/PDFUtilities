import os

import fitz  # PyMuPDF
from PIL import Image
from PyQt6.QtCore import QThread, pyqtSignal

from compressor import compress_multiple_pdfs  # New import for compression
from converter import (  # Ensure converter.py is in the same directory or accessible via PYTHONPATH
    convert_multiple_pdfs_to_docx,
)


class ConversionWorker(QThread):
    progress = pyqtSignal(int)  # Percentage progress (0-100)
    status_update = pyqtSignal(str)  # For individual file status messages
    finished = pyqtSignal(list, list)  # (successful_messages, failed_messages)
    error = pyqtSignal(str)  # For critical errors in the thread itself

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
                if not self._is_running:
                    return
                if max_value > 0:
                    percentage = int((current_value / max_value) * 100)
                    self.progress.emit(percentage)
                else:
                    self.progress.emit(0)

            def status_reporter(message):
                if not self._is_running:
                    return
                self.status_update.emit(message)

            if not self.pdf_files:  # Check moved here to avoid issues if run with no files
                status_reporter("No files selected for conversion.")
                self.finished.emit([], [])
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
                self.pdf_files, self.output_directory, progress_callback=progress_reporter, status_callback=status_reporter
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
                if not self._is_running:
                    return
                percent = int((current / total) * 100) if total > 0 else 0
                self.progress.emit(percent)

            def status_reporter(msg):
                if not self._is_running:
                    return
                self.status_update.emit(msg)

            if not self.pdf_files:
                status_reporter("No files selected for compression.")
                self.finished.emit([], [])
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
                status_callback=status_reporter,
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
                    self.progress.emit(int((i + 1) / len(self.pdf_files) * 100))

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
            success = True

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
                                f"{os.path.splitext(os.path.basename(pdf_file))[0]}_page_{page_num + 1}.pdf",
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
                            self.error.emit(
                                f"Invalid page numbers: {', '.join(map(str, invalid_pages))}. "
                                f"Document has only {total_pages} pages."
                            )
                            success = False
                            continue

                        # Create a new PDF for each range
                        for range_idx, page_num in enumerate(self.page_ranges):
                            if not self._is_running:
                                break

                            new_doc = fitz.open()
                            new_doc.insert_pdf(doc, from_page=page_num - 1, to_page=page_num - 1)  # Convert to 0-based index
                            output_file = os.path.join(
                                self.output_directory, f"{os.path.splitext(os.path.basename(pdf_file))[0]}_page_{page_num}.pdf"
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
                                    f"{os.path.splitext(os.path.basename(pdf_file))[0]}_part{current_part}.pdf",
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
                                f"{os.path.splitext(os.path.basename(pdf_file))[0]}_part{current_part}.pdf",
                            )
                            new_doc.save(output_file)
                            new_doc.close()

                        # Clean up temp file
                        if os.path.exists(temp_file):
                            os.remove(temp_file)

                    doc.close()
                    self.progress.emit(int((i + 1) / len(self.pdf_files) * 100))

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

    def __init__(self, pdf_files, output_directory, extract_mode, page_range, page_ranges=None, parent=None):
        super().__init__(parent)
        self.pdf_files = pdf_files
        self.output_directory = output_directory
        self.extract_mode = extract_mode
        self.page_range = page_range
        self.page_ranges = page_ranges
        self._is_running = True

    def run(self):
        try:
            self._is_running = True

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
                        pages_to_process = range(start_page, end_page + 1)
                    else:  # Custom Range
                        if not self.page_ranges:
                            self.error.emit("No page ranges specified")
                            continue

                        # Validate all page numbers first
                        invalid_pages = [p for p in self.page_ranges if p > total_pages]
                        if invalid_pages:
                            self.error.emit(
                                f"Invalid page numbers: {', '.join(map(str, invalid_pages))}. "
                                f"Document has only {total_pages} pages."
                            )
                            continue

                        # Convert to 0-based index
                        pages_to_process = [p - 1 for p in self.page_ranges]

                    # Create output directory for this file
                    file_base = os.path.splitext(os.path.basename(pdf_file))[0]
                    file_output_dir = os.path.join(self.output_directory, file_base)
                    os.makedirs(file_output_dir, exist_ok=True)

                    if self.extract_mode in ["Text Only", "Text with Images"]:
                        # Extract text
                        text_file = os.path.join(file_output_dir, "extracted_text.txt")
                        with open(text_file, "w", encoding="utf-8") as f:
                            for page_num in pages_to_process:
                                if not self._is_running:
                                    break
                                page = doc[page_num]
                                text = page.get_text()
                                f.write(f"\n--- Page {page_num + 1} ---\n")
                                f.write(text)
                                self.status_update.emit(f"Extracted text from page {page_num + 1}")

                    if self.extract_mode in ["Text with Images", "Images Only"]:
                        # Extract images
                        for page_num in pages_to_process:
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
                    self.progress.emit(int((i + 1) / len(self.pdf_files) * 100))

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


class ConvertToImageWorker(QThread):
    progress = pyqtSignal(int)
    status_update = pyqtSignal(str)
    finished = pyqtSignal(bool)
    error = pyqtSignal(str)

    def __init__(self, pdf_files, output_directory, image_format, dpi, result_type, color_type, parent=None):
        super().__init__(parent)
        self.pdf_files = pdf_files
        self.output_directory = output_directory
        self.image_format = image_format
        self.dpi = dpi
        self.result_type = result_type
        self.color_type = color_type
        self._is_running = True

    def run(self):
        try:
            self._is_running = True
            success = True

            for i, pdf_file in enumerate(self.pdf_files):
                if not self._is_running:
                    break

                try:
                    self.status_update.emit(f"Processing {os.path.basename(pdf_file)}...")
                    doc = fitz.open(pdf_file)
                    total_pages = len(doc)

                    # Create output directory for this file
                    file_base = os.path.splitext(os.path.basename(pdf_file))[0]
                    file_output_dir = os.path.join(self.output_directory, file_base)
                    os.makedirs(file_output_dir, exist_ok=True)

                    # Log the output directory
                    self.status_update.emit(f"Output directory: {file_output_dir}")

                    # Determine colorspace based on color type
                    colorspace = "gray" if self.color_type == "Gray Scale" else "rgb"

                    if self.result_type == "Multiple Images":
                        # Convert each page to separate image
                        for page_num in range(total_pages):
                            if not self._is_running:
                                break

                            try:
                                page = doc[page_num]
                                # Calculate zoom factor based on DPI
                                zoom = self.dpi / 72  # 72 is the default DPI
                                matrix = fitz.Matrix(zoom, zoom)

                                # Get page pixmap with appropriate colorspace
                                pix = page.get_pixmap(
                                    matrix=matrix,
                                    alpha=False,  # No alpha channel for better compatibility
                                    colorspace=colorspace,
                                )

                                # Convert to PIL Image for better format handling
                                if self.color_type == "Gray Scale":
                                    img = Image.frombytes("L", [pix.width, pix.height], pix.samples)
                                else:
                                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                                # Save image
                                image_filename = f"page_{page_num + 1}.{self.image_format}"
                                image_path = os.path.join(file_output_dir, image_filename)

                                # Log the image path
                                self.status_update.emit(f"Saving image to: {image_path}")

                                if self.image_format == "jpeg":
                                    img.save(image_path, "JPEG", quality=85, optimize=True)
                                else:  # PNG
                                    img.save(image_path, "PNG", optimize=True)

                                # Verify file was created
                                if os.path.exists(image_path):
                                    self.status_update.emit(f"Successfully saved: {image_filename}")
                                else:
                                    self.error.emit(f"Failed to save image: {image_path}")
                                    success = False

                                self.status_update.emit(f"Converted page {page_num + 1} of {total_pages}")

                            except Exception as e:
                                self.error.emit(f"Error converting page {page_num + 1}: {str(e)}")
                                success = False
                                continue

                    else:  # Single Big Image
                        # Calculate total height for all pages
                        total_height = 0
                        page_widths = []

                        for page_num in range(total_pages):
                            page = doc[page_num]
                            zoom = self.dpi / 72
                            matrix = fitz.Matrix(zoom, zoom)
                            rect = page.rect
                            width = int(rect.width * zoom)
                            height = int(rect.height * zoom)
                            page_widths.append(width)
                            total_height += height

                        # Use the maximum width
                        max_width = max(page_widths)

                        # Create a large image to hold all pages
                        if self.color_type == "Gray Scale":
                            combined_img = Image.new("L", (max_width, total_height), 255)
                        else:
                            combined_img = Image.new("RGB", (max_width, total_height), (255, 255, 255))

                        current_y = 0

                        for page_num in range(total_pages):
                            if not self._is_running:
                                break

                            try:
                                page = doc[page_num]
                                zoom = self.dpi / 72
                                matrix = fitz.Matrix(zoom, zoom)

                                pix = page.get_pixmap(matrix=matrix, alpha=False, colorspace=colorspace)

                                if self.color_type == "Gray Scale":
                                    img = Image.frombytes("L", [pix.width, pix.height], pix.samples)
                                else:
                                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                                # Paste the page image into the combined image
                                combined_img.paste(img, (0, current_y))
                                current_y += img.height

                                self.status_update.emit(f"Processed page {page_num + 1} of {total_pages}")

                            except Exception as e:
                                self.error.emit(f"Error processing page {page_num + 1}: {str(e)}")
                                success = False
                                continue

                        # Save the combined image
                        image_filename = f"{file_base}_combined.{self.image_format}"
                        image_path = os.path.join(file_output_dir, image_filename)

                        self.status_update.emit(f"Saving combined image to: {image_path}")

                        if self.image_format == "jpeg":
                            combined_img.save(image_path, "JPEG", quality=85, optimize=True)
                        else:  # PNG
                            combined_img.save(image_path, "PNG", optimize=True)

                        if os.path.exists(image_path):
                            self.status_update.emit(f"Successfully saved combined image: {image_filename}")
                        else:
                            self.error.emit(f"Failed to save combined image: {image_path}")
                            success = False

                    doc.close()
                    self.progress.emit(int((i + 1) / len(self.pdf_files) * 100))

                except Exception as e:
                    self.error.emit(f"Error processing {os.path.basename(pdf_file)}: {str(e)}")
                    success = False
                    continue

            if self._is_running:
                self.finished.emit(success)

        except Exception as e:
            if self._is_running:
                self.error.emit(f"Critical error in convert to image worker: {str(e)}")
                self.finished.emit(False)
        finally:
            self._is_running = False

    def stop(self):
        self._is_running = False


class ExtractTextWorker(QThread):
    progress = pyqtSignal(int)
    status_update = pyqtSignal(str)
    finished = pyqtSignal(bool)
    error = pyqtSignal(str)

    def __init__(self, pdf_files, output_directory, mode, page_range, output_format, parent=None):
        super().__init__(parent)
        self.pdf_files = pdf_files
        self.output_directory = output_directory
        self.mode = mode
        self.page_range = page_range
        self.output_format = output_format
        self._is_running = True

    def run(self):
        try:
            self._is_running = True

            for i, pdf_file in enumerate(self.pdf_files):
                if not self._is_running:
                    break

                try:
                    self.status_update.emit(f"Processing {os.path.basename(pdf_file)}...")
                    doc = fitz.open(pdf_file)
                    total_pages = len(doc)

                    # Create output directory for this file
                    file_base = os.path.splitext(os.path.basename(pdf_file))[0]
                    file_output_dir = os.path.join(self.output_directory, file_base)
                    os.makedirs(file_output_dir, exist_ok=True)

                    # Log the output directory
                    self.status_update.emit(f"Output directory: {file_output_dir}")

                    # Determine which pages to process
                    if self.mode == "All Pages":
                        pages_to_process = range(total_pages)
                    elif self.mode == "Selected Pages":
                        pages_to_process = range(total_pages)  # TODO: Implement page selection
                    else:  # Page Range
                        try:
                            pages_to_process = self._parse_page_range(self.page_range, total_pages)
                        except ValueError as e:
                            self.error.emit(f"Invalid page range: {str(e)}")
                            self.finished.emit(False)
                            return

                    # Extract text from each page
                    extracted_text = []
                    for page_num in pages_to_process:
                        if not self._is_running:
                            break

                        try:
                            page = doc[page_num]
                            text = page.get_text()
                            extracted_text.append(text)
                            self.status_update.emit(f"Extracted text from page {page_num + 1} of {total_pages}")

                        except Exception as e:
                            self.error.emit(f"Error extracting text from page {page_num + 1}: {str(e)}")
                            self.finished.emit(False)
                            return

                    # Save extracted text
                    if extracted_text:
                        output_file = os.path.join(file_output_dir, f"{file_base}.{self.output_format}")
                        try:
                            if self.output_format == "txt":
                                with open(output_file, "w", encoding="utf-8") as f:
                                    f.write("\n\n".join(extracted_text))
                            else:  # Word format
                                from docx import Document

                                doc = Document()
                                for text in extracted_text:
                                    doc.add_paragraph(text)
                                doc.save(output_file)

                            self.status_update.emit(f"Saved extracted text to: {output_file}")
                        except Exception as e:
                            self.error.emit(f"Error saving extracted text: {str(e)}")
                            self.finished.emit(False)
                            return

                    doc.close()
                    self.progress.emit(int((i + 1) / len(self.pdf_files) * 100))

                except Exception as e:
                    self.error.emit(f"Error processing {os.path.basename(pdf_file)}: {str(e)}")
                    self.finished.emit(False)
                    return

            if self._is_running:
                self.finished.emit(True)

        except Exception as e:
            if self._is_running:
                self.error.emit(f"Critical error in extract text worker: {str(e)}")
                self.finished.emit(False)
        finally:
            self._is_running = False

    def _parse_page_range(self, page_range, total_pages):
        """Parse page range string (e.g., "1-3,5,7-9") into list of page numbers"""
        if not page_range:
            return range(total_pages)

        pages = []
        for part in page_range.split(","):
            if "-" in part:
                start, end = map(int, part.split("-"))
                if start < 1 or end > total_pages or start > end:
                    raise ValueError(f"Invalid page range: {part}")
                pages.extend(range(start - 1, end))
            else:
                page = int(part)
                if page < 1 or page > total_pages:
                    raise ValueError(f"Invalid page number: {page}")
                pages.append(page - 1)
        return sorted(set(pages))

    def stop(self):
        self._is_running = False
