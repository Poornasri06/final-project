import uuid
import datetime
from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.connection import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="researcher")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    research_sessions = relationship("ResearchSession", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    title = Column(String(255), nullable=False)
    domain = Column(String(100), default="Healthcare")
    category = Column(String(100), default="General Healthcare") # Diabetes, Cardiovascular Disease, Hypertension, General Healthcare
    author = Column(String(255), nullable=True)
    publication_date = Column(String(100), nullable=True)
    source_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    file_path = Column(Text, nullable=True)
    file_size_bytes = Column(Integer, default=0)
    total_pages = Column(Integer, default=1)
    chunk_count = Column(Integer, default=0)
    processing_status = Column(String(50), default="READY") # UPLOADED, CLEANING, CHUNKING, EMBEDDING, READY, FAILED
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, default=1)
    section = Column(String(255), default="General")
    text = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    domain = Column(String(100), default="Healthcare")
    category = Column(String(100), default="General Healthcare")
    embedding = Column(JSON, nullable=True) # JSON stored vector array for compatibility
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    document = relationship("Document", back_populates="chunks")
    evidence_items = relationship("Evidence", back_populates="chunk")

class ResearchSession(Base):
    __tablename__ = "research_sessions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    title = Column(String(255), nullable=False)
    question = Column(Text, nullable=False)
    domain = Column(String(100), default="Healthcare")
    research_depth = Column(String(50), default="Standard") # Quick, Standard, Deep
    use_knowledge_base = Column(Boolean, default=True)
    use_web_search = Column(Boolean, default=True)
    use_memory = Column(Boolean, default=True)
    category_filter = Column(String(100), nullable=True)
    max_reflection_cycles = Column(Integer, default=3)
    current_reflection_cycle = Column(Integer, default=0)
    status = Column(String(50), default="COMPLETED") # INITIALIZED, PLANNING, RETRIEVING, VERIFYING, REFLECTING, COMPLETED, FAILED
    current_step_description = Column(String(255), default="Session ready")
    execution_time_seconds = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="research_sessions")
    plans = relationship("ResearchPlan", back_populates="session", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="session", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="session", cascade="all, delete-orphan")
    conflicts = relationship("Conflict", back_populates="session", cascade="all, delete-orphan")
    confidence = relationship("ConfidenceAssessment", back_populates="session", uselist=False, cascade="all, delete-orphan")
    critique = relationship("Critique", back_populates="session", uselist=False, cascade="all, delete-orphan")
    reflections = relationship("Reflection", back_populates="session", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="session", uselist=False, cascade="all, delete-orphan")

class ResearchPlan(Base):
    __tablename__ = "research_plans"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("research_sessions.id"), nullable=False)
    intent = Column(Text, nullable=False)
    subtopics = Column(JSON, default=list) # List[str]
    research_tasks = Column(JSON, default=list) # List[Dict]
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    session = relationship("ResearchSession", back_populates="plans")

class Source(Base):
    __tablename__ = "sources"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("research_sessions.id"), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=True)
    title = Column(String(255), nullable=False)
    url = Column(Text, nullable=True)
    domain = Column(String(100), default="Healthcare")
    source_type = Column(String(50), default="Knowledge Base Document") # Knowledge Base Document, Web Article, Medical Guidelines, Journal Paper
    author = Column(String(255), nullable=True)
    publication_date = Column(String(100), nullable=True)
    retrieved_date = Column(String(100), default=lambda: datetime.datetime.utcnow().strftime("%Y-%m-%d"))
    snippet = Column(Text, nullable=True)
    quality_assessment = Column(String(50), default="HIGH") # HIGH, MODERATE, LOW
    quality_explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    session = relationship("ResearchSession", back_populates="sources")
    evidence_list = relationship("Evidence", back_populates="source")
    evaluations = relationship("SourceEvaluation", back_populates="source", cascade="all, delete-orphan")

class Claim(Base):
    __tablename__ = "claims"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("research_sessions.id"), nullable=False)
    claim_text = Column(Text, nullable=False)
    claim_type = Column(String(100), default="Factual Claim") # Risk Factor, Clinical Outcome, Epidemiological Metric, Treatment Efficacy
    subtopic = Column(String(255), default="General")
    importance = Column(String(50), default="HIGH") # HIGH, MEDIUM, LOW
    verification_status = Column(String(50), default="SUPPORTED") # SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED, CONTRADICTED
    confidence_score = Column(Float, default=0.85)
    summary_reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    session = relationship("ResearchSession", back_populates="claims")
    claim_evidence_links = relationship("ClaimEvidence", back_populates="claim", cascade="all, delete-orphan")

class Evidence(Base):
    __tablename__ = "evidence"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_id = Column(String(36), ForeignKey("sources.id"), nullable=False)
    chunk_id = Column(String(36), ForeignKey("document_chunks.id"), nullable=True)
    evidence_text = Column(Text, nullable=False)
    section = Column(String(255), default="General")
    page_number = Column(Integer, default=1)
    relevance_score = Column(Float, default=0.90)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    source = relationship("Source", back_populates="evidence_list")
    chunk = relationship("DocumentChunk", back_populates="evidence_items")
    claim_links = relationship("ClaimEvidence", back_populates="evidence")

class ClaimEvidence(Base):
    __tablename__ = "claim_evidence"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(36), ForeignKey("claims.id"), nullable=False)
    evidence_id = Column(String(36), ForeignKey("evidence.id"), nullable=False)
    relationship_type = Column(String(50), default="SUPPORTED") # SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED, CONTRADICTED
    analysis_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    claim = relationship("Claim", back_populates="claim_evidence_links")
    evidence = relationship("Evidence", back_populates="claim_links")

class SourceEvaluation(Base):
    __tablename__ = "source_evaluations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_id = Column(String(36), ForeignKey("sources.id"), nullable=False)
    authority_score = Column(Float, default=0.9)
    relevance_score = Column(Float, default=0.9)
    recency_score = Column(Float, default=0.85)
    evidence_quality_score = Column(Float, default=0.88)
    overall_rating = Column(String(50), default="HIGH") # HIGH, MODERATE, LOW
    rationale = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    source = relationship("Source", back_populates="evaluations")

class Conflict(Base):
    __tablename__ = "conflicts"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("research_sessions.id"), nullable=False)
    topic = Column(String(255), nullable=False)
    claim_a_id = Column(String(36), ForeignKey("claims.id"), nullable=True)
    claim_b_id = Column(String(36), ForeignKey("claims.id"), nullable=True)
    source_a_id = Column(String(36), ForeignKey("sources.id"), nullable=True)
    source_b_id = Column(String(36), ForeignKey("sources.id"), nullable=True)
    explanation = Column(Text, nullable=False)
    methodological_differences = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    session = relationship("ResearchSession", back_populates="conflicts")

class ConfidenceAssessment(Base):
    __tablename__ = "confidence_assessments"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("research_sessions.id"), nullable=False)
    overall_confidence = Column(String(50), default="HIGH") # HIGH, MODERATE, LOW
    confidence_score = Column(Float, default=0.88)
    supporting_sources_count = Column(Integer, default=3)
    contradictory_sources_count = Column(Integer, default=0)
    unsupported_claims_count = Column(Integer, default=0)
    key_reasons = Column(JSON, default=list) # List[str]
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    session = relationship("ResearchSession", back_populates="confidence")

class Critique(Base):
    __tablename__ = "critiques"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("research_sessions.id"), nullable=False)
    unsupported_claims_count = Column(Integer, default=0)
    weak_evidence_count = Column(Integer, default=0)
    conflicts_count = Column(Integer, default=0)
    research_gaps_count = Column(Integer, default=0)
    gaps_description = Column(Text, nullable=True)
    recommendations = Column(JSON, default=list) # List[str]
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    session = relationship("ResearchSession", back_populates="critique")

class Reflection(Base):
    __tablename__ = "reflections"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("research_sessions.id"), nullable=False)
    cycle_index = Column(Integer, nullable=False)
    need_additional_research = Column(Boolean, default=False)
    reflection_notes = Column(Text, nullable=False)
    new_subtopics_to_search = Column(JSON, default=list) # List[str]
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    session = relationship("ResearchSession", back_populates="reflections")

class MemoryItem(Base):
    __tablename__ = "memory_items"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("research_sessions.id"), nullable=True)
    previous_question = Column(Text, nullable=False)
    key_finding = Column(Text, nullable=False)
    source_title = Column(String(255), nullable=False)
    relevance_tag = Column(String(100), default="Healthcare")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("research_sessions.id"), nullable=False)
    title = Column(String(255), nullable=False)
    executive_summary = Column(Text, nullable=False)
    methodology = Column(Text, nullable=False)
    full_content_markdown = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    session = relationship("ResearchSession", back_populates="report")
    citations = relationship("Citation", back_populates="report", cascade="all, delete-orphan")

class Citation(Base):
    __tablename__ = "citations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_id = Column(String(36), ForeignKey("reports.id"), nullable=False)
    citation_number = Column(Integer, nullable=False) # e.g. 1 for [1]
    source_id = Column(String(36), ForeignKey("sources.id"), nullable=False)
    citation_text = Column(Text, nullable=False)
    
    report = relationship("Report", back_populates="citations")
