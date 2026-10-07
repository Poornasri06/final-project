import sys
import os
import json

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.connection import SessionLocal
from app.agents.orchestrator import MultiAgentOrchestrator
from app.models.models import ResearchSession, Document, DocumentChunk

def test_pipeline():
    db = SessionLocal()
    try:
        # Check DB counts
        doc_count = db.query(Document).count()
        chunk_count = db.query(DocumentChunk).count()
        print(f"=== Knowledge Base Status ===")
        print(f"Total Real WHO Documents in DB: {doc_count}")
        print(f"Total Chunks in DB: {chunk_count}")
        
        docs = db.query(Document).all()
        for d in docs:
            c_cnt = db.query(DocumentChunk).filter(DocumentChunk.document_id == d.id).count()
            print(f" - [{d.category}] {d.title} ({d.file_path}): {c_cnt} chunks, {d.total_pages} pages")
        
        print("\n=== Running Live Medical Research Test ===")
        orchestrator = MultiAgentOrchestrator(db)
        
        test_questions = [
            ("What are the clinical diagnostic criteria and symptoms of pulmonary tuberculosis according to WHO guidelines?", "Tuberculosis"),
            ("What are the blood pressure thresholds for diagnosing hypertension and recommended lifestyle modifications?", "Hypertension"),
            ("What are the emergency signs and triage priorities for severe illness in children?", "Hospital Care - Children"),
            ("What is quantum computing algorithm for Shor factorization?", None)
        ]
        
        for q, cat in test_questions:
            print(f"\n" + "="*80)
            print(f"QUESTION: {q}")
            print(f"CATEGORY FILTER: {cat}")
            print("="*80)
            
            session = orchestrator.run_full_research_session(
                question=q,
                domain="healthcare",
                depth="comprehensive",
                use_knowledge_base=True,
                use_web_search=False,
                use_memory=False,
                category_filter=cat,
                max_reflection_cycles=1
            )
            
            print(f"\n[Session ID: {session.id}] Status: {session.status} in {session.execution_time_seconds:.2f}s")
            
            # Print Claims & Verification
            print(f"\nExtracted Claims ({len(session.claims)}):")
            for c in session.claims[:3]:
                print(f" - Claim: {c.claim_text}")
                print(f"   Status: {c.verification_status} | Confidence: {c.confidence_score}")
                for ce in c.claim_evidence_links:
                    safe_ev = ce.evidence.evidence_text[:120].encode('ascii', 'replace').decode('ascii')
                    safe_doc = ce.evidence.source.title.encode('ascii', 'replace').decode('ascii')
                    print(f"   Evidence [{ce.relationship_type}]: {safe_ev}... (Doc: {safe_doc}, Page: {ce.evidence.page_number})")
            
            # Print Reports
            if session.report:
                rep = session.report
                print(f"\nReport Title: {rep.title}")
                print(f"Report Summary (first 250 chars):\n{rep.executive_summary[:250]}...")
                has_disclaimer = "Medical & Clinical Safety Disclaimer" in rep.full_content_markdown or "Disclaimer" in rep.full_content_markdown
                print(f"Has Clinical Safety Disclaimer: {has_disclaimer}")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_pipeline()
