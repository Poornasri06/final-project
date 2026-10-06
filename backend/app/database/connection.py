import os
import math
import logging
from sqlalchemy import create_engine, event, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

logger = logging.getLogger("evida.db")

Base = declarative_base()

# Determine database engine
DB_URL = settings.DATABASE_URL
engine = None
IS_SQLITE = False

try:
    if "postgresql" in DB_URL:
        engine = create_engine(DB_URL, pool_pre_ping=True)
        # Test connection
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        logger.info("Connected successfully to PostgreSQL database.")
    else:
        raise Exception("Not PostgreSQL URL")
except Exception as e:
    logger.warning(f"PostgreSQL connection failed ({e}). Falling back to local SQLite database with vector emulation.")
    sqlite_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evida_local.db")
    engine = create_engine(f"sqlite:///{sqlite_db_path}", connect_args={"check_same_thread": False})
    IS_SQLITE = True

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Custom vector similarity calculation for SQLite fallback
def cosine_similarity(vec1, vec2):
    if not vec1 or not vec2:
        return 0.0
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)
