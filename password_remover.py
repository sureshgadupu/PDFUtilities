import os
import fitz  # PyMuPDF


def remove_password_from_pdf(input_pdf_path, output_pdf_path, password=None):
    """
    Remove password protection from a PDF file.
    If the PDF is not password-protected, it will simply copy the file.
    
    Args:
        input_pdf_path (str): Path to the PDF file (password-protected or not)
        output_pdf_path (str): Path where the unlocked PDF will be saved
        password (str, optional): Password for the PDF file (only needed if password-protected)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
        
        # First, check if the PDF is password-protected
        doc = fitz.open(input_pdf_path)
        
        try:
            # Try to access the first page without password
            doc[0]
            # If we get here, PDF is not password protected
            doc.close()
            
            # Simply copy the file since it's not password-protected
            import shutil
            shutil.copy2(input_pdf_path, output_pdf_path)
            
            # Verify the file was created successfully
            if os.path.exists(output_pdf_path):
                file_size = os.path.getsize(output_pdf_path)
                return True, f"PDF {os.path.basename(input_pdf_path)} was not password-protected. File copied successfully. File size: {file_size} bytes"
            else:
                return False, f"Failed to copy PDF to {output_pdf_path}"
                
        except Exception as e:
            # PDF appears to be password-protected
            if not password:
                doc.close()
                return False, f"PDF {os.path.basename(input_pdf_path)} is password-protected but no password provided"
            
            # Try to authenticate with the provided password
            if not doc.authenticate(password):
                doc.close()
                return False, f"Invalid password for {os.path.basename(input_pdf_path)}"
            
            # Save the document without password protection
            # This effectively removes the password by saving it as a new document
            doc.save(output_pdf_path)
            doc.close()
            
            # Verify the file was created successfully
            if os.path.exists(output_pdf_path):
                file_size = os.path.getsize(output_pdf_path)
                return True, f"Successfully removed password from {os.path.basename(input_pdf_path)}. File size: {file_size} bytes"
            else:
                return False, f"Failed to create unlocked PDF at {output_pdf_path}"
            
    except Exception as e:
        return False, f"Error processing {os.path.basename(input_pdf_path)}: {str(e)}"


def remove_passwords_from_multiple_pdfs(pdf_files, output_directory, passwords=None, progress_callback=None, status_callback=None):
    """
    Remove passwords from multiple PDF files.
    
    Args:
        pdf_files (list): List of paths to password-protected PDF files
        output_directory (str): Directory to save unlocked PDF files
        passwords (dict, optional): Dictionary mapping file paths to passwords
        progress_callback (function, optional): Function to call for progress updates
        status_callback (function, optional): Function to call for status messages
        
    Returns:
        tuple: (list_of_successful_messages, list_of_failed_messages)
    """
    if not pdf_files:
        if status_callback:
            status_callback("No PDF files selected for password removal.")
        return [], []

    if passwords is None:
        passwords = {}

    if not os.path.exists(output_directory):
        try:
            os.makedirs(output_directory)
        except OSError as e:
            if status_callback:
                status_callback(f"Error creating output directory {output_directory}: {e}")
            return [], [f"Error creating output directory {output_directory}: {e}"]

    successful_messages = []
    failed_messages = []
    total_files = len(pdf_files)

    if progress_callback:
        progress_callback(0, total_files)  # Initialize progress

    for index, pdf_file in enumerate(pdf_files):
        base_name = os.path.basename(pdf_file)
        # Create output filename with "_unlocked" suffix
        unlocked_name = os.path.splitext(base_name)[0] + "_unlocked.pdf"
        unlocked_path = os.path.join(output_directory, unlocked_name)

        if status_callback:
            status_callback(f"Removing password from {base_name} ({index + 1}/{total_files})...")

        # Get password for this file (optional - only needed for password-protected files)
        password = passwords.get(pdf_file)

        success, message = remove_password_from_pdf(pdf_file, unlocked_path, password)

        if success:
            successful_messages.append(message)
        else:
            failed_messages.append(message)

        if status_callback:
            status_callback(message)

        if progress_callback:
            progress_callback(index + 1, total_files)

    final_status = f"Password removal finished. {len(successful_messages)} succeeded, {len(failed_messages)} failed."
    if status_callback:
        status_callback(final_status)

    return successful_messages, failed_messages


def is_pdf_password_protected(file_path):
    """
    Check if a PDF file is password protected.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        bool: True if the PDF is password protected, False otherwise
    """
    try:
        doc = fitz.open(file_path)
        # Try to access the first page without password
        doc[0]
        doc.close()
        return False
    except Exception as e:
        # If we can't access the page, it's likely password protected
        error_msg = str(e).lower()
        if 'password' in error_msg or 'encrypted' in error_msg or 'permission' in error_msg or 'closed' in error_msg:
            return True
        # For other errors, we'll assume it's not password protected
        return False
