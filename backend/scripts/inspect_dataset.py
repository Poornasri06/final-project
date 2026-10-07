import os
import json
import PyPDF2

base = r"C:\Users\Admin\OneDrive\Desktop\final project\EVIDA_MEDICAL_DATASET"
meta_path = os.path.join(base, "metadata.json")
with open(meta_path, "r", encoding="utf-8") as f:
    meta = json.load(f)

print(f"Total documents configured: {len(meta)}")
for d in meta:
    pdf_path = os.path.join(base, d["folder"], d["filename"])
    if not os.path.exists(pdf_path):
        print(f"MISSING: {pdf_path}")
        continue
    reader = PyPDF2.PdfReader(pdf_path)
    # Sample text from middle page
    mid = len(reader.pages) // 2
    sample_text = reader.pages[mid].extract_text() or ""
    words = len(sample_text.split())
    print(f"[{d['category']}] {d['filename']}: {len(reader.pages)} pages, {os.path.getsize(pdf_path)} bytes, page {mid} words: {words}")
