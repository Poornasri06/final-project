import json
from typing import Dict, Any, List
from app.agents.base import BaseAgent

class ResearchPlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ResearchPlannerAgent",
            role_description="Deconstructs healthcare research questions into domain subtopics, intent analysis, and structured retrieval tasks."
        )

    def plan_research(self, question: str, domain: str = "Healthcare", depth: str = "Standard") -> Dict[str, Any]:
        prompt = f"""Analyze this healthcare research question and return a structured JSON plan:
Question: "{question}"
Domain: {domain}
Depth: {depth}

Format required:
{{
  "intent": "Brief description of research intent",
  "subtopics": ["Subtopic 1", "Subtopic 2", "Subtopic 3"],
  "research_tasks": [
    {{"task": "Search vector database for...", "target_source": "WHO Knowledge Base"}},
    {{"task": "Query web research APIs for...", "target_source": "Public Health Research"}}
  ]
}}"""
        llm_output = self.call_llm(prompt)
        if llm_output:
            try:
                cleaned = llm_output.strip().strip("```json").strip("```")
                res = json.loads(cleaned)
                if "subtopics" in res and "research_tasks" in res:
                    return res
            except Exception:
                pass

        # Dynamic heuristic planner across all 8 WHO clinical domains
        q_lower = question.lower()
        subtopics = []
        if "tuberculosis" in q_lower or " tb" in q_lower or "tb " in q_lower:
            subtopics = ["Tuberculosis Diagnosis & Sputum Testing", "First-Line Treatment Regimens (6-Month vs 4-Month)", "Drug-Resistant TB & Comorbidities"]
        elif "hiv" in q_lower or "aids" in q_lower or "antiretroviral" in q_lower or "art" in q_lower:
            subtopics = ["HIV Diagnostic Screening & CD4 / Viral Load", "First-Line Antiretroviral Therapy (DTG/TDF/3TC)", "Opportunistic Infections & Key Populations"]
        elif "respiratory" in q_lower or "sari" in q_lower or "oxygen" in q_lower or "ventilator" in q_lower or "critical" in q_lower:
            subtopics = ["Severe Respiratory Infection Triage", "Oxygen Therapy & Hypoxemia Management", "Mechanical Ventilation & ARDS Protocols"]
        elif "child" in q_lower or "pediatric" in q_lower or "infant" in q_lower or "newborn" in q_lower:
            subtopics = ["Emergency Triage Assessment & Treatment (ETAT)", "Common Childhood Illnesses (Pneumonia, Diarrhea, Fever)", "Pediatric Inpatient Supportive Care"]
        elif "hospital" in q_lower or "adult" in q_lower or "triage" in q_lower or "inpatient" in q_lower or "emergency" in q_lower:
            subtopics = ["Emergency Triage & Initial 24-Hour Resuscitation", "Severe Infections, Sepsis & Shock Protocols", "Inpatient Ward Monitoring & Clinical Care"]
        elif "nutrition" in q_lower or "diet" in q_lower or "sugar" in q_lower or "carbohydrate" in q_lower or "fiber" in q_lower:
            subtopics = ["Dietary Carbohydrate & Sugar Intake Thresholds", "Dietary Fiber & Whole Grain Health Outcomes", "Public Health Nutritional Prevention Guidelines"]
        elif "diabetes" in q_lower or "glucose" in q_lower or "insulin" in q_lower or "hba1c" in q_lower:
            subtopics = ["Diagnostic Criteria & Fasting Glucose Thresholds", "First-Line Pharmacotherapy (Metformin & Combinations)", "Microvascular & Cardiovascular Complication Screening"]
        elif "hypertension" in q_lower or "blood pressure" in q_lower or "systolic" in q_lower:
            subtopics = ["Blood Pressure Diagnostic Thresholds (≥140/90 mmHg)", "First-Line Antihypertensive Classes (ACE-i, ARB, CCB, Thiazide)", "Target Blood Pressure Goals & Follow-Up Protocols"]
        else:
            subtopics = [f"Clinical Presentation & Diagnosis of {question[:40]}", f"Evidence-Based Management Protocols", "Outcomes, Complications & WHO Guidelines"]

        return {
            "intent": f"Systematic evidence analysis regarding '{question}' within official WHO clinical guidelines.",
            "subtopics": subtopics,
            "research_tasks": [
                {"task": f"Retrieve clinical guideline chunks for {subtopics[0]}", "target_source": "WHO Clinical Knowledge Base"},
                {"task": f"Retrieve treatment protocols for {subtopics[1]}", "target_source": "WHO Clinical Knowledge Base"},
                {"task": f"Analyze guideline evidence for {subtopics[2]}", "target_source": "WHO Clinical Knowledge Base"}
            ]
        }
