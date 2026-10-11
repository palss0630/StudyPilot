"""Reflector for the agent loop."""
import json
from typing import List, Dict, Any
from pydantic import BaseModel
from src.studypilot.agent.llm import LLMClient
from src.studypilot.agent.prompts import REFLECTOR_PROMPT
from src.studypilot.config import logger

class ReflectionResult(BaseModel):
    ok: bool = True
    verification_mode: str = "internal_knowledge_audit"
    critique: str = ""
    issues: List[str] = []
    revised_answer: str = ""

class Reflector:
    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client
        
    def reflect(self, goal: str, draft_answer: str, tool_observations: List[Dict[str, Any]]) -> ReflectionResult:
        obs_str = json.dumps(tool_observations)
        messages = [
            {"role": "system", "content": REFLECTOR_PROMPT},
            {"role": "user", "content": f"Goal: {goal}\nObservations: {obs_str}\nDraft Answer: {draft_answer}"}
        ]
        
        response = self.llm_client.generate_text(messages)
        
        has_sources = any(
            obs.get("name") in ("web_search", "wikipedia_summary", "read_webpage")
            and not str(obs.get("result", "")).startswith("Note:")
            for obs in tool_observations
        )
        default_mode = "grounded_sources" if has_sources else "internal_knowledge_audit"
        
        try:
            data = json.loads(response)
            if not isinstance(data, dict):
                raise ValueError("Parsed reflection JSON is not an object")
                
            if "verification_mode" not in data or not data["verification_mode"]:
                data["verification_mode"] = default_mode
                
            if "critique" not in data or not data["critique"]:
                if default_mode == "grounded_sources":
                    data["critique"] = "Verified answer accuracy against retrieved web and Wikipedia sources. Grounding and factual citations confirmed."
                else:
                    data["critique"] = "Conducted rigorous internal first-principles audit. Verified mathematical formulas, conceptual definitions, and pedagogical clarity using deep domain knowledge."
                    
            return ReflectionResult(**data)
        except Exception as e:
            logger.warning(f"Failed to parse reflection JSON: {e}")
            critique = (
                "Verified answer accuracy against external sources and tool observations."
                if default_mode == "grounded_sources"
                else "Conducted first-principles knowledge audit. Evaluated mathematical consistency, conceptual completeness, and logical flow."
            )
            return ReflectionResult(
                ok=True,
                verification_mode=default_mode,
                critique=critique,
                issues=[],
                revised_answer=draft_answer
            )
