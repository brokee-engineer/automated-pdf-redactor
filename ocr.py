import fitz  # PyMuPDF
from PIL import Image
from pdf2image import convert_from_path
import pytesseract
import io
import os

# ✅ Set the Poppler binary path explicitly
POPPLER_PATH = r"C:\Users\anssh\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"  # Update as needed

def extract_text_with_boxes(pdf_path):
    """
    Convert PDF pages to images, run OCR with Tesseract, 
    and return a list of words with scaled bounding boxes for each page.
    """
    pages = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
    results = []

    # Open PDF to get page dimensions for scaling
    pdf_doc = fitz.open(pdf_path)

    for page_num, image in enumerate(pages):
        # Get OCR data from the image
        ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

        # Image (OCR) dimensions
        img_width, img_height = image.size

        # PDF page dimensions
        pdf_page = pdf_doc[page_num]
        pdf_width, pdf_height = pdf_page.rect.width, pdf_page.rect.height

        # Scale factors to map OCR coordinates -> PDF coordinates
        scale_x = pdf_width / img_width
        scale_y = pdf_height / img_height

        page_words = []
        for i in range(len(ocr_data['text'])):
            word = ocr_data['text'][i].strip()
            if word:
                # Original OCR bbox (pixel-based)
                x, y, w, h = (ocr_data['left'][i], ocr_data['top'][i],
                              ocr_data['width'][i], ocr_data['height'][i])

                # Scale to PDF coordinate space
                scaled_x = x * scale_x
                scaled_y = y * scale_y
                scaled_w = w * scale_x
                scaled_h = h * scale_y

                page_words.append({
                    "text": word,
                    "bbox": (scaled_x, scaled_y, scaled_w, scaled_h)
                })

        results.append(page_words)

    pdf_doc.close()
    return results
