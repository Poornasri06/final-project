from typing import Dict, Any
from app.agents.base import BaseAgent
from app.config import settings

class ReflectionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ReflectionAgent",
            role_description="Evaluates critic feedback to determine if additional research retrieval iterations are necessary."
        )

    def reflect(self, critique: Dict[str, Any], current_cycle: int) -> Dict[str, Any]:
        max_cycles = settings.MAX_REFLECTION_CYCLES
        
        # Decide if another cycle is needed
        need_more = False
        new_subtopics = []
        notes = "Current research synthesis has reached satisfactory evidence saturation across primary clinical subtopics."

        if current_cycle < max_cycles and (critique.get("research_gaps_count", 0) > 0 or critique.get("unsupported_claims_count", 0) > 0):
            need_more = True
            new_subtopics = ["Long-term Subgroup Safety", "Combination Pharmacotherapy Outcomes"]
            notes = f"Reflection Cycle #{current_cycle + 1}: Initiating targeted secondary retrieval for identified research gaps: {critique.get('gaps_description')}."

        return {
            "cycle_index": current_cycle,
            "need_additional_research": need_more,
            "reflection_notes": notes,
            "new_subtopics_to_search": new_subtopics
        }
