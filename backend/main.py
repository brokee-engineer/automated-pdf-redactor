from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil, tempfile, os, json

from ocr import extract_text_with_boxes
from detect import detect_entities
from redact import redact_pdf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your Vercel domain
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/redact")
async def redact(pdf: UploadFile, tags: str = Form(...)):
    labels = json.loads(tags)
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, pdf.filename)

    with open(input_path, "wb") as f:
        shutil.copyfileobj(pdf.file, f)

    ocr = extract_text_with_boxes(input_path)
    full_text = "\n".join(" ".join(word["text"] for word in page) for page in ocr)
    entities = detect_entities(full_text, labels)
    output_path = os.path.join(temp_dir, f"redacted_{pdf.filename}")
    redact_pdf(input_path, entities, ocr, output_path)

    return FileResponse(output_path, filename=f"redacted_{pdf.filename}")
