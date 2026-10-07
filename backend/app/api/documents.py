import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.models import Document, DocumentChunk
from app.models.schemas import DocumentResponse, DocumentChunkResponse
from app.rag.chunker import RecursiveStructureChunker
from app.rag.embedding import EmbeddingProvider

router = APIRouter(prefix="/api/documents", tags=["Documents"])
chunker = RecursiveStructureChunker(chunk_size=600, chunk_overlap=75)
embedder = EmbeddingProvider()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("", response_model=List[DocumentResponse])
def list_documents(category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Document)
    if category and category.lower() != "all":
        clean_cat = category.replace("Care - ", "").replace("Care ", "").replace(" & ", " ").replace(" - ", " ").strip()
        query = query.filter((Document.category == category) | (Document.category.ilike(f"%{clean_cat}%")))
    docs = query.order_by(Document.created_at.desc()).all()
    
    res = []
    for d in docs:
        res.append(DocumentResponse(
            id=d.id,
            title=d.title,
            domain=d.domain,
            category=d.category,
            author=d.author,
            publication_date=d.publication_date,
            source_url=d.source_url,
            description=d.description,
            file_size_bytes=d.file_size_bytes or 0,
            total_pages=d.total_pages or 1,
            chunk_count=d.chunk_count or 0,
            processing_status=d.processing_status or "READY",
            is_demo=d.is_demo or False,
            created_at=d.created_at.strftime("%Y-%m-%d %H:%M")
        ))
    return res

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("General Healthcare"),
    author: Optional[str] = Form(None),
    publication_date: Optional[str] = Form(None),
    source_url: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(('.pdf', '.txt', '.docx')):
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF, TXT, or DOCX.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)

    # 1. Save Document record
    doc = Document(
        title=title,
        domain="Healthcare",
        category=category,
        author=author,
        publication_date=publication_date or "2025",
        source_url=source_url,
        description=description,
        file_path=file_path,
        file_size_bytes=file_size,
        processing_status="PROCESSING"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    try:
        pages_content = []
        if file.filename.endswith('.pdf'):
            pages_content = chunker.extract_text_from_pdf(file_path)
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
                pages_content = [{"page_number": 1, "text": chunker.clean_text(text)}]

        doc.total_pages = len(pages_content)

        # Chunk document
        chunks_data = chunker.chunk_document(
            document_id=doc.id,
            document_title=doc.title,
            pages_content=pages_content,
            domain="Healthcare",
            category=category
        )

        chunk_models = []
        for c in chunks_data:
            vec = embedder.get_embedding(c["text"])
            chunk_m = DocumentChunk(
                document_id=doc.id,
                chunk_index=c["chunk_index"],
                page_number=c["page_number"],
                section=c["section"],
                text=c["text"],
                token_count=c["token_count"],
                domain=c["domain"],
                category=c["category"],
                embedding=vec
            )
            chunk_models.append(chunk_m)

        db.add_all(chunk_models)
        doc.chunk_count = len(chunk_models)
        doc.processing_status = "READY"
        db.commit()
        db.refresh(doc)

        return DocumentResponse(
            id=doc.id,
            title=doc.title,
            domain=doc.domain,
            category=doc.category,
            author=doc.author,
            publication_date=doc.publication_date,
            source_url=doc.source_url,
            description=doc.description,
            file_size_bytes=doc.file_size_bytes,
            total_pages=doc.total_pages,
            chunk_count=doc.chunk_count,
            processing_status=doc.processing_status,
            is_demo=False,
            created_at=doc.created_at.strftime("%Y-%m-%d %H:%M")
        )

    except Exception as e:
        doc.processing_status = "FAILED"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@router.get("/{id}/chunks", response_model=List[DocumentChunkResponse])
def get_document_chunks(id: str, db: Session = Depends(get_db)):
    chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == id).order_by(DocumentChunk.chunk_index.asc()).all()
    res = []
    for c in chunks:
        res.append(DocumentChunkResponse(
            id=c.id,
            chunk_index=c.chunk_index,
            page_number=c.page_number,
            section=c.section,
            text=c.text,
            token_count=c.token_count,
            domain=c.domain
        ))
    return res

@router.delete("/{id}")
def delete_document(id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted successfully"}
