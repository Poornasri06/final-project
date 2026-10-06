import math
import hashlib
import httpx
from typing import List
from app.config import settings

class EmbeddingProvider:
    def __init__(self):
        self.provider = settings.EMBEDDING_PROVIDER.lower()
        self.model = settings.EMBEDDING_MODEL
        self.api_key = settings.EMBEDDING_API_KEY
        self.dimension = settings.EMBEDDING_DIMENSION

    def get_embedding(self, text: str) -> List[float]:
        """Generate a dense vector embedding for input text using configured provider."""
        if not text or not text.strip():
            return [0.0] * self.dimension

        if self.provider == "openai" and self.api_key:
            try:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                payload = {"input": text, "model": self.model}
                res = httpx.post("https://api.openai.com/v1/embeddings", json=payload, headers=headers, timeout=10.0)
                if res.status_code == 200:
                    return res.json()["data"][0]["embedding"]
            except Exception:
                pass

        elif self.provider == "gemini" and self.api_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={self.api_key}"
                payload = {"content": {"parts": [{"text": text}]}}
                res = httpx.post(url, json=payload, timeout=10.0)
                if res.status_code == 200:
                    return res.json()["embedding"]["values"]
            except Exception:
                pass

        # Fallback / Offline Heuristic Feature Vector Generator
        # Deterministic domain-aware hashing vector for demonstration & testing
        return self._generate_heuristic_vector(text)

    def _generate_heuristic_vector(self, text: str) -> List[float]:
        """Create a reproducible 384-dimensional semantic pseudo-embedding vector."""
        vec = [0.0] * self.dimension
        words = text.lower().split()
        
        # Medical key concepts weight vector slots
        medical_keywords = {
            "diabetes": 0, "glucose": 1, "insulin": 2, "hba1c": 3, "hyperglycemia": 4,
            "hypertension": 5, "blood pressure": 6, "systolic": 7, "diastolic": 8, "vascular": 9,
            "cardiovascular": 10, "heart": 11, "cholesterol": 12, "statin": 13, "atherosclerosis": 14,
            "lifestyle": 15, "diet": 16, "exercise": 17, "weight": 18, "obesity": 19,
            "risk": 20, "complication": 21, "retinopathy": 22, "nephropathy": 23, "neuropathy": 24,
            "guideline": 25, "trial": 26, "mortality": 27, "screening": 28, "prevention": 29
        }

        for w in words:
            clean_w = w.strip(".,;:()")
            if clean_w in medical_keywords:
                slot = medical_keywords[clean_w]
                vec[slot] += 2.5
            
            # Hash contribution for all words to populate the vector space
            h = int(hashlib.md5(clean_w.encode('utf-8')).hexdigest(), 16) % self.dimension
            vec[h] += 0.1

        # Normalize L2 norm
        norm = math.sqrt(sum(val * val for val in vec))
        if norm > 0:
            vec = [val / norm for val in vec]
        
        return vec
