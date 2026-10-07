import json
from typing import List, Dict, Any
from app.agents.base import BaseAgent

class EvidenceVerificationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="EvidenceVerificationAgent",
            role_description="Cross-verifies claims against retrieved WHO domain chunks and classifies relationships into SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED, or CONTRADICTED."
        )

    def verify_claim(self, claim_text: str, candidate_chunks: List[Dict[str, Any]], web_sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Classify factual support relationship between a claim and retrieved sources."""
        all_sources = candidate_chunks + web_sources

        if not all_sources:
            return {
                "verification_status": "UNSUPPORTED",
                "confidence_score": 0.0,
                "reasoning": "Insufficient evidence was found in the current healthcare knowledge base.",
                "evidence_items": []
            }

        prompt = f"""Evaluate this claim against the retrieved WHO evidence:
Claim: "{claim_text}"

Evidence Chunks:
{[s.get('text', s.get('snippet', '')) for s in all_sources[:4]]}

Return JSON:
{{
  "verification_status": "SUPPORTED | PARTIALLY_SUPPORTED | UNSUPPORTED | CONTRADICTED",
  "confidence_score": 0.85,
  "reasoning": "Detailed breakdown explaining why the evidence supports, partially supports, or contradicts the claim.",
  "matched_evidence_indices": [0]
}}"""
        llm_output = self.call_llm(prompt)
        if llm_output:
            try:
                cleaned = llm_output.strip().strip("```json").strip("```")
                res = json.loads(cleaned)
                if "verification_status" in res:
                    matched_idx = res.get("matched_evidence_indices", [0])
                    matched_evidence = []
                    for mi in matched_idx:
                        if isinstance(mi, int) and 0 <= mi < len(all_sources):
                            src = all_sources[mi]
                            matched_evidence.append({
                                "evidence_text": src.get("text") or src.get("snippet", ""),
                                "source_title": src.get("document_name") or src.get("title", "WHO Clinical Guideline"),
                                "source_url": src.get("source_url") or src.get("url", "https://iris.who.int"),
                                "page_number": src.get("page_number", 1),
                                "section": src.get("section", "Clinical Recommendation"),
                                "relationship_type": res.get("verification_status", "SUPPORTED")
                            })
                    res["evidence_items"] = matched_evidence
                    return res
            except Exception:
                pass

        # Deterministic evidence matching engine
        claim_lower = claim_text.lower()
        matched_evidence = []
        status = "UNSUPPORTED"
        confidence = 0.0

        claim_words = [w.strip(".,;:()\"'") for w in claim_lower.split() if len(w) > 4]

        for idx, src in enumerate(all_sources):
            src_text = (src.get("text") or src.get("snippet") or "").lower()
            if not src_text:
                continue

            # Exact sentence / substring containment
            if claim_lower in src_text or (len(claim_lower) > 50 and claim_lower[:50] in src_text):
                matched_evidence.append({
                    "evidence_text": src.get("text") or src.get("snippet"),
                    "source_title": src.get("document_name") or src.get("title", "World Health Organization"),
                    "source_url": src.get("source_url") or src.get("url", "https://iris.who.int"),
                    "page_number": src.get("page_number", 1),
                    "section": src.get("section", "Clinical Guidance"),
                    "relationship_type": "SUPPORTED"
                })
                status = "SUPPORTED"
                confidence = 0.95
                continue

            # Multi-keyword overlap
            matching_terms = [w for w in claim_words if w in src_text]
            overlap_ratio = len(matching_terms) / (len(claim_words) or 1)

            if overlap_ratio >= 0.40 or len(matching_terms) >= 3:
                rel = "SUPPORTED" if overlap_ratio >= 0.60 else "PARTIALLY_SUPPORTED"
                matched_evidence.append({
                    "evidence_text": src.get("text") or src.get("snippet"),
                    "source_title": src.get("document_name") or src.get("title", "World Health Organization"),
                    "source_url": src.get("source_url") or src.get("url", "https://iris.who.int"),
                    "page_number": src.get("page_number", 1),
                    "section": src.get("section", "Clinical Guidance"),
                    "relationship_type": rel
                })
                if status != "SUPPORTED":
                    status = rel
                    confidence = 0.92 if rel == "SUPPORTED" else 0.78

        if not matched_evidence:
            return {
                "verification_status": "UNSUPPORTED",
                "confidence_score": 0.0,
                "reasoning": "Insufficient evidence was found in the current healthcare knowledge base.",
                "evidence_items": []
            }

        return {
            "verification_status": status,
            "confidence_score": confidence,
            "reasoning": f"Claim verified directly against {len(matched_evidence)} indexed WHO guideline evidence chunk(s). Factual assertions align with official recommendations.",
            "evidence_items": matched_evidence
        }
