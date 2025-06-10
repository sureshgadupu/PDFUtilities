import sys
import os
import fitz  # PyMuPDF

def compress_pdf(input_path, output_path, dpi=100):
    if not os.path.isfile(input_path):
        print(f"❌ Error: File '{input_path}' does not exist.")
        return

    try:
        doc = fitz.open(input_path)
        new_pdf = fitz.open()  # Empty PDF

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # Render page at reduced DPI
            zoom = dpi / 72  # 72 is the default DPI for PDF
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            # Create new PDF page from image
            img_pdf = fitz.open()
            img_pdf.insert_page(-1, width=pix.width, height=pix.height)
            img_page = img_pdf[-1]
            img_page.insert_image(img_page.rect, stream=pix.tobytes())

            # Add the page to the new PDF
            new_pdf.insert_pdf(img_pdf)

        # Save compressed PDF
        new_pdf.save(output_path, deflate=True, garbage=3)
        new_pdf.close()
        doc.close()

        print(f"✅ Compression complete. Saved as: {output_path}")

    except Exception as e:
        print(f"❌ Error during compression: {e}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python compress_pdf.py input.pdf output.pdf")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]

    compress_pdf(input_pdf, output_pdf)

if __name__ == "__main__":
    main()
