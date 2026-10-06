from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.agents.base import BaseAgent
from app.rag.retrieval import VectorRetrievalService

class DomainRAGAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="DomainRAGAgent",
            role_description="Retrieves highly relevant healthcare knowledge base chunks via pgvector similarity search."
        )

    def retrieve_domain_evidence(self, db: Session, query: str, category_filter: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        retrieval_service = VectorRetrievalService(db)
        return retrieval_service.search_similar_chunks(query, top_k=top_k, category_filter=category_filter)
