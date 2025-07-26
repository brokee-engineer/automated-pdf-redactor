from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os
import shutil
from ocr import extract_text_with_boxes
from detect import detect_entities
from redact import redact_pdf

app = FastAPI()

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 1. Extract OCR word-level boxes
    word_boxes_per_page = extract_text_with_boxes(file_path)

    # 2. Detect PII entities from all text (you can flatten words if needed)
    full_text = " ".join(word["text"] for page in word_boxes_per_page for word in page)
    pii_entities = detect_entities(full_text)

    # 3. Redact PII based on OCR boxes
    output_path = os.path.join(OUTPUT_FOLDER, f"redacted_{file.filename}")
    redact_pdf(file_path, pii_entities, word_boxes_per_page, output_path)

    return FileResponse(output_path, media_type="application/pdf", filename=f"redacted_{file.filename}")
