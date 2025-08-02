import fitz  # PyMuPDF
import io
from PIL import Image
from google.cloud import vision
from google.cloud.vision_v1 import types
import os

# Load Google credentials from environment variable
gcp_credentials_str = os.getenv("GOOGLE_CREDENTIALS")
if not gcp_credentials_str:
    raise RuntimeError("Missing GOOGLE_CREDENTIALS environment variable!")

# Write credentials JSON to a temporary file
with open("/tmp/creds.json", "w") as f:
    f.write(gcp_credentials_str)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/creds.json"

# Initialize Vision client
vision_client = vision.ImageAnnotatorClient()

def extract_text_with_boxes(pdf_path):
    """
    Use PyMuPDF to render each PDF page as an image,
    send to Google Cloud Vision for OCR,
    and return a list of words with bounding boxes per page.
    """
    doc = fitz.open(pdf_path)
    results = []

    for page_num, page in enumerate(doc):
        # Render page to PNG image
        zoom = 2  # Increase resolution (300 dpi equivalent)
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Convert image to bytes for GCV
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        content = img_byte_arr.getvalue()

        # GCV image object
        gcv_image = types.Image(content=content)

        # Send to Google Cloud Vision API
        response = vision_client.document_text_detection(image=gcv_image)
        annotations = response.full_text_annotation

        page_words = []

        img_width, img_height = img.size
        pdf_width, pdf_height = page.rect.width, page.rect.height

        scale_x = pdf_width / img_width
        scale_y = pdf_height / img_height

        for gcv_page in annotations.pages:
            for block in gcv_page.blocks:
                for para in block.paragraphs:
                    for word in para.words:
                        word_text = ''.join([s.text for s in word.symbols])
                        if word_text.strip():
                            # Get GCV bounding box
                            vertices = word.bounding_box.vertices
                            x_min = min(v.x for v in vertices)
                            y_min = min(v.y for v in vertices)
                            x_max = max(v.x for v in vertices)
                            y_max = max(v.y for v in vertices)

                            x, y, w, h = x_min, y_min, x_max - x_min, y_max - y_min

                            scaled_x = x * scale_x
                            scaled_y = y * scale_y
                            scaled_w = w * scale_x
                            scaled_h = h * scale_y

                            page_words.append({
                                "text": word_text,
                                "bbox": (scaled_x, scaled_y, scaled_w, scaled_h)
                            })

        results.append(page_words)

    doc.close()
    return results
