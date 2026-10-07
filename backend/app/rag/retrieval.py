from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.models import DocumentChunk, Document
from app.rag.embedding import EmbeddingProvider
from app.database.connection import cosine_similarity

class VectorRetrievalService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_provider = EmbeddingProvider()

    def search_similar_chunks(
        self,
        query: str,
        top_k: int = 5,
        category_filter: Optional[str] = None,
        domain: str = "Healthcare"
    ) -> List[Dict[str, Any]]:
        """Perform semantic vector similarity search against indexed document chunks."""
        query_vector = self.embedding_provider.get_embedding(query)
        
        # Fetch candidate chunks from DB
        query_builder = self.db.query(DocumentChunk).join(Document)
        if category_filter and category_filter.lower() != "all":
            # Normalize common category name variations
            clean_cat = category_filter.replace("Care - ", "").replace("Care ", "").replace(" & ", " ").replace(" - ", " ").strip()
            query_builder = query_builder.filter(
                (DocumentChunk.category == category_filter) |
                (DocumentChunk.category.ilike(f"%{clean_cat}%"))
            )
            
        candidate_chunks = query_builder.all()
        
        scored_chunks = []
        for chunk in candidate_chunks:
            chunk_vec = chunk.embedding
            if not chunk_vec:
                continue
            
            score = cosine_similarity(query_vector, chunk_vec)
            
            scored_chunks.append({
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "document_name": chunk.document.title,
                "author": chunk.document.author or "Medical Advisory Panel",
                "publication_date": chunk.document.publication_date or "2025",
                "source_url": chunk.document.source_url or "",
                "page_number": chunk.page_number,
                "section": chunk.section,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "similarity_score": round(score, 4),
                "domain": chunk.domain,
                "category": chunk.category
            })
            
        # Sort descending by similarity score
        scored_chunks.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_chunks[:top_k]
