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
    {{"task": "Search vector database for...", "target_source": "Knowledge Base"}},
    {{"task": "Query web research APIs for...", "target_source": "Web Research"}}
  ]
}}"""
        llm_output = self.call_llm(prompt)
        if llm_output:
            try:
                cleaned = llm_output.strip().strip("```json").strip("```")
                return json.loads(cleaned)
            except Exception:
                pass

        # Domain heuristic fallback
        q_lower = question.lower()
        subtopics = []
        if "diabetes" in q_lower or "t2d" in q_lower or "glucose" in q_lower:
            subtopics = ["Glycemic Control & HbA1c", "Metabolic & Lifestyle Factors", "Microvascular & Cardiovascular Complications"]
        elif "hypertension" in q_lower or "blood pressure" in q_lower:
            subtopics = ["Sodium & Lifestyle Modifications", "End-Organ Damage & Screening", "Pharmacotherapy Guidelines"]
        elif "cardiovascular" in q_lower or "heart" in q_lower or "lipid" in q_lower:
            subtopics = ["Lipid Management & Statins", "Atherosclerotic Risk Factors", "Primary Prevention Guidelines"]
        else:
            subtopics = ["Epidemiology & Prevalence", "Clinical Interventions", "Patient Outcomes & Guidelines"]

        return {
            "intent": f"Systematic evidence analysis regarding '{question}' in {domain} domain.",
            "subtopics": subtopics,
            "research_tasks": [
                {"task": f"Retrieve clinical guideline chunks for {subtopics[0]}", "target_source": "Healthcare Knowledge Base"},
                {"task": f"Retrieve research study chunks for {subtopics[1]}", "target_source": "Healthcare Knowledge Base"},
                {"task": f"Search recent public health publications for {subtopics[2]}", "target_source": "Web Research"}
            ]
        }
