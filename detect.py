from transformers import AutoTokenizer, AutoModelForTokenClassification
from gliner import GLiNER
import torch

model = GLiNER.from_pretrained("urchade/gliner_base")

def detect_entities(text):
    found_entities = model.predict_entities(
        text,
        labels=[
            "person", "email_address", "phone", "address", "city", "country",
            "id_number", "credit_card",  "account_number", "license_number", 
            "organization", "date", "time"
        ]
    )

    return found_entities