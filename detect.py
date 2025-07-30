from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
from gliner import GLiNER

# Load model once
model = GLiNER.from_pretrained("urchade/gliner_base")

# Master list of supported labels
ALL_LABELS = [
    "person", "email_address", "phone", "address", "city", "country",
    "id_number", "credit_card", "account_number", "license_number",
    "organization", "date", "time", "doctor", "patient_id", "dob", "location", "medical_condition", "body_part", "age"
]

def detect_entities(text, labels):
    return model.predict_entities(text, labels=labels)
