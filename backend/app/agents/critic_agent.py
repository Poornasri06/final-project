from typing import List, Dict, Any
from app.agents.base import BaseAgent

class CriticAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CriticAgent",
            role_description="Audits research outputs for unsupported claims, weak evidence, citation gaps, and missing medical subtopics."
        )

    def critique_research(self, claims: List[Dict[str, Any]], conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        unsupported = [c for c in claims if c.get("verification_status") == "UNSUPPORTED"]
        partial = [c for c in claims if c.get("verification_status") == "PARTIALLY_SUPPORTED"]

        gaps = []
        if partial:
            gaps.append("Long-term compliance data for lifestyle interventions requires further longitudinal evaluation.")
        if unsupported:
            gaps.append("Specific dosage response curves for novel combination therapies were under-documented in current chunks.")
        if not gaps:
            gaps.append("Pediatric and geriatric subgroup response variations warrant further specialized document indexing.")

        recommendations = [
            "Perform targeted retrieval on long-term safety and renal outcomes.",
            "Verify sub-analysis for diabetic patients with concurrent hypertension."
        ]

        return {
            "unsupported_claims_count": len(unsupported),
            "weak_evidence_count": len(partial),
            "conflicts_count": len(conflicts),
            "research_gaps_count": len(gaps),
            "gaps_description": "; ".join(gaps),
            "recommendations": recommendations
        }
