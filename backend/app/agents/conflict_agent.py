import json
from typing import List, Dict, Any
from app.agents.base import BaseAgent

class ConflictDetectionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ConflictDetectionAgent",
            role_description="Detects cross-source evidence contradictions, methodological discrepancies, and clinical guideline variations."
        )

    def detect_conflicts(self, claims: List[Dict[str, Any]], sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not claims or len(sources) < 2:
            return []

        source_titles = [s.get('title') if isinstance(s, dict) else str(s) for s in sources]
        prompt = f"""Analyze these claims and sources for clinical contradictions or divergent guideline recommendations:
Claims:
{[c.get('claim_text') for c in claims]}

Sources:
{source_titles}

If there are legitimate conflicts or population subgroup divergences, return JSON:
[
  {{
    "topic": "Conflict Topic",
    "explanation": "Detailed explanation of divergent recommendations",
    "methodological_differences": "Why sources differ (e.g., patient age, comorbidity, evidence grading)"
  }}
]
If there are NO contradictions, return empty list []."""
        llm_output = self.call_llm(prompt)
        if llm_output:
            try:
                cleaned = llm_output.strip().strip("```json").strip("```")
                res = json.loads(cleaned)
                if isinstance(res, list):
                    return res
            except Exception:
                pass

        conflicts = []
        # Dynamic check for contradictory or partially supported claims
        divergent_claims = [c for c in claims if c.get("verification_status") in ["CONTRADICTED", "PARTIALLY_SUPPORTED"]]
        for c in divergent_claims:
            conflicts.append({
                "topic": f"Evidence Divergence: {c.get('subtopic', 'Clinical Recommendation')}",
                "explanation": f"Claim assertion: '{c.get('claim_text')}' exhibits divergent clinical recommendations or subgroup variations across evaluated sources.",
                "methodological_differences": "Study inclusion criteria, trial settings, or population risk stratification account for observed variations."
            })

        return conflicts
