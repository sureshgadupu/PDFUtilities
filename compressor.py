import os
import shutil
import subprocess
import sys

import fitz  # PyMuPDF


def compress_pdf(input_path, output_path, image_quality=80, remove_metadata=True):
    """Compress PDF by recompressing images and optionally removing metadata.
    
    Args:
        input_path (str): Path to input PDF file.
        output_path (str): Path to output PDF file.
        image_quality (int): JPEG quality (10-100, higher is better quality/larger size).
        remove_metadata (bool): If True, remove metadata from the PDF.
    Returns:
        bool: True if compression succeeded, False otherwise.
        str: Message about the result.
    """
    try:
        doc = fitz.open(input_path)
        for page_num, page in enumerate(doc):
            images = page.get_images(full=True)
            for img_index, img in enumerate(images):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                img_ext = base_image["ext"]
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
                    except Exception as img_e:
                        print(f"[ERROR]     Failed to recompress image {img_index+1}: {img_e}")
        if remove_metadata:
            doc.set_metadata({})
        doc.save(output_path, garbage=4, deflate=True)
        doc.close()
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
            ("high", 300),  # Start with high quality
            ("high", 250),  # Gradual reduction from high
            ("high", 200),
            ("high", 175),
            ("medium", 150),  # Then medium
            ("medium", 120),  # Then intermediate steps
            ("medium", 100),
            ("medium", 80),
            ("low", 72),  # Finally low quality
        ]
    else:
        quality_steps = [
            ("medium", 150),  # Start with medium quality
            ("medium", 120),  # Then intermediate steps
            ("medium", 100),
            ("medium", 80),
            ("low", 72),  # Finally low quality
        ]

    # Try each quality step
    for quality, dpi in quality_steps:
        print(f"\nTrying {quality} quality ({dpi} DPI)...")
        temp_output = output_path.replace(".pdf", f"_{quality}_{dpi}.pdf")
        ghostscript_compress(input_path, temp_output, quality, custom_dpi=dpi)
        temp_size = os.path.getsize(temp_output) / 1024
        print(f"Size at {dpi} DPI: {temp_size:.2f} KB")

        if temp_size <= target_size_kb:
            print(f"Target size achieved with {quality} quality ({dpi} DPI)!")
            shutil.move(temp_output, output_path)
            return True, f"Target size achieved: {temp_size:.2f} KB"

        # Clean up intermediate file
        try:
            os.remove(temp_output)
        except OSError:
            pass

    # If quality steps didn't work, try image quality reduction
    print("\nAttempting image quality reduction...")
    quality = 85
    while quality >= 30:
        print(f"\nTrying with image quality: {quality}%")
        temp_output = output_path.replace(".pdf", f"_q{quality}.pdf")
        ghostscript_compress(input_path, temp_output, "low", image_quality=quality)
        temp_size = os.path.getsize(temp_output) / 1024
        print(f"Size at {quality}% quality: {temp_size:.2f} KB")

        if temp_size <= target_size_kb:
            print(f"Target size achieved with {quality}% image quality!")
            shutil.move(temp_output, output_path)
            return True, f"Target size achieved: {temp_size:.2f} KB"

        # Clean up intermediate file
        try:
            os.remove(temp_output)
        except OSError:
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
        temp_output = output_path.replace(".pdf", f"_{quality}_{dpi}.pdf")
        try:
            ghostscript_compress(input_path, temp_output, quality, custom_dpi=dpi)
            temp_size = os.path.getsize(temp_output) / 1024
            sizes[f"{quality}_{dpi}"] = (temp_output, temp_size)
        except (OSError, subprocess.CalledProcessError):
            pass

    # Add low quality with image compression as last resort
    temp_output = output_path.replace(".pdf", "_q30.pdf")
    try:
        ghostscript_compress(input_path, temp_output, "low", image_quality=30)
        temp_size = os.path.getsize(temp_output) / 1024
        sizes["low_q30"] = (temp_output, temp_size)
    except (OSError, subprocess.CalledProcessError):
        pass

    if not sizes:
        return False, "Failed to compress file"

    # Clean up all temporary files except the smallest one
    best_quality = min(sizes.items(), key=lambda x: x[1][1])
    for quality, (path, _) in sizes.items():
        if path != best_quality[1][0]:
            try:
                os.remove(path)
            except OSError:
                pass

    shutil.move(best_quality[1][0], output_path)
    final_size = best_quality[1][1]
    print(f"Final size: {final_size:.2f} KB")
    
    # Return False for target size not achieved, but with informative message
    return False, f"Target size ({target_size_kb} KB) not achieved. Best size: {final_size:.2f} KB"


def get_system_ghostscript_path():
    """Get the path to the system-installed Ghostscript executable."""
    if os.name == "nt":
        # Check for system-installed Ghostscript
        gs_path = shutil.which("gswin64c")
        if gs_path:
            return gs_path
        gs_path = shutil.which("gswin32c")
        if gs_path:
            return gs_path
    else:
        # Unix-like systems
        gs_path = shutil.which("gs")
        if gs_path:
            return gs_path
    return None


def is_ghostscript_available():
    """Check if Ghostscript is available (system installation on all platforms)."""
    if os.name == "nt":
        return shutil.which("gswin64c") is not None or shutil.which("gswin32c") is not None
    else:
        return shutil.which("gs") is not None


def get_ghostscript_cmd():
    """Get the Ghostscript command to use."""
    if os.name == "nt":
        gs_path = shutil.which("gswin64c")
        if gs_path:
            return gs_path
        gs_path = shutil.which("gswin32c")
        if gs_path:
            return gs_path
        return "gswin64c"  # fallback, will error if not installed
    else:
        gs_path = shutil.which("gs")
        if gs_path:
            return gs_path
        return "gs"  # fallback, will error if not installed


def ghostscript_compress(input_path, output_path, quality="medium", image_quality=None, custom_dpi=None):
    """Compress PDF using Ghostscript with specified quality settings."""
    if not is_ghostscript_available():
        if os.name == "nt":
            raise Exception("Ghostscript is not available. Please install it or ensure it is in your PATH.")
        else:
            raise Exception(
                "Ghostscript is not installed or not in PATH. Please install it using your package manager:\n"
                "- Ubuntu/Debian: sudo apt install ghostscript\n"
                "- Fedora: sudo dnf install ghostscript\n"
                "- Arch: sudo pacman -S ghostscript\n"
                "- openSUSE: sudo zypper install ghostscript"
            )

    # Define quality settings
    quality_settings = {"low": ("/screen", 72), "medium": ("/ebook", 150), "high": ("/printer", 300)}

    # Get base settings
    gs_setting, base_dpi = quality_settings[quality]

    # Use custom DPI if provided
    dpi = custom_dpi if custom_dpi is not None else base_dpi

    # Build Ghostscript command
    gs_cmd = get_ghostscript_cmd()
    cmd = [
        gs_cmd,
        "-sDEVICE=pdfwrite",
        f"-dPDFSETTINGS={gs_setting}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-dColorImageResolution={dpi}",
        f"-dGrayImageResolution={dpi}",
        f"-dMonoImageResolution={dpi}",
    ]

    # Add image quality settings if specified
    if image_quality is not None:
        cmd.extend(
            [
                f"-dJPEGQ={image_quality}",
                "-dAutoFilterColorImages=false",
                "-dAutoFilterGrayImages=false",
                "-dColorImageDownsampleType=/Bicubic",
                "-dGrayImageDownsampleType=/Bicubic",
            ]
        )

    cmd.extend(["-sOutputFile=" + output_path, input_path])

    # Execute command
    subprocess.run(cmd, check=True, capture_output=True)


def compress_multiple_pdfs(
    pdf_files, output_directory, compression_mode="medium", target_size_kb=None, progress_callback=None, status_callback=None
):
    """
    Compress multiple PDFs using Ghostscript. compression_mode: 'low', 'medium', 'high'.
    target_size_kb: if set, will compress to target size using image quality adjustment.
    Output files are named with _compressed before .pdf, and numbered if needed.
    """
    if not is_ghostscript_available():
        if os.name == "nt":
            msg = "Ghostscript is not installed or not in PATH. Please install Ghostscript."
        elif sys.platform == "darwin":
            msg = (
                "Ghostscript is not installed or not in PATH. Please install it using Homebrew:\n"
                "- macOS: brew install ghostscript"
            )
        else:
            msg = (
                "Ghostscript is not installed or not in PATH. Please install it using your package manager:\n"
                "- Ubuntu/Debian: sudo apt install ghostscript\n"
                "- Fedora: sudo dnf install ghostscript\n"
                "- Arch: sudo pacman -S ghostscript\n"
                "- openSUSE: sudo zypper install ghostscript"
            )
        print(f"[ERROR] {msg}")
        if status_callback:
            status_callback(msg)
        return [], [msg]

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

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

        if status_callback:
            status_callback(f"Compressing {base} ({idx+1}/{total})...")

        try:
            # If target size is specified, use the target size compression function
            if target_size_kb:
                if status_callback:
                    status_callback(f"Compressing to target size: {target_size_kb} KB...")
                success, message = compress_pdf_to_target_size(pdf, out_path, target_size_kb)
                if success:
                    successes.append(f"Compressed: {base} - {message}")
                else:
                    # Check if it's a complete failure or just target size not achieved
                    if "Failed to compress file" in message:
                        failures.append(f"Failed to compress {base}: {message}")
                    else:
                        # Target size not achieved but file was compressed
                        successes.append(f"Compressed: {base} - {message}")
            else:
                # If no target size, use specified compression mode
                ghostscript_compress(pdf, out_path, quality=compression_mode)
                successes.append(f"Compressed: {base}")

            if progress_callback:
                progress_callback(idx + 1, total)

        except Exception as e:
            error_msg = f"Error compressing {base}: {str(e)}"
            print(f"[ERROR] {error_msg}")
            failures.append(error_msg)
            if status_callback:
                status_callback(error_msg)

    return successes, failures
