import os
from pdf2docx import Converter # Assuming you use pdf2docx

# Placeholder for potential Qt threading if needed later
# from PyQt6.QtCore import QObject, pyqtSignal

def convert_single_pdf_to_docx(pdf_path, docx_path):
    """Converts a single PDF file to DOCX and returns success status and a message."""
    try:
        # Ensure output directory for the docx_path exists
        os.makedirs(os.path.dirname(docx_path), exist_ok=True)
        
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()
        return True, f"Successfully converted {os.path.basename(pdf_path)} to DOCX."
    except Exception as e:
        return False, f"Error converting {os.path.basename(pdf_path)}: {str(e)}"

def convert_multiple_pdfs_to_docx(pdf_files, output_directory, progress_callback=None, status_callback=None):
    """
    Converts a list of PDF files to DOCX format, saving them in the output_directory.

    Args:
        pdf_files (list): A list of paths to PDF files.
        output_directory (str): The directory to save converted DOCX files.
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

    if not os.path.exists(output_directory):
        try:
            os.makedirs(output_directory)
        except OSError as e:
            if status_callback:
                status_callback(f"Error creating output directory {output_directory}: {e}")
            return [], [f"Error creating output directory {output_directory}: {e}"] # Or handle differently

    successful_messages = []
    failed_messages = []
    total_files = len(pdf_files)

    if progress_callback:
        progress_callback(0, total_files) # Initialize progress

    for index, pdf_file in enumerate(pdf_files):
        base_name = os.path.basename(pdf_file)
        docx_name = os.path.splitext(base_name)[0] + ".docx"
        docx_path = os.path.join(output_directory, docx_name)

        if status_callback:
            status_callback(f"Converting {base_name} ({index + 1}/{total_files})...")

        success, message = convert_single_pdf_to_docx(pdf_file, docx_path)

        if success:
            successful_messages.append(message)
        else:
            failed_messages.append(message)
        
        if status_callback: # Update status after each attempt
             status_callback(message)


        if progress_callback:
            progress_callback(index + 1, total_files)

    final_status = f"Conversion finished. {len(successful_messages)} succeeded, {len(failed_messages)} failed."
    if status_callback:
        status_callback(final_status)
    
    if not successful_messages and not failed_messages and total_files > 0: # Should not happen if logic is correct
        if status_callback:
            status_callback("Conversion process completed, but no files were processed.")


    return successful_messages, failed_messages 