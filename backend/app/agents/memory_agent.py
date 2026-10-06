from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import MemoryItem
from app.rag.embedding import EmbeddingProvider
from app.database.connection import cosine_similarity

class MemoryAgent:
    def __init__(self):
        self.embedding_provider = EmbeddingProvider()

    def search_memory(self, db: Session, question: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search previous research sessions for relevant past findings."""
        items = db.query(MemoryItem).all()
        if not items:
            return []

        q_vec = self.embedding_provider.get_embedding(question)
        scored = []
        for item in items:
            item_vec = self.embedding_provider.get_embedding(item.previous_question + " " + item.key_finding)
            score = cosine_similarity(q_vec, item_vec)
            if score > 0.4:  # Threshold relevance
                scored.append({
                    "id": item.id,
                    "previous_question": item.previous_question,
                    "finding": item.key_finding,
                    "source": item.source_title,
                    "date": item.created_at.strftime("%Y-%m-%d"),
                    "relevance_score": round(score, 3)
                })

        scored.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored[:top_k]
