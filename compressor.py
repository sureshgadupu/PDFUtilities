import os
import fitz  # PyMuPDF
import shutil
import subprocess
import sys
import platform

def compress_pdf(input_path, output_path, image_quality=80, remove_metadata=True):
    """
    Compress a PDF by recompressing images and optionally removing metadata.
    Args:
        input_path (str): Path to the input PDF.
        output_path (str): Path to save the compressed PDF.
        image_quality (int): JPEG quality (10-100, higher is better quality/larger size).
        remove_metadata (bool): If True, remove metadata from the PDF.
    Returns:
        bool: True if compression succeeded, False otherwise.
        str: Message about the result.
    """
    try:
        print(f"[DEBUG] Opening PDF: {input_path}")
        doc = fitz.open(input_path)
        for page_num, page in enumerate(doc):
            images = page.get_images(full=True)
            print(f"[DEBUG] Page {page_num+1}: {len(images)} images found.")
            for img_index, img in enumerate(images):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                img_ext = base_image["ext"]
                print(f"[DEBUG]   Image {img_index+1}: xref={xref}, ext={img_ext}, size={len(image_bytes)} bytes")
                # Only recompress JPEG or PNG images
                if img_ext.lower() in ["jpeg", "jpg", "png"]:
                    try:
                        import io
                        from PIL import Image
                        pil_img = Image.open(io.BytesIO(image_bytes))
                        img_io = io.BytesIO()
                        pil_img.save(img_io, format="JPEG", quality=image_quality, optimize=True)
                        img_io.seek(0)
                        new_img_bytes = img_io.read()
                        doc.update_image(xref, new_img_bytes)
                        print(f"[DEBUG]     Recompressed image {img_index+1} at quality {image_quality}.")
                    except Exception as img_e:
                        print(f"[ERROR]     Failed to recompress image {img_index+1}: {img_e}")
        if remove_metadata:
            doc.set_metadata({})
            print(f"[DEBUG] Metadata removed.")
        print(f"[DEBUG] Saving compressed PDF to: {output_path}")
        doc.save(output_path, garbage=4, deflate=True)
        doc.close()
        print(f"[DEBUG] Compression complete for: {output_path}")
        return True, f"Compressed: {os.path.basename(input_path)}"
    except Exception as e:
        print(f"[ERROR] Exception during compression of {input_path}: {e}")
        return False, f"Error compressing {os.path.basename(input_path)}: {e}"

def compress_pdf_to_target_size(input_path, output_path, target_size_kb):
    """Compress PDF to target size using Ghostscript with progressive quality reduction."""
    print(f"\nCompressing to target size: {target_size_kb} KB")
    print(f"Original file: {input_path}")
    
    # Get original size
    original_size = os.path.getsize(input_path) / 1024  # Convert to KB
    print(f"Original size: {original_size:.2f} KB")
    
    # Define quality steps based on target size
    if target_size_kb > 1000:  # If target is more than 1MB
        quality_steps = [
            ('high', 300),    # Start with high quality
            ('high', 250),    # Gradual reduction from high
            ('high', 200),
            ('high', 175),
            ('medium', 150),  # Then medium
            ('medium', 120),  # Then intermediate steps
            ('medium', 100),
            ('medium', 80),
            ('low', 72)       # Finally low quality
        ]
    else:
        quality_steps = [
            ('medium', 150),  # Start with medium quality
            ('medium', 120),  # Then intermediate steps
            ('medium', 100),
            ('medium', 80),
            ('low', 72)       # Finally low quality
        ]
    
    # Try each quality step
    for quality, dpi in quality_steps:
        print(f"\nTrying {quality} quality ({dpi} DPI)...")
        temp_output = output_path.replace('.pdf', f'_{quality}_{dpi}.pdf')
        ghostscript_compress(input_path, temp_output, quality, custom_dpi=dpi)
        temp_size = os.path.getsize(temp_output) / 1024
        print(f"Size at {dpi} DPI: {temp_size:.2f} KB")
        
        if temp_size <= target_size_kb:
            print(f"Target size achieved with {quality} quality ({dpi} DPI)!")
            shutil.move(temp_output, output_path)
            return True
        
        # Clean up intermediate file
        try:
            os.remove(temp_output)
        except:
            pass
    
    # If quality steps didn't work, try image quality reduction
    print("\nAttempting image quality reduction...")
    quality = 85
    while quality >= 30:
        print(f"\nTrying with image quality: {quality}%")
        temp_output = output_path.replace('.pdf', f'_q{quality}.pdf')
        ghostscript_compress(input_path, temp_output, 'low', image_quality=quality)
        temp_size = os.path.getsize(temp_output) / 1024
        print(f"Size at {quality}% quality: {temp_size:.2f} KB")
        
        if temp_size <= target_size_kb:
            print(f"Target size achieved with {quality}% image quality!")
            shutil.move(temp_output, output_path)
            return True
        
        # Clean up intermediate file
        try:
            os.remove(temp_output)
        except:
            pass
        
        # Reduce quality more aggressively if we're still far from target
        if temp_size > target_size_kb * 1.5:
            quality -= 15
        else:
            quality -= 5
    
    # If we still haven't achieved the target size, use the smallest result
    print("\nCould not achieve target size. Using best available compression...")
    sizes = {}
    
    # Try one final time with each quality level to get the smallest possible size
    for quality, dpi in quality_steps:
        temp_output = output_path.replace('.pdf', f'_{quality}_{dpi}.pdf')
        try:
            ghostscript_compress(input_path, temp_output, quality, custom_dpi=dpi)
            temp_size = os.path.getsize(temp_output) / 1024
            sizes[f"{quality}_{dpi}"] = (temp_output, temp_size)
        except:
            pass
    
    # Add low quality with image compression as last resort
    temp_output = output_path.replace('.pdf', '_q30.pdf')
    try:
        ghostscript_compress(input_path, temp_output, 'low', image_quality=30)
        temp_size = os.path.getsize(temp_output) / 1024
        sizes['low_q30'] = (temp_output, temp_size)
    except:
        pass
    
    if not sizes:
        return False
    
    # Clean up all temporary files except the smallest one
    best_quality = min(sizes.items(), key=lambda x: x[1][1])
    for quality, (path, _) in sizes.items():
        if path != best_quality[1][0]:
            try:
                os.remove(path)
            except:
                pass
    
    shutil.move(best_quality[1][0], output_path)
    print(f"Final size: {best_quality[1][1]:.2f} KB")
    return False

def get_bundled_ghostscript_path():
    """Get the path to the bundled Ghostscript executable."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        if hasattr(sys, '_MEIPASS'):
            # One-file mode: files are extracted to a temporary directory
            base_path = sys._MEIPASS
            print(f"[DEBUG] Running as frozen executable (one-file), temp path: {base_path}")
        else:
            # One-directory mode: files are in the same directory as the executable
            base_path = os.path.dirname(sys.executable)
            print(f"[DEBUG] Running as frozen executable (one-dir), base path: {base_path}")
    else:
        # Running as script
        base_path = os.path.dirname(os.path.abspath(__file__))
        print(f"[DEBUG] Running as script, base path: {base_path}")
    
    print(f"[DEBUG] Base path: {base_path}")
    
    # Check in platform-specific Ghostscript directory
    if os.name == 'nt':
        # Windows version
        gs_dir = os.path.join(base_path, 'bin', 'Ghostscript', 'Windows')
        print(f"[DEBUG] Looking for Ghostscript in: {gs_dir}")
        print(f"[DEBUG] Directory exists: {os.path.exists(gs_dir)}")
        
        if os.path.exists(gs_dir):
            print(f"[DEBUG] Directory contents: {os.listdir(gs_dir)}")
        else:
            # If not found, list what's actually in the base path
            print(f"[DEBUG] Base path contents: {os.listdir(base_path) if os.path.exists(base_path) else 'Base path does not exist'}")
        
        # Try 64-bit, then 32-bit
        gs_exe = os.path.join(gs_dir, 'gswin64c.exe')
        print(f"[DEBUG] Checking for 64-bit version: {gs_exe}")
        print(f"[DEBUG] 64-bit exists: {os.path.exists(gs_exe)}")
        
        if not os.path.exists(gs_exe):
            print(f"[DEBUG] 64-bit version not found, checking 32-bit")
            gs_exe = os.path.join(gs_dir, 'gswin32c.exe')
            print(f"[DEBUG] Checking for 32-bit version: {gs_exe}")
            print(f"[DEBUG] 32-bit exists: {os.path.exists(gs_exe)}")
    else:
        # Linux version
        gs_dir = os.path.join(base_path, 'bin', 'Ghostscript', 'Linux')
        print(f"[DEBUG] Looking for Ghostscript in: {gs_dir}")
        print(f"[DEBUG] Directory exists: {os.path.exists(gs_dir)}")
        
        if os.path.exists(gs_dir):
            print(f"[DEBUG] Directory contents: {os.listdir(gs_dir)}")
        else:
            # If not found, list what's actually in the base path
            print(f"[DEBUG] Base path contents: {os.listdir(base_path) if os.path.exists(base_path) else 'Base path does not exist'}")
            
        gs_exe = os.path.join(gs_dir, 'gs')
        print(f"[DEBUG] Checking for Linux version: {gs_exe}")
        print(f"[DEBUG] Linux version exists: {os.path.exists(gs_exe)}")
    
    if os.path.exists(gs_exe):
        print(f"[DEBUG] Found Ghostscript at: {gs_exe}")
        # Check if it's executable
        if os.access(gs_exe, os.X_OK):
            print(f"[DEBUG] Ghostscript is executable")
        else:
            print(f"[DEBUG] Warning: Ghostscript exists but is not executable")
    else:
        print(f"[DEBUG] Ghostscript not found at: {gs_exe}")
    
    return gs_exe if os.path.exists(gs_exe) else None

def is_ghostscript_available():
    """Check if Ghostscript is available in the bin directory."""
    return get_bundled_ghostscript_path() is not None

def get_ghostscript_cmd():
    """Get the Ghostscript command to use from bin directory."""
    gs_path = get_bundled_ghostscript_path()
    if gs_path:
        return gs_path
    
    # Fallback to system PATH if not found in bin
    if os.name == 'nt':
        return shutil.which('gswin64c') or shutil.which('gswin32c') or 'gswin64c'
    else:
        return shutil.which('gs') or 'gs'

def ghostscript_compress(input_path, output_path, quality='medium', image_quality=None, custom_dpi=None):
    """Compress PDF using Ghostscript with specified quality settings."""
    if not is_ghostscript_available():
        raise Exception("Ghostscript is not available. Please install it first.")
    
    # Define quality settings
    quality_settings = {
        'low': ('/screen', 72),
        'medium': ('/ebook', 150),
        'high': ('/printer', 300)
    }
    
    # Get base settings
    gs_setting, base_dpi = quality_settings[quality]
    
    # Use custom DPI if provided
    dpi = custom_dpi if custom_dpi is not None else base_dpi
    
    # Build Ghostscript command
    gs_cmd = get_ghostscript_cmd()
    cmd = [
        gs_cmd,
        '-sDEVICE=pdfwrite',
        f'-dPDFSETTINGS={gs_setting}',
        '-dNOPAUSE',
        '-dQUIET',
        '-dBATCH',
        f'-dColorImageResolution={dpi}',
        f'-dGrayImageResolution={dpi}',
        f'-dMonoImageResolution={dpi}'
    ]
    
    # Add image quality settings if specified
    if image_quality is not None:
        cmd.extend([
            f'-dJPEGQ={image_quality}',
            '-dAutoFilterColorImages=false',
            '-dAutoFilterGrayImages=false',
            '-dColorImageDownsampleType=/Bicubic',
            '-dGrayImageDownsampleType=/Bicubic'
        ])
    
    cmd.extend(['-sOutputFile=' + output_path, input_path])
    
    # Execute command
    subprocess.run(cmd, check=True, capture_output=True)

def compress_multiple_pdfs(pdf_files, output_directory, compression_mode="medium", target_size_kb=None, progress_callback=None, status_callback=None):
    """
    Compress multiple PDFs using Ghostscript. compression_mode: 'low', 'medium', 'high'.
    target_size_kb: if set, will compress to target size using image quality adjustment.
    Output files are named with _compressed before .pdf, and numbered if needed.
    """
    print(f"[DEBUG] compress_multiple_pdfs called with {len(pdf_files)} files. Output dir: {output_directory}")
    print(f"[DEBUG] Compression mode: {compression_mode}, Target size: {target_size_kb} KB")
    
    if not is_ghostscript_available():
        msg = "Ghostscript is not installed or not in PATH. Please install Ghostscript."
        print(f"[ERROR] {msg}")
        if status_callback:
            status_callback(msg)
        return [], [msg]
    
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"[DEBUG] Created output directory: {output_directory}")
    
    total = len(pdf_files)
    successes, failures = [], []
    
    for idx, pdf in enumerate(pdf_files):
        base = os.path.basename(pdf)
        name, ext = os.path.splitext(base)
        out_base = f"{name}_compressed{ext}"
        out_path = os.path.join(output_directory, out_base)
        
        # Ensure unique file name
        counter = 1
        while os.path.exists(out_path):
            out_base = f"{name}_compressed({counter}){ext}"
            out_path = os.path.join(output_directory, out_base)
            counter += 1
        
        print(f"[DEBUG] Compressing {pdf} -> {out_path}")
        if status_callback:
            status_callback(f"Compressing {base} ({idx+1}/{total})...")
        
        try:
            # If target size is specified, use the target size compression function
            if target_size_kb:
                print(f"[DEBUG] Using target size compression: {target_size_kb} KB")
                if status_callback:
                    status_callback(f"Compressing to target size: {target_size_kb} KB...")
                success = compress_pdf_to_target_size(pdf, out_path, target_size_kb)
                if success:
                    successes.append(f"Compressed: {base}")
                else:
                    failures.append(f"Failed to compress {base} to target size")
            else:
                # If no target size, use specified compression mode
                print(f"[DEBUG] Using {compression_mode} compression (no target size)")
                ghostscript_compress(pdf, out_path, quality=compression_mode)
                successes.append(f"Compressed: {base}")
            
            if progress_callback:
                progress_callback(idx+1, total)
                
        except Exception as e:
            error_msg = f"Error compressing {base}: {str(e)}"
            print(f"[ERROR] {error_msg}")
            failures.append(error_msg)
            if status_callback:
                status_callback(error_msg)
    
    print(f"[DEBUG] Compression finished. Successes: {len(successes)}, Failures: {len(failures)}")
    return successes, failures 