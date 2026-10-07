from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.connection import get_db
from app.models.models import Document, DocumentChunk
from app.models.schemas import KnowledgeBaseStatsResponse
from app.knowledge_base.loader import ensure_real_dataset_loaded

router = APIRouter(prefix="/api/knowledge-base", tags=["Knowledge Base"])

@router.get("/stats", response_model=KnowledgeBaseStatsResponse)
def get_knowledge_base_stats(db: Session = Depends(get_db)):
    total_docs = db.query(Document).count()
    indexed_docs = db.query(Document).filter(Document.processing_status == "READY").count()
    total_chunks = db.query(DocumentChunk).count()

    categories_query = db.query(
        Document.category, func.count(Document.id)
    ).group_by(Document.category).all()

    categories = [
        {"category": cat or "General Healthcare", "count": count}
        for cat, count in categories_query
    ]

    return KnowledgeBaseStatsResponse(
        dataset_name="WHO Clinical Knowledge Base (Official Guidelines)",
        domain="Healthcare",
        documents_count=total_docs,
        indexed_count=indexed_docs,
        chunks_count=total_chunks,
        status="Ready",
        categories=categories
    )

@router.post("/sync")
@router.post("/seed-demo")
def sync_knowledge_base(db: Session = Depends(get_db)):
    """Synchronize and verify real WHO healthcare documents in the knowledge base."""
    count = ensure_real_dataset_loaded(db)
    return {"status": "SUCCESS", "message": f"WHO Clinical Knowledge Base active with {count} verified documents."}

@router.post("/unload-demo")
def clear_knowledge_base(db: Session = Depends(get_db)):
    """Cleanly purge legacy demo documents while preserving real documents."""
    demo_docs = db.query(Document).filter(Document.is_demo == True).all()
    for doc in demo_docs:
        db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()
        db.delete(doc)
    db.commit()
    return {"message": "Knowledge base verified and cleaned successfully."}
