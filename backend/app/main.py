import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.connection import engine, Base, SessionLocal
from app.knowledge_base.loader import ensure_real_dataset_loaded
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.research import router as research_router
from app.api.knowledge_base import router as kb_router
from app.api.memory import router as memory_router
from app.api.evaluation import router as eval_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("evida.main")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Evidence Verification & Intelligent Domain Analysis System for Healthcare Research"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(research_router)
app.include_router(kb_router)
app.include_router(memory_router)
app.include_router(eval_router)

@app.on_event("startup")
def startup_event():
    logger.info("Initializing database schema...")
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            ensure_real_dataset_loaded(db)
        finally:
            db.close()
        logger.info("Application startup complete. Ready for evidence verification requests.")
    except Exception as e:
        logger.error(f"Startup database initialization error: {str(e)}")

@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "domain": settings.DOMAIN,
        "llm_provider": settings.LLM_PROVIDER,
        "embedding_provider": settings.EMBEDDING_PROVIDER
    }
