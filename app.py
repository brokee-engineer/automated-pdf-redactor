import streamlit as st
from ocr import extract_text_with_boxes
from detect import detect_entities, ALL_LABELS
from redact import redact_pdf
import os
import tempfile
import shutil

st.set_page_config(page_title="PDF Redactor", layout="centered")

st.title("SafeDocs : Automated PDF Redactor")
st.markdown(
    "Upload a PDF file to automatically find and hide sensitive personal information. "
    "SafeDocs helps protect your privacy - so you don’t have to worry."
)

# --- Helper: Normalize uppercase names like "DOE, REGINA" to "Doe, Regina"
def normalize_text_for_ner(text):
    lines = text.split("\n")
    processed = []
    for line in lines:
        if line.isupper() and "," in line:
            processed.append(line.title())  # DOE, REGINA -> Doe, Regina
        else:
            processed.append(line)
    return "\n".join(processed)

# --- Upload PDF ---
uploaded_file = st.file_uploader("📄 Upload your PDF file :", type=["pdf"])

# --- Custom Entity Selection from detect.ALL_LABELS ---
st.markdown("### 🏷️ Select What You Want Hidden")
selected_labels = st.multiselect("Entity Tags :", ALL_LABELS, default=ALL_LABELS)

if uploaded_file is not None:
    with st.spinner("Processing. Please wait..."):
        # Save the uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        input_path = os.path.join(temp_dir, uploaded_file.name)

        with open(input_path, "wb") as f:
            f.write(uploaded_file.read())

        # Step 1: OCR
        word_boxes_per_page = extract_text_with_boxes(input_path)

        # Step 2: PII Detection
        full_text = "\n".join(" ".join(word["text"] for word in page) for page in word_boxes_per_page)
        processed_text = normalize_text_for_ner(full_text)  # ✅ Normalize names before detection
        pii_entities = detect_entities(processed_text, selected_labels)

        # Step 3: Redaction
        output_path = os.path.join(temp_dir, f"redacted_{uploaded_file.name}")
        redact_pdf(input_path, pii_entities, word_boxes_per_page, output_path)

        # Step 4: Download button
        st.success("Your file has been successfully redacted.")
        st.download_button(
            label="💾 Download Redacted PDF",
            data=open(output_path, "rb").read(),
            file_name=f"redacted_{uploaded_file.name}",
            mime="application/pdf"
        )

        shutil.rmtree(temp_dir)
