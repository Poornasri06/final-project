from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.models import MemoryItem
from app.agents.memory_agent import MemoryAgent

router = APIRouter(prefix="/api/memory", tags=["Memory"])
memory_agent = MemoryAgent()

@router.get("")
def get_memory_items(db: Session = Depends(get_db)):
    items = db.query(MemoryItem).order_by(MemoryItem.created_at.desc()).all()
    return [
        {
            "id": i.id,
            "previous_question": i.previous_question,
            "finding": i.key_finding,
            "source_title": i.source_title,
            "relevance_tag": i.relevance_tag,
            "created_at": i.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for i in items
    ]

@router.post("/search")
def search_memory(question: str = Query(...), db: Session = Depends(get_db)):
    return memory_agent.search_memory(db, question, top_k=3)
