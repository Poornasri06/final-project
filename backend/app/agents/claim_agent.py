import re
import json
from typing import List, Dict, Any
from app.agents.base import BaseAgent

class ClaimExtractionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ClaimExtractionAgent",
            role_description="Extracts testable, atomic healthcare factual claims directly from retrieved WHO clinical literature."
        )

    def extract_claims(self, question: str, retrieved_chunks: List[Dict[str, Any]], web_sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Check query term overlap or similarity threshold
        stopwords = {
            "what", "are", "the", "for", "and", "how", "with", "does", "explain", "who", "which",
            "can", "when", "where", "from", "that", "this", "these", "those", "about", "into",
            "over", "after", "is", "was", "were", "been", "being", "have", "has", "had", "algorithm"
        }
        query_words = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', question.lower()) if w not in stopwords]

        valid_chunks = []
        for c in retrieved_chunks:
            c_text_lower = c.get("text", "").lower()
            overlap_count = sum(1 for w in query_words if w in c_text_lower)
            sim = c.get("similarity_score", 0)
            
            # Must have at least 1 meaningful keyword match from question OR high semantic similarity
            if (overlap_count >= 1 and sim > 0.05) or (sim > 0.45 and len(query_words) == 0):
                valid_chunks.append(c)

        if not valid_chunks and not web_sources:
            return []

        # Combine retrieved context
        context_str = "\n---\n".join([f"[{c.get('document_name', 'WHO Document')}, Page {c.get('page_number', 1)}, Section: {c.get('section', 'General')}]:\n{c['text']}" for c in valid_chunks[:6]])
        
        prompt = f"""Extract 3 to 5 core factual medical/healthcare claims made in this official WHO literature related to the question: "{question}".
All claims must be grounded directly in the provided text.

Literature Context:
{context_str}

Return JSON array format:
[
  {{
    "claim_text": "Exact factual claim directly supported by text",
    "claim_type": "Clinical Guideline / Diagnosis & Screening / Treatment & Management / Risk Factor / Clinical Sign",
    "subtopic": "Relevant subtopic",
    "importance": "HIGH"
  }}
]"""
        llm_output = self.call_llm(prompt)
        if llm_output:
            try:
                cleaned = llm_output.strip().strip("```json").strip("```")
                parsed = json.loads(cleaned)
                if isinstance(parsed, list) and len(parsed) > 0:
                    return parsed
            except Exception:
                pass

        # Dynamic Evidence-Grounded Extraction Engine (Extracts real sentences from retrieved WHO chunks)
        claims = []
        seen_sentences = set()

        medical_action_verbs = [
            "recommend", "suggest", "guideline", "treat", "diagnos", "symptom", "sign",
            "cause", "manag", "risk", "therap", "criteri", "dose", "indicat",
            "prevent", "associat", "result", "defin", "care", "evaluat", "assess",
            "screen", "infect", "threshold", "reduc", "increas", "first-line", "protocol"
        ]

        for chunk in valid_chunks:
            text = chunk.get("text", "")
            doc_name = chunk.get("document_name", "WHO Guideline")
            section = chunk.get("section", "Clinical Practice")
            category = chunk.get("category", "General Healthcare")

            # Split into clean sentences
            sentences = re.split(r'(?<=[.!?])\s+', text)
            for raw_s in sentences:
                s = raw_s.strip()
                # Clean bullet markers, numbers
                s_clean = re.sub(r'^[•\-\*\d\.\)\s]+', '', s).strip()
                s_lower = s_clean.lower()

                # Must be a coherent sentence of appropriate length (50-250 chars)
                if len(s_clean) < 45 or len(s_clean) > 300:
                    continue
                if s_clean in seen_sentences:
                    continue

                # Check if sentence contains clinical value and connects to medical concepts
                has_action = any(verb in s_lower for verb in medical_action_verbs)
                if has_action:
                    seen_sentences.add(s_clean)

                    # Determine claim type
                    claim_type = "Clinical Guideline"
                    if any(k in s_lower for k in ["diagnos", "criteria", "screen", "threshold", "test", "defin"]):
                        claim_type = "Diagnostic Criteria"
                    elif any(k in s_lower for k in ["treat", "dose", "drug", "first-line", "therap", "manag", "regimen"]):
                        claim_type = "Treatment & Management"
                    elif any(k in s_lower for k in ["risk", "complication", "mortality", "factor"]):
                        claim_type = "Risk Factor & Outcomes"
                    elif any(k in s_lower for k in ["symptom", "sign", "fever", "cough", "pain", "present"]):
                        claim_type = "Clinical Sign & Symptom"

                    claims.append({
                        "claim_text": s_clean,
                        "claim_type": claim_type,
                        "subtopic": section if section != "General" else f"{category} Practice",
                        "importance": "HIGH" if len(claims) < 2 else "MEDIUM",
                        "source_document": doc_name,
                        "page_number": chunk.get("page_number", 1)
                    })

                    if len(claims) >= 5:
                        break
            if len(claims) >= 5:
                break

        return claims
