from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field

# User Schemas
class UserRegister(BaseModel):
    email: str
    full_name: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Document Schemas
class DocumentCreate(BaseModel):
    title: str
    domain: str = "Healthcare"
    category: str = "General Healthcare"
    author: Optional[str] = None
    publication_date: Optional[str] = None
    source_url: Optional[str] = None
    description: Optional[str] = None

class DocumentChunkResponse(BaseModel):
    id: str
    chunk_index: int
    page_number: int
    section: str
    text: str
    token_count: int
    domain: str

class DocumentResponse(BaseModel):
    id: str
    title: str
    domain: str
    category: str
    author: Optional[str]
    publication_date: Optional[str]
    source_url: Optional[str]
    description: Optional[str]
    file_size_bytes: int
    total_pages: int
    chunk_count: int
    processing_status: str
    is_demo: bool
    created_at: str

# Research Request Schema
class ResearchRequest(BaseModel):
    question: str
    domain: str = "Healthcare"
    research_depth: str = "Standard" # Quick, Standard, Deep
    use_knowledge_base: bool = True
    use_web_search: bool = True
    use_memory: bool = True
    category_filter: Optional[str] = None
    max_reflection_cycles: int = 3

# Agent Execution Payload Schemas
class ClaimEvidenceLink(BaseModel):
    evidence_text: str
    source_title: str
    source_url: Optional[str]
    relationship_type: str # SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED, CONTRADICTED
    section: str
    page_number: int

class ClaimResponse(BaseModel):
    id: str
    claim_text: str
    claim_type: str
    subtopic: str
    importance: str
    verification_status: str
    confidence_score: float
    summary_reasoning: Optional[str]
    evidence_links: List[ClaimEvidenceLink] = []

class SourceResponse(BaseModel):
    id: str
    title: str
    url: Optional[str]
    domain: str
    source_type: str
    author: Optional[str]
    publication_date: Optional[str]
    snippet: Optional[str]
    quality_assessment: str
    quality_explanation: Optional[str]

class ConflictResponse(BaseModel):
    id: str
    topic: str
    explanation: str
    methodological_differences: Optional[str]

class ConfidenceResponse(BaseModel):
    overall_confidence: str
    confidence_score: float
    supporting_sources_count: int
    contradictory_sources_count: int
    unsupported_claims_count: int
    key_reasons: List[str]

class CritiqueResponse(BaseModel):
    unsupported_claims_count: int
    weak_evidence_count: int
    conflicts_count: int
    research_gaps_count: int
    gaps_description: Optional[str]
    recommendations: List[str]

class ResearchSessionResponse(BaseModel):
    id: str
    title: str
    question: str
    domain: str
    research_depth: str
    status: str
    current_step_description: str
    execution_time_seconds: float
    created_at: str
    claims_count: int = 0
    sources_count: int = 0
    conflicts_count: int = 0

class ReportResponse(BaseModel):
    id: str
    session_id: str
    title: str
    executive_summary: str
    methodology: str
    full_content_markdown: str
    created_at: str
    citations: List[Dict[str, Any]] = []

class KnowledgeBaseStatsResponse(BaseModel):
    dataset_name: str = "Healthcare Research Knowledge Base"
    domain: str = "Healthcare"
    documents_count: int
    indexed_count: int
    chunks_count: int
    status: str = "Ready"
    categories: List[Dict[str, Any]]
