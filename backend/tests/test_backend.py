import pytest
from app.rag.chunker import RecursiveStructureChunker
from app.agents.verification_agent import EvidenceVerificationAgent
from app.agents.conflict_agent import ConflictDetectionAgent

def test_chunker():
    chunker = RecursiveStructureChunker(chunk_size=50, chunk_overlap=10)
    pages = [
        {"page_number": 1, "text": "SECTION: DIABETES GUIDELINES\nType 2 diabetes risk factors include elevated body mass index, sedentary lifestyle, and genetic family history. Early screening is recommended."},
        {"page_number": 2, "text": "SECTION: TREATMENT\nMetformin remains the primary first-line pharmacotherapy for glycemic control."}
    ]
    chunks = chunker.chunk_document("doc123", "ADA Guidelines", pages, "Healthcare", "Diabetes")
    assert len(chunks) >= 2
    assert chunks[0]["document_id"] == "doc123"
    assert "token_count" in chunks[0]

def test_evidence_verification():
    verifier = EvidenceVerificationAgent()
    claim = "Elevated HbA1c levels increase diabetic microvascular risk."
    candidates = [
        {"text": "HbA1c levels above 6.5% strongly correlate with microvascular complications like retinopathy.", "document_name": "ADA Guidelines", "page_number": 1}
    ]
    res = verifier.verify_claim(claim, candidates, [])
    assert res["verification_status"] in ["SUPPORTED", "PARTIALLY_SUPPORTED"]
    assert res["confidence_score"] > 0.5

def test_conflict_detection():
    detector = ConflictDetectionAgent()
    claims = [
        {"claim_text": "Intensive lifestyle modification yields 58% risk reduction.", "verification_status": "PARTIALLY_SUPPORTED", "subtopic": "Lifestyle"}
    ]
    conflicts = detector.detect_conflicts(claims, ["ADA Guidelines", "Observational Study"])
    assert len(conflicts) > 0
    assert "topic" in conflicts[0]
