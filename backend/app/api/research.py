from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.models import (
    ResearchSession, Claim, Source, Evidence, ClaimEvidence,
    Conflict, ConfidenceAssessment, Critique, Reflection, Report, Citation
)
from app.models.schemas import (
    ResearchRequest, ResearchSessionResponse, ClaimResponse,
    SourceResponse, ConflictResponse, ConfidenceResponse, CritiqueResponse, ReportResponse
)
from app.agents.orchestrator import MultiAgentOrchestrator

router = APIRouter(prefix="/api/research", tags=["Research"])

@router.post("", response_model=ResearchSessionResponse)
def create_research_session(req: ResearchRequest, db: Session = Depends(get_db)):
    orchestrator = MultiAgentOrchestrator(db)
    session = orchestrator.run_full_research_session(
        question=req.question,
        domain=req.domain,
        depth=req.research_depth,
        use_knowledge_base=req.use_knowledge_base,
        use_web_search=req.use_web_search,
        use_memory=req.use_memory,
        category_filter=req.category_filter,
        max_reflection_cycles=req.max_reflection_cycles
    )

    claims_c = db.query(Claim).filter(Claim.session_id == session.id).count()
    sources_c = db.query(Source).filter(Source.session_id == session.id).count()
    conflicts_c = db.query(Conflict).filter(Conflict.session_id == session.id).count()

    return ResearchSessionResponse(
        id=session.id,
        title=session.title,
        question=session.question,
        domain=session.domain,
        research_depth=session.research_depth,
        status=session.status,
        current_step_description=session.current_step_description,
        execution_time_seconds=session.execution_time_seconds or 0.0,
        created_at=session.created_at.strftime("%Y-%m-%d %H:%M"),
        claims_count=claims_c,
        sources_count=sources_c,
        conflicts_count=conflicts_c
    )

@router.get("", response_model=List[ResearchSessionResponse])
def list_research_sessions(db: Session = Depends(get_db)):
    sessions = db.query(ResearchSession).order_by(ResearchSession.created_at.desc()).all()
    res = []
    for s in sessions:
        claims_c = db.query(Claim).filter(Claim.session_id == s.id).count()
        sources_c = db.query(Source).filter(Source.session_id == s.id).count()
        conflicts_c = db.query(Conflict).filter(Conflict.session_id == s.id).count()
        res.append(ResearchSessionResponse(
            id=s.id,
            title=s.title,
            question=s.question,
            domain=s.domain,
            research_depth=s.research_depth,
            status=s.status,
            current_step_description=s.current_step_description,
            execution_time_seconds=s.execution_time_seconds or 0.0,
            created_at=s.created_at.strftime("%Y-%m-%d %H:%M"),
            claims_count=claims_c,
            sources_count=sources_c,
            conflicts_count=conflicts_c
        ))
    return res

@router.get("/{id}", response_model=Dict[str, Any])
def get_research_session(id: str, db: Session = Depends(get_db)):
    session = db.query(ResearchSession).filter(ResearchSession.id == id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Research session not found")

    plans = [
        {"intent": p.intent, "subtopics": p.subtopics, "research_tasks": p.research_tasks}
        for p in session.plans
    ]

    claims = []
    for c in session.claims:
        links = []
        for ce in c.claim_evidence_links:
            links.append({
                "evidence_text": ce.evidence.evidence_text,
                "source_title": ce.evidence.source.title,
                "source_url": ce.evidence.source.url,
                "relationship_type": ce.relationship_type,
                "section": ce.evidence.section,
                "page_number": ce.evidence.page_number
            })
        claims.append({
            "id": c.id,
            "claim_text": c.claim_text,
            "claim_type": c.claim_type,
            "subtopic": c.subtopic,
            "importance": c.importance,
            "verification_status": c.verification_status,
            "confidence_score": c.confidence_score,
            "summary_reasoning": c.summary_reasoning,
            "evidence_links": links
        })

    sources = [
        {
            "id": s.id,
            "title": s.title,
            "url": s.url,
            "domain": s.domain,
            "source_type": s.source_type,
            "author": s.author,
            "publication_date": s.publication_date,
            "snippet": s.snippet,
            "quality_assessment": s.quality_assessment,
            "quality_explanation": s.quality_explanation
        }
        for s in session.sources
    ]

    conflicts = [
        {
            "id": conf.id,
            "topic": conf.topic,
            "explanation": conf.explanation,
            "methodological_differences": conf.methodological_differences
        }
        for conf in session.conflicts
    ]

    confidence = None
    if session.confidence:
        confidence = {
            "overall_confidence": session.confidence.overall_confidence,
            "confidence_score": session.confidence.confidence_score,
            "supporting_sources_count": session.confidence.supporting_sources_count,
            "contradictory_sources_count": session.confidence.contradictory_sources_count,
            "unsupported_claims_count": session.confidence.unsupported_claims_count,
            "key_reasons": session.confidence.key_reasons
        }

    critique = None
    if session.critique:
        critique = {
            "unsupported_claims_count": session.critique.unsupported_claims_count,
            "weak_evidence_count": session.critique.weak_evidence_count,
            "conflicts_count": session.critique.conflicts_count,
            "research_gaps_count": session.critique.research_gaps_count,
            "gaps_description": session.critique.gaps_description,
            "recommendations": session.critique.recommendations
        }

    return {
        "id": session.id,
        "title": session.title,
        "question": session.question,
        "domain": session.domain,
        "research_depth": session.research_depth,
        "status": session.status,
        "current_step_description": session.current_step_description,
        "execution_time_seconds": session.execution_time_seconds,
        "created_at": session.created_at.strftime("%Y-%m-%d %H:%M"),
        "plans": plans,
        "claims": claims,
        "sources": sources,
        "conflicts": conflicts,
        "confidence": confidence,
        "critique": critique,
        "report_id": session.report.id if session.report else None
    }

@router.get("/{id}/report", response_model=ReportResponse)
def get_research_report(id: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.session_id == id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not generated for this session")

    citations = [
        {
            "citation_number": c.citation_number,
            "source_id": c.source_id,
            "citation_text": c.citation_text
        }
        for c in report.citations
    ]

    return ReportResponse(
        id=report.id,
        session_id=report.session_id,
        title=report.title,
        executive_summary=report.executive_summary,
        methodology=report.methodology,
        full_content_markdown=report.full_content_markdown,
        created_at=report.created_at.strftime("%Y-%m-%d %H:%M"),
        citations=citations
    )
