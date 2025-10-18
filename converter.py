import os
import threading
import time

import fitz  # PyMuPDF for password handling
from pdf2docx import Converter  # Assuming you use pdf2docx

# Placeholder for potential Qt threading if needed later
# from PyQt6.QtCore import QObject, pyqtSignal


class TimeoutError(Exception):
    """Custom exception for timeout errors"""
    pass


def convert_with_timeout(func, timeout_seconds):
    """Run a function with a timeout using threading"""
    result = [None]
    exception = [None]
    completed = [False]
    
    def target():
        try:
            result[0] = func()
            completed[0] = True
        except Exception as e:
            exception[0] = e
            completed[0] = True
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout_seconds)
    
    if not completed[0]:
        # Thread is still running, timeout occurred
        print(f"DEBUG: Conversion timed out after {timeout_seconds} seconds")
        raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")
    
    if exception[0]:
        raise exception[0]
    
    return result[0]


def convert_single_pdf_to_docx(pdf_path, docx_path, password=None, timeout=60):
    """Converts a single PDF file to DOCX and returns success status and a message."""
    try:
        # Ensure output directory for the docx_path exists
        os.makedirs(os.path.dirname(docx_path), exist_ok=True)

        # First, check if PDF is password protected
        doc = fitz.open(pdf_path)
        try:
            # Try to access first page to check if password is needed
            doc[0]
            # If we get here, PDF is not password protected
            password = None
            print(f"DEBUG: PDF {os.path.basename(pdf_path)} is not password protected")
        except Exception as e:
            print(f"DEBUG: PDF {os.path.basename(pdf_path)} appears to be password protected: {str(e)}")
            # PDF is password protected, try with provided password
            if password:
                try:
                    # Try to authenticate with password
                    if doc.authenticate(password):
                        print(f"DEBUG: Password authentication successful for {os.path.basename(pdf_path)}")
                    else:
                        doc.close()
                        return False, f"Error opening password-protected PDF {os.path.basename(pdf_path)}: Invalid password"
                except Exception as e:
                    doc.close()
                    return False, f"Error opening password-protected PDF {os.path.basename(pdf_path)}: Invalid password"
            else:
                doc.close()
                return False, f"Error opening password-protected PDF {os.path.basename(pdf_path)}: Password required"
        finally:
            doc.close()

        # For password-protected files, use alternative method directly
        if password:
            print(f"DEBUG: Password-protected file detected, using alternative method directly")
            return convert_pdf_to_docx_alternative(pdf_path, docx_path, password)
        
        # Convert using pdf2docx with timeout for non-password protected files
        try:
            print(f"DEBUG: Attempting pdf2docx conversion for {os.path.basename(pdf_path)}")
            def convert_func():
                cv = Converter(pdf_path)
                cv.convert(docx_path, start=0, end=None)
                cv.close()
                return True
            
            convert_with_timeout(convert_func, timeout)
            print(f"DEBUG: pdf2docx conversion completed successfully")
                
        except TimeoutError:
            print(f"DEBUG: pdf2docx conversion timed out, switching to alternative method")
            # Try alternative method using PyMuPDF for text extraction
            return convert_pdf_to_docx_alternative(pdf_path, docx_path, password)
        except Exception as e:
            # If conversion fails and we have a password, try a different approach
            if password:
                # Create a temporary unlocked PDF first
                temp_pdf_path = pdf_path.replace('.pdf', '_temp_unlocked.pdf')
                try:
                    doc = fitz.open(pdf_path)
                    if doc.authenticate(password):
                        doc.save(temp_pdf_path)
                        doc.close()
                        
                        # Convert the temporary unlocked PDF with timeout
                        try:
                            def convert_temp_func():
                                cv = Converter(temp_pdf_path)
                                cv.convert(docx_path, start=0, end=None)
                                cv.close()
                                return True
                            
                            convert_with_timeout(convert_temp_func, timeout)
                            
                        except TimeoutError:
                            # Clean up temporary file
                            if os.path.exists(temp_pdf_path):
                                os.remove(temp_pdf_path)
                            return convert_pdf_to_docx_alternative(temp_pdf_path, docx_path, None)
                        
                        # Clean up temporary file
                        os.remove(temp_pdf_path)
                    else:
                        doc.close()
                        return False, f"Error opening password-protected PDF {os.path.basename(pdf_path)}: Invalid password"
                except Exception as temp_e:
                    # Clean up temporary file if it exists
                    if os.path.exists(temp_pdf_path):
                        os.remove(temp_pdf_path)
                    return False, f"Error converting password-protected PDF {os.path.basename(pdf_path)}: {str(temp_e)}"
            else:
                return False, f"Error converting {os.path.basename(pdf_path)}: {str(e)}"
        
        return True, f"Successfully converted {os.path.basename(pdf_path)} to DOCX."
    except Exception as e:
        return False, f"Error converting {os.path.basename(pdf_path)}: {str(e)}"


def convert_pdf_to_docx_alternative(pdf_path, docx_path, password=None):
    """Alternative conversion method using PyMuPDF for text extraction when pdf2docx fails"""
    try:
        print(f"DEBUG: Using alternative conversion method for {os.path.basename(pdf_path)}")
        
        # Try to import python-docx
        try:
            from docx import Document
            from docx.shared import Inches
        except ImportError:
            return False, f"python-docx library not installed. Please install it with: pip install python-docx"
        
        # Open PDF with password if needed
        doc = fitz.open(pdf_path)
        if password and not doc.authenticate(password):
            doc.close()
            return False, f"Invalid password for {os.path.basename(pdf_path)}"
        
        print(f"DEBUG: PDF opened successfully, {len(doc)} pages found")
        
        # Create a new Word document
        word_doc = Document()
        
        # Extract text from each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            print(f"DEBUG: Page {page_num + 1}: {len(text)} characters extracted")
            
            if text.strip():  # Only add pages with text
                # Add page break for pages after the first
                if page_num > 0:
                    word_doc.add_page_break()
                
                # Add the text to the document
                paragraph = word_doc.add_paragraph(text)
        
        # Save the document
        print(f"DEBUG: Saving DOCX to {docx_path}")
        word_doc.save(docx_path)
        doc.close()
        
        # Verify the file was created
        if os.path.exists(docx_path):
            file_size = os.path.getsize(docx_path)
            print(f"DEBUG: DOCX file created successfully, size: {file_size} bytes")
            return True, f"Successfully converted {os.path.basename(pdf_path)} to DOCX (using alternative method)."
        else:
            return False, f"Failed to create DOCX file at {docx_path}"
        
    except Exception as e:
        print(f"DEBUG: Error in alternative conversion: {str(e)}")
        return False, f"Error converting {os.path.basename(pdf_path)} using alternative method: {str(e)}"


def convert_multiple_pdfs_to_docx(pdf_files, output_directory, passwords=None, progress_callback=None, status_callback=None):
    """
    Converts a list of PDF files to DOCX format, saving them in the output_directory.

    Args:
        pdf_files (list): A list of paths to PDF files.
        output_directory (str): The directory to save converted DOCX files.
        passwords (dict, optional): Dictionary mapping file paths to passwords.
        progress_callback (function, optional):
            A function to call for progress updates.
            Expected to take (current_value, max_value).
        status_callback (function, optional):
            A function to call for status messages.
            Expected to take (message_string).
    Returns:
        tuple: (list_of_successful_conversion_messages, list_of_failed_conversion_messages)
    """
    if not pdf_files:
        if status_callback:
            status_callback("No PDF files selected for conversion.")
        return [], []

    if passwords is None:
        passwords = {}

    if not os.path.exists(output_directory):
        try:
            os.makedirs(output_directory)
        except OSError as e:
            if status_callback:
                status_callback(f"Error creating output directory {output_directory}: {e}")
            return [], [f"Error creating output directory {output_directory}: {e}"]  # Or handle differently

    successful_messages = []
    failed_messages = []
    total_files = len(pdf_files)

    if progress_callback:
        progress_callback(0, total_files)  # Initialize progress

    for index, pdf_file in enumerate(pdf_files):
        base_name = os.path.basename(pdf_file)
        docx_name = os.path.splitext(base_name)[0] + ".docx"
        docx_path = os.path.join(output_directory, docx_name)

        if status_callback:
            status_callback(f"Converting {base_name} ({index + 1}/{total_files})...")

        # Get password for this file if available
        password = passwords.get(pdf_file)
        success, message = convert_single_pdf_to_docx(pdf_file, docx_path, password)

        if success:
            successful_messages.append(message)
        else:
            failed_messages.append(message)

        if status_callback:  # Update status after each attempt
            status_callback(message)

        if progress_callback:
            progress_callback(index + 1, total_files)

    final_status = f"Conversion finished. {len(successful_messages)} succeeded, {len(failed_messages)} failed."
    if status_callback:
        status_callback(final_status)

    if not successful_messages and not failed_messages and total_files > 0:  # Should not happen if logic is correct
        if status_callback:
            status_callback("Conversion process completed, but no files were processed.")

    return successful_messages, failed_messages
