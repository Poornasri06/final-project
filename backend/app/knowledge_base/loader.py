import os
import sys
import json
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.models import Document, DocumentChunk, User
from app.rag.chunker import RecursiveStructureChunker
from app.rag.embedding import EmbeddingProvider
from app.config import settings

logger = logging.getLogger("evida.knowledge_base")

def get_or_create_researcher_user(db: Session) -> User:
    user = db.query(User).filter(User.email == "researcher@evida.health").first()
    if not user:
        import hashlib
        pwd_hash = hashlib.sha256("evida2026_clinical_research".encode()).hexdigest()
        user = User(
            email="researcher@evida.health",
            full_name="WHO Evidence Researcher",
            password_hash=pwd_hash,
            role="admin"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def ensure_real_dataset_loaded(db: Session) -> int:
    """Ensure that the real WHO Healthcare Knowledge Base is indexed in the database."""
    # First purge any legacy demo documents if any exist
    legacy_demos = db.query(Document).filter(Document.is_demo == True).all()
    if legacy_demos:
        logger.info(f"Purging {len(legacy_demos)} legacy demo documents...")
        for ld in legacy_demos:
            db.query(DocumentChunk).filter(DocumentChunk.document_id == ld.id).delete()
            db.delete(ld)
        db.commit()

    real_docs_count = db.query(Document).filter(Document.is_demo == False).count()
    if real_docs_count >= 8:
        logger.info(f"Knowledge Base already contains {real_docs_count} verified WHO clinical documents.")
        return real_docs_count

    logger.info("Initializing WHO Clinical Knowledge Base indexing...")
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    dataset_dir = os.path.abspath(os.path.join(backend_root, "..", "EVIDA_MEDICAL_DATASET"))
    meta_file = os.path.join(dataset_dir, "metadata.json")

    if not os.path.exists(dataset_dir) or not os.path.exists(meta_file):
        logger.warning(f"Medical dataset directory not found at {dataset_dir}")
        return real_docs_count

    with open(meta_file, "r", encoding="utf-8") as f:
        meta_list = json.load(f)

    user = get_or_create_researcher_user(db)
    chunker = RecursiveStructureChunker(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
    embedder = EmbeddingProvider()

    for item in meta_list:
        pdf_path = os.path.join(dataset_dir, item["folder"], item["filename"])
        if not os.path.exists(pdf_path):
            continue

        existing = db.query(Document).filter(Document.title == item["title"]).first()
        if existing and existing.chunk_count > 0:
            continue

        try:
            pages = chunker.extract_text_from_pdf(pdf_path)
            doc = Document(
                user_id=user.id,
                title=item["title"],
                domain="Healthcare",
                category=item["category"],
                author=item.get("author", "World Health Organization"),
                publication_date=item.get("publication_date", "2023"),
                source_url=item.get("source_url", "https://iris.who.int"),
                description=f"{item.get('document_type', 'Clinical Guideline')} published by {item.get('author', 'WHO')}.",
                file_path=pdf_path,
                file_size_bytes=os.path.getsize(pdf_path),
                total_pages=len(pages),
                processing_status="READY",
                is_demo=False
            )
            db.add(doc)
            db.flush()

            raw_chunks = chunker.chunk_document(
                document_id=doc.id,
                document_title=doc.title,
                pages_content=pages,
                domain=item.get("domain", "Healthcare Research"),
                category=item["category"]
            )

            chunk_models = []
            for rc in raw_chunks:
                vec = embedder.get_embedding(rc["text"])
                chunk_obj = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=rc["chunk_index"],
                    page_number=rc["page_number"],
                    section=rc["section"],
                    text=rc["text"],
                    token_count=rc["token_count"],
                    domain=rc["domain"],
                    category=rc["category"],
                    embedding=vec
                )
                chunk_models.append(chunk_obj)

            db.add_all(chunk_models)
            doc.chunk_count = len(chunk_models)
            db.commit()
            logger.info(f"Indexed '{doc.title}': {len(chunk_models)} chunks.")
        except Exception as e:
            db.rollback()
            logger.error(f"Error indexing {item['filename']}: {e}")

    return db.query(Document).filter(Document.is_demo == False).count()
