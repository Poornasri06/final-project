from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.connection import get_db
from app.models.models import Document, DocumentChunk
from app.models.schemas import KnowledgeBaseStatsResponse
from app.demo_dataset.seeder import seed_database_if_empty

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
        dataset_name="Healthcare Research Knowledge Base",
        domain="Healthcare",
        documents_count=total_docs,
        indexed_count=indexed_docs,
        chunks_count=total_chunks,
        status="Ready",
        categories=categories
    )

@router.post("/seed-demo")
def seed_demo_dataset(db: Session = Depends(get_db)):
    """Explicitly seed demo healthcare documents into the knowledge base upon user request."""
    seed_database_if_empty(db, force=True)
    return {"message": "Demo healthcare dataset loaded successfully"}

@router.post("/unload-demo")
def unload_demo_dataset(db: Session = Depends(get_db)):
    """Unload/remove demo healthcare documents from the knowledge base."""
    demo_docs = db.query(Document).filter(Document.is_demo == True).all()
    for doc in demo_docs:
        db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()
        db.delete(doc)
    db.commit()
    return {"message": "Demo healthcare dataset unloaded successfully"}
