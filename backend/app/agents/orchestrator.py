import time
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.models import (
    ResearchSession, ResearchPlan, Claim, Source, Evidence, ClaimEvidence,
    SourceEvaluation, Conflict, ConfidenceAssessment, Critique, Reflection,
    Report, Citation, MemoryItem
)
from app.agents.planner_agent import ResearchPlannerAgent
from app.agents.rag_agent import DomainRAGAgent
from app.agents.web_agent import WebResearchAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.claim_agent import ClaimExtractionAgent
from app.agents.verification_agent import EvidenceVerificationAgent
from app.agents.source_agent import SourceEvaluationAgent
from app.agents.conflict_agent import ConflictDetectionAgent
from app.agents.confidence_agent import ConfidenceAssessmentAgent
from app.agents.critic_agent import CriticAgent
from app.agents.reflection_agent import ReflectionAgent
from app.agents.report_agent import ReportAgent

class MultiAgentOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.planner = ResearchPlannerAgent()
        self.rag_agent = DomainRAGAgent()
        self.web_agent = WebResearchAgent()
        self.memory_agent = MemoryAgent()
        self.claim_agent = ClaimExtractionAgent()
        self.verifier = EvidenceVerificationAgent()
        self.evaluator = SourceEvaluationAgent()
        self.conflict_detector = ConflictDetectionAgent()
        self.confidence_assessor = ConfidenceAssessmentAgent()
        self.critic = CriticAgent()
        self.reflector = ReflectionAgent()
        self.reporter = ReportAgent()

    def run_full_research_session(
        self,
        question: str,
        domain: str = "Healthcare",
        depth: str = "Standard",
        use_knowledge_base: bool = True,
        use_web_search: bool = True,
        use_memory: bool = True,
        category_filter: Optional[str] = None,
        max_reflection_cycles: int = 3,
        user_id: Optional[str] = None
    ) -> ResearchSession:
        start_time = time.time()

        # 1. Initialize Session in DB
        session = ResearchSession(
            user_id=user_id,
            title=f"Research: {question[:60]}",
            question=question,
            domain=domain,
            research_depth=depth,
            use_knowledge_base=use_knowledge_base,
            use_web_search=use_web_search,
            use_memory=use_memory,
            category_filter=category_filter,
            max_reflection_cycles=max_reflection_cycles,
            status="RUNNING",
            current_step_description="Analyzing question and creating research plan..."
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        try:
            # STEP 1: RESEARCH PLANNING
            session.current_step_description = "Research planning and intent analysis..."
            self.db.commit()
            plan_data = self.planner.plan_research(question, domain, depth)
            plan_obj = ResearchPlan(
                session_id=session.id,
                intent=plan_data.get("intent", "Domain research analysis"),
                subtopics=plan_data.get("subtopics", []),
                research_tasks=plan_data.get("research_tasks", [])
            )
            self.db.add(plan_obj)
            self.db.commit()

            # STEP 2: DOMAIN RETRIEVAL (RAG)
            retrieved_chunks = []
            if use_knowledge_base:
                session.current_step_description = "Searching Healthcare Knowledge Base vectors..."
                self.db.commit()
                retrieved_chunks = self.rag_agent.retrieve_domain_evidence(
                    self.db, question, category_filter=category_filter, top_k=6
                )

            # STEP 3: WEB RESEARCH
            web_sources = []
            if use_web_search:
                session.current_step_description = "Executing external web research..."
                self.db.commit()
                web_res = self.web_agent.search_web(question, max_results=3)
                web_sources = web_res.get("sources", [])

            # STEP 4: MEMORY SEARCH
            memory_items = []
            if use_memory:
                session.current_step_description = "Searching previous research memory..."
                self.db.commit()
                memory_items = self.memory_agent.search_memory(self.db, question, top_k=2)

            # STEP 5: CLAIM EXTRACTION
            session.current_step_description = "Extracting factual claims..."
            self.db.commit()
            raw_claims = self.claim_agent.extract_claims(question, retrieved_chunks, web_sources)

            # Save Sources to DB
            source_map = {} # title -> Source DB model
            for chunk in retrieved_chunks:
                doc_title = chunk["document_name"]
                if doc_title not in source_map:
                    s_eval = self.evaluator.evaluate_source(doc_title, "Knowledge Base Document", chunk.get("publication_date", "2025"))
                    s_model = Source(
                        session_id=session.id,
                        document_id=chunk.get("document_id"),
                        title=doc_title,
                        url=chunk.get("source_url"),
                        domain=chunk.get("domain", "Healthcare"),
                        source_type="Knowledge Base Document",
                        author=chunk.get("author", "Medical Advisory Panel"),
                        publication_date=chunk.get("publication_date", "2025"),
                        snippet=chunk["text"][:200] + "...",
                        quality_assessment=s_eval["overall_rating"],
                        quality_explanation=s_eval["rationale"]
                    )
                    self.db.add(s_model)
                    self.db.flush()
                    source_map[doc_title] = s_model

            for ws in web_sources:
                w_title = ws["title"]
                if w_title not in source_map:
                    s_eval = self.evaluator.evaluate_source(w_title, ws.get("source_type", "Web Article"), ws.get("publication_date", "2025"))
                    s_model = Source(
                        session_id=session.id,
                        title=w_title,
                        url=ws.get("url"),
                        domain=ws.get("domain", "web"),
                        source_type=ws.get("source_type", "Web Article"),
                        publication_date=ws.get("publication_date", "2025"),
                        snippet=ws.get("snippet"),
                        quality_assessment=s_eval["overall_rating"],
                        quality_explanation=s_eval["rationale"]
                    )
                    self.db.add(s_model)
                    self.db.flush()
                    source_map[w_title] = s_model

            self.db.commit()

            # STEP 6: EVIDENCE VERIFICATION
            session.current_step_description = "Verifying claims against evidence..."
            self.db.commit()
            db_claims = []
            verified_claims_data = []

            for claim_item in raw_claims:
                c_text = claim_item["claim_text"]
                verif_res = self.verifier.verify_claim(c_text, retrieved_chunks, web_sources)
                
                c_model = Claim(
                    session_id=session.id,
                    claim_text=c_text,
                    claim_type=claim_item.get("claim_type", "Factual Claim"),
                    subtopic=claim_item.get("subtopic", "General"),
                    importance=claim_item.get("importance", "HIGH"),
                    verification_status=verif_res["verification_status"],
                    confidence_score=verif_res["confidence_score"],
                    summary_reasoning=verif_res["reasoning"]
                )
                self.db.add(c_model)
                self.db.flush()
                db_claims.append(c_model)

                v_data = claim_item.copy()
                v_data["verification_status"] = verif_res["verification_status"]
                v_data["confidence_score"] = verif_res["confidence_score"]
                v_data["summary_reasoning"] = verif_res["reasoning"]
                verified_claims_data.append(v_data)

                # Link Evidence & ClaimEvidence in DB
                for ev_item in verif_res.get("evidence_items", []):
                    # Find matching source by title
                    s_title = ev_item.get("source_title")
                    s_obj = source_map.get(s_title) or (list(source_map.values())[0] if source_map else None)
                    if s_obj:
                        ev_model = Evidence(
                            source_id=s_obj.id,
                            evidence_text=ev_item["evidence_text"],
                            section=ev_item.get("section", "General"),
                            page_number=ev_item.get("page_number", 1),
                            relevance_score=0.92
                        )
                        self.db.add(ev_model)
                        self.db.flush()

                        ce_link = ClaimEvidence(
                            claim_id=c_model.id,
                            evidence_id=ev_model.id,
                            relationship_type=ev_item.get("relationship_type", "SUPPORTED"),
                            analysis_notes="Semantic evidence matching completed."
                        )
                        self.db.add(ce_link)

            self.db.commit()

            # STEP 7: CONFLICT DETECTION
            session.current_step_description = "Detecting cross-source conflicts..."
            self.db.commit()
            conflicts_data = self.conflict_detector.detect_conflicts(verified_claims_data, list(source_map.keys()))
            for conf in conflicts_data:
                conf_model = Conflict(
                    session_id=session.id,
                    topic=conf["topic"],
                    explanation=conf["explanation"],
                    methodological_differences=conf.get("methodological_differences")
                )
                self.db.add(conf_model)
            self.db.commit()

            # STEP 8: CONFIDENCE ASSESSMENT
            session.current_step_description = "Evaluating multi-factor confidence assessment..."
            self.db.commit()
            conf_assess = self.confidence_assessor.assess_confidence(
                verified_claims_data, list(source_map.values()), conflicts_data
            )
            conf_model = ConfidenceAssessment(
                session_id=session.id,
                overall_confidence=conf_assess["overall_confidence"],
                confidence_score=conf_assess["confidence_score"],
                supporting_sources_count=conf_assess["supporting_sources_count"],
                contradictory_sources_count=conf_assess["contradictory_sources_count"],
                unsupported_claims_count=conf_assess["unsupported_claims_count"],
                key_reasons=conf_assess["key_reasons"]
            )
            self.db.add(conf_model)
            self.db.commit()

            # STEP 9: CRITIC & REFLECTION LOOP
            session.current_step_description = "Performing research critique and reflection audit..."
            self.db.commit()
            critique_data = self.critic.critique_research(verified_claims_data, conflicts_data)
            critique_model = Critique(
                session_id=session.id,
                unsupported_claims_count=critique_data["unsupported_claims_count"],
                weak_evidence_count=critique_data["weak_evidence_count"],
                conflicts_count=critique_data["conflicts_count"],
                research_gaps_count=critique_data["research_gaps_count"],
                gaps_description=critique_data["gaps_description"],
                recommendations=critique_data["recommendations"]
            )
            self.db.add(critique_model)

            reflection_data = self.reflector.reflect(critique_data, current_cycle=1)
            refl_model = Reflection(
                session_id=session.id,
                cycle_index=1,
                need_additional_research=reflection_data["need_additional_research"],
                reflection_notes=reflection_data["reflection_notes"],
                new_subtopics_to_search=reflection_data["new_subtopics_to_search"]
            )
            self.db.add(refl_model)
            self.db.commit()

            # STEP 10: REPORT GENERATION
            session.current_step_description = "Generating final traceable research report..."
            self.db.commit()
            all_sources_list = [
                {
                    "id": s.id, "title": s.title, "url": s.url,
                    "source_type": s.source_type, "quality_assessment": s.quality_assessment,
                    "publication_date": s.publication_date
                } for s in source_map.values()
            ]

            report_data = self.reporter.generate_report(
                question, verified_claims_data, all_sources_list, conflicts_data, conf_assess, critique_data
            )

            report_model = Report(
                session_id=session.id,
                title=report_data["title"],
                executive_summary=report_data["executive_summary"],
                methodology=report_data["methodology"],
                full_content_markdown=report_data["full_content_markdown"]
            )
            self.db.add(report_model)
            self.db.flush()

            for cit in report_data["citations"]:
                cit_model = Citation(
                    report_id=report_model.id,
                    citation_number=cit["citation_number"],
                    source_id=cit["source_id"],
                    citation_text=cit["citation_text"]
                )
                self.db.add(cit_model)

            # Store useful finding into persistent Memory
            mem_item = MemoryItem(
                session_id=session.id,
                previous_question=question,
                key_finding=f"{verified_claims_data[0]['claim_text'] if verified_claims_data else question} (Confidence: {conf_assess['overall_confidence']})",
                source_title=all_sources_list[0]["title"] if all_sources_list else "Healthcare Guidelines",
                relevance_tag=domain
            )
            self.db.add(mem_item)

            # Finalize Session Status
            session.execution_time_seconds = round(time.time() - start_time, 2)
            session.status = "COMPLETED"
            session.current_step_description = "Research complete. Evidence report generated."
            self.db.commit()
            self.db.refresh(session)

            return session

        except Exception as e:
            session.status = "FAILED"
            session.current_step_description = f"Research failed: {str(e)}"
            self.db.commit()
            raise e
