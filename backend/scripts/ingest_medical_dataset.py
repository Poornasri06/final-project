import os
import sys
import json
import logging
from typing import Dict, Any, List

# Ensure backend root is on sys.path
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from app.database.connection import SessionLocal, Base, engine
from app.models.models import Document, DocumentChunk, User
from app.rag.chunker import RecursiveStructureChunker
from app.rag.embedding import EmbeddingProvider
from app.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("evida.ingestion")

def get_or_create_admin_user(db):
    user = db.query(User).filter(User.email == "researcher@evida.health").first()
    if not user:
        # Check if old demo user exists, or create clinical researcher user
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

def ingest_dataset():
    # Make sure DB schema is created
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Step 1: Purge any old demo documents
        old_demo_docs = db.query(Document).filter(Document.is_demo == True).all()
        if old_demo_docs:
            logger.info(f"Removing {len(old_demo_docs)} old demo documents from database...")
            for d in old_demo_docs:
                db.query(DocumentChunk).filter(DocumentChunk.document_id == d.id).delete()
                db.delete(d)
            db.commit()

        user = get_or_create_admin_user(db)
        chunker = RecursiveStructureChunker(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
        embedder = EmbeddingProvider()

        dataset_dir = os.path.abspath(os.path.join(backend_root, "..", "EVIDA_MEDICAL_DATASET"))
        meta_file = os.path.join(dataset_dir, "metadata.json")

        if not os.path.exists(dataset_dir):
            raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")

        doc_metadata_map: Dict[str, Dict[str, Any]] = {}
        if os.path.exists(meta_file):
            with open(meta_file, "r", encoding="utf-8") as f:
                meta_list = json.load(f)
                for item in meta_list:
                    doc_metadata_map[item["filename"]] = item

        # Step 2: Discover all PDF files recursively
        discovered_pdfs = []
        for root, _, files in os.walk(dataset_dir):
            for file in sorted(files):
                if file.lower().endswith(".pdf"):
                    discovered_pdfs.append((os.path.join(root, file), file))

        total_found = len(discovered_pdfs)
        total_processed = 0
        total_failed = 0
        total_pages = 0
        total_chunks = 0
        total_embeddings = 0
        categories_processed = set()

        for pdf_path, filename in discovered_pdfs:
            logger.info(f"Processing PDF: {filename}...")
            meta = doc_metadata_map.get(filename, {})
            title = meta.get("title", filename.replace(".pdf", "").replace("_", " "))
            category = meta.get("category", "General Healthcare")
            domain = meta.get("domain", "Healthcare Research")
            author = meta.get("author", "World Health Organization")
            pub_date = meta.get("publication_date", "2023")
            source_url = meta.get("source_url", "https://iris.who.int")
            doc_type = meta.get("document_type", "Official Clinical Guideline")

            # Check if this real document is already ingested
            existing_doc = db.query(Document).filter(
                (Document.title == title) | (Document.file_path == pdf_path)
            ).first()

            if existing_doc and existing_doc.chunk_count > 0:
                logger.info(f"Document '{title}' already indexed with {existing_doc.chunk_count} chunks. Skipping.")
                total_processed += 1
                total_pages += existing_doc.total_pages
                total_chunks += existing_doc.chunk_count
                total_embeddings += existing_doc.chunk_count
                categories_processed.add(category)
                continue

            try:
                # Extract text page by page
                pages_content = chunker.extract_text_from_pdf(pdf_path)
                file_size = os.path.getsize(pdf_path)
                page_count = len(pages_content)
                total_pages += page_count

                # Create Document entity
                if existing_doc:
                    doc = existing_doc
                    # Clear old chunks if any
                    db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()
                else:
                    doc = Document(
                        user_id=user.id,
                        title=title,
                        domain="Healthcare",
                        category=category,
                        author=author,
                        publication_date=pub_date,
                        source_url=source_url,
                        description=f"{doc_type} published by {author} on {category}.",
                        file_path=pdf_path,
                        file_size_bytes=file_size,
                        total_pages=page_count,
                        processing_status="PROCESSING",
                        is_demo=False
                    )
                    db.add(doc)
                    db.flush()

                # Chunk document
                raw_chunks = chunker.chunk_document(
                    document_id=doc.id,
                    document_title=doc.title,
                    pages_content=pages_content,
                    domain=domain,
                    category=category
                )

                # Generate embeddings & create chunk models
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
                doc.processing_status = "READY"
                db.commit()

                total_chunks += len(chunk_models)
                total_embeddings += len(chunk_models)
                total_processed += 1
                categories_processed.add(category)
                logger.info(f"Ingested '{title}': {page_count} pages, {len(chunk_models)} chunks.")

            except Exception as e:
                db.rollback()
                logger.error(f"Failed to ingest '{filename}': {str(e)}")
                total_failed += 1

        db.close()

        # Print formatted summary report required by specifications
        print("\n" + "=" * 50)
        print("E.V.I.D.A. MEDICAL KNOWLEDGE BASE")
        print("=" * 50)
        print(f"\nDocuments found: {total_found}\n")
        print(f"Documents processed: {total_processed}")
        print(f"Documents failed: {total_failed}\n")
        print(f"Total pages: {total_pages}")
        print(f"Total chunks: {total_chunks}")
        print(f"Total embeddings: {total_embeddings}\n")
        print("Categories:")
        for cat in sorted(categories_processed):
            print(f"  {cat}")
        print("\nIngestion completed successfully.")
        print("=" * 50 + "\n")

    except Exception as e:
        logger.error(f"Ingestion pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    ingest_dataset()
