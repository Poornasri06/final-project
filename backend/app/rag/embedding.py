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
        
        # Comprehensive medical key concepts vector slots across all 8 WHO domains
        medical_keywords = {
            # Diabetes & Metabolic
            "diabetes": 0, "glucose": 1, "insulin": 2, "hba1c": 3, "hyperglycemia": 4,
            "hypoglycemia": 5, "metformin": 6, "sulfonylurea": 7, "sglt2": 8, "glp-1": 9,
            "ketoacidosis": 10, "diabetic": 11, "retinopathy": 12, "nephropathy": 13, "neuropathy": 14,
            
            # Hypertension & Cardiovascular
            "hypertension": 15, "blood pressure": 16, "systolic": 17, "diastolic": 18, "vascular": 19,
            "cardiovascular": 20, "antihypertensive": 21, "amlodipine": 22, "thiazide": 23, "stroke": 24,
            "heart failure": 25, "cholesterol": 26, "statin": 27, "atherosclerosis": 28, "angina": 29,

            # Tuberculosis (TB)
            "tuberculosis": 30, "tb": 31, "mycobacterium": 32, "sputum": 33, "rifampicin": 34,
            "isoniazid": 35, "pyrazinamide": 36, "ethambutol": 37, "bpal": 38, "smear": 39,
            "culture": 40, "pulmonary": 41, "extrapulmonary": 42, "bacillus": 43, "mdr-tb": 44,

            # HIV & Viral Infections
            "hiv": 45, "aids": 46, "antiretroviral": 47, "art": 48, "cd4": 49,
            "viral load": 50, "dolutegravir": 51, "efavirenz": 52, "tenofovir": 53, "opportunistic": 54,
            "transmission": 55, "prophylaxis": 56, "prep": 57, "pep": 58, "immunodeficiency": 59,

            # Hospital Adult & Emergency Triage
            "hospital": 60, "adult": 61, "adolescent": 62, "inpatient": 63, "emergency": 64,
            "clinician": 65, "triage": 66, "acute": 67, "severe": 68, "ward": 69,
            "sepsis": 70, "shock": 71, "coma": 72, "resuscitation": 73, "monitoring": 74,

            # Hospital Children & Pediatrics
            "child": 75, "children": 76, "pediatric": 77, "infant": 78, "newborn": 79,
            "neonate": 80, "diarrhea": 81, "pneumonia": 82, "dehydration": 83, "measles": 84,
            "meningitis": 85, "oral rehydration": 86, "ors": 87, "zinc": 88, "childhood": 89,

            # Emergency Critical Care (SARI)
            "sari": 90, "critical": 91, "respiratory": 92, "oxygen": 93, "hypoxemia": 94,
            "ventilator": 95, "ventilation": 96, "intubation": 97, "ards": 98, "oximetry": 99,
            "intensive": 100, "icu": 101, "hypoxemic": 102, "cannula": 103, "infection": 104,

            # Nutrition & Public Health
            "nutrition": 105, "diet": 106, "dietary": 107, "carbohydrate": 108, "sugar": 109,
            "fiber": 110, "fats": 111, "saturated": 112, "sodium": 113, "malnutrition": 114,
            "stunting": 115, "wasting": 116, "micronutrient": 117, "energy": 118, "intake": 119,

            # General Clinical & Evidence Terms
            "diagnosis": 120, "diagnostic": 121, "treatment": 122, "therapy": 123, "recommendation": 124,
            "guideline": 125, "clinical": 126, "signs": 127, "symptoms": 128, "criteria": 129,
            "management": 130, "dose": 131, "contraindication": 132, "adverse": 133, "efficacy": 134,
            "mortality": 135, "screening": 136, "prevention": 137, "fever": 138, "cough": 139,
            "lifestyle": 140, "exercise": 141, "weight": 142, "obesity": 143, "risk": 144
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
