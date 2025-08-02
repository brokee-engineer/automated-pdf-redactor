import fitz  # PyMuPDF

def normalize(text):
    """Lowercase and strip non-alphanumeric characters for reliable matching."""
    return ''.join(e.lower() for e in text if e.isalnum())

def is_vertically_aligned(span_words, threshold=10):
    """Check if all words in a span are horizontally aligned (same line)."""
    y_positions = [w['bbox'][1] for w in span_words]
    return max(y_positions) - min(y_positions) <= threshold

def redact_pdf(pdf_path, pii_results, ocr_results, output_path):
    doc = fitz.open(pdf_path)

    pii_set = set()
    for ent in pii_results:
        if ent.get("text"):
            text = normalize(ent['text'])
            pii_set.add(text)
            # Also add base form without possessive suffix for redaction purposes
            if text.endswith("s"):
                pii_set.add(text.rstrip("s"))
            elif text.endswith("’s") or text.endswith("'s"):
                pii_set.add(text.rstrip("’s").rstrip("'s"))

    for page_num, page in enumerate(doc):
        if page_num >= len(ocr_results):
            continue

        ocr_words = ocr_results[page_num]
        num_words = len(ocr_words)

        print(f"\n[PAGE {page_num + 1}]")
        print(f"PII Entities on Page: {list(pii_set)}")

        i = 0
        while i < num_words:
            matched = False

            # Try 5,4,3,2,1-word spans in decreasing order
            for window in range(5, 0, -1):
                if i + window > num_words:
                    continue

                span_words = ocr_words[i:i + window]
                span_text_raw = ''.join(w['text'] for w in span_words)
                span_text_norm = normalize(span_text_raw)
                span_text_base = span_text_norm.rstrip("’s").rstrip("'s")

                if (span_text_norm in pii_set or span_text_base in pii_set) and is_vertically_aligned(span_words):
                    # Get combined bounding box for horizontally aligned words
                    x0 = min(w['bbox'][0] for w in span_words)
                    y0 = min(w['bbox'][1] for w in span_words)
                    x1 = max(w['bbox'][0] + w['bbox'][2] for w in span_words)
                    y1 = max(w['bbox'][1] + w['bbox'][3] for w in span_words)

                    rect = fitz.Rect(x0, y0, x1, y1)
                    page.add_redact_annot(rect, fill=(0, 0, 0))
                    print(f"[MATCHED & REDACTED] '{span_text_raw}' at {rect}")
                    i += window
                    matched = True
                    break  # stop checking shorter spans

            if not matched:
                print(f"[SKIPPED] '{ocr_words[i]['text']}'")
                i += 1

        page.apply_redactions()

    doc.save(output_path)
    doc.close()