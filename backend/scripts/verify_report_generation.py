import os
import sys
import json

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import PyPDF2
from fastapi.testclient import TestClient
from app.main import app

def verify_reports():
    sys.stdout.reconfigure(encoding='utf-8')
    print("="*60)
    print("=== Testing E.V.I.D.A. English Clinical Report & PDF System ===")
    print("="*60)
    
    client = TestClient(app)
    
    # 1. Fetch sessions
    res = client.get("/api/research")
    assert res.status_code == 200, f"Failed to list sessions: {res.status_code}"
    sessions = res.json()
    print(f"Total Research Sessions Available: {len(sessions)}")
    
    if not sessions:
        print("No sessions available to test.")
        return

    sample_session = sessions[0]
    sid = sample_session['id']
    question = sample_session['question']
    print(f"\nTesting Session ID: {sid}")
    print(f"Question: {question}")
    
    # 2. Formatted Report English
    print("\n--- 1. Testing English Formatted Report Endpoint ---")
    res_en = client.get(f"/api/research/{sid}/formatted-report")
    assert res_en.status_code == 200, f"English report failed: {res_en.status_code}"
    data_en = res_en.json()
    print(f"Report Title: {data_en['report_title']}")
    print(f"Language: {data_en['language_name']}")
    print(f"Executive Summary: {data_en['executive_summary'][:120]}...")
    print(f"Methodology Steps: {len(data_en['methodology_steps'])}")
    print(f"Sources Count: {len(data_en['sources'])}")
    print(f"Key Findings Count: {len(data_en['key_findings'])}")
    print(f"Claims Table Rows: {len(data_en['claims_table'])}")
    print(f"Confidence: {data_en['confidence']['rating']} ({data_en['confidence']['score_percent']}%)")
    print(f"Has Medical Disclaimer: {bool(data_en['disclaimer'])}")

    assert len(data_en['methodology_steps']) == 10, "Should have 10 methodology steps"
    assert data_en['language'] == 'en'
    assert "E.V.I.D.A." in data_en['disclaimer']

    # 3. English PDF Download
    print("\n--- 2. Testing Clinical English PDF Download ---")
    res_pdf_en = client.get(f"/api/research/{sid}/pdf")
    assert res_pdf_en.status_code == 200, f"English PDF failed: {res_pdf_en.status_code}"
    pdf_en = res_pdf_en.content
    print(f"English PDF Downloaded: {len(pdf_en)} bytes | Header Content-Type: {res_pdf_en.headers.get('content-type')}")
    assert len(pdf_en) > 20000, f"English PDF size too small ({len(pdf_en)} bytes)!"
    assert pdf_en[:4] == b'%PDF', "Invalid PDF magic header!"
    assert "attachment" in res_pdf_en.headers.get("content-disposition", "")
    assert f"EVIDA_Clinical_Report_{sid[:8]}.pdf" in res_pdf_en.headers.get("content-disposition", "")

    # Save to disk and inspect with PyPDF2
    en_file = os.path.join(os.path.dirname(__file__), "test_verified_en.pdf")
    with open(en_file, "wb") as f:
        f.write(pdf_en)
    reader_en = PyPDF2.PdfReader(en_file)
    print(f"English PDF Page Count: {len(reader_en.pages)}")
    en_text = "".join([p.extract_text() for p in reader_en.pages])
    assert "EXECUTIVE SUMMARY" in en_text, "Missing Executive Summary in English PDF"
    assert "RESEARCH SOURCES" in en_text, "Missing Research Sources in English PDF"
    assert "CLAIMS AND EVIDENCE" in en_text, "Missing Claims & Evidence in English PDF"
    assert "CONFIDENCE ASSESSMENT" in en_text, "Missing Confidence in English PDF"
    assert "MEDICAL DISCLAIMER" in en_text, "Missing Disclaimer in English PDF"
    print("English PDF content verification passed!")

    print("\n" + "="*60)
    print("ALL CLINICAL REPORT & PDF TESTS PASSED!")
    print("="*60)

if __name__ == "__main__":
    verify_reports()
