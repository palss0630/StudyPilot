"""Reflector for the agent loop."""
import json
from typing import List, Dict, Any
from pydantic import BaseModel
from src.studypilot.agent.llm import LLMClient
from src.studypilot.agent.prompts import REFLECTOR_PROMPT
from src.studypilot.config import logger

class ReflectionResult(BaseModel):
    ok: bool
    issues: List[str]
    revised_answer: str

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
        
        try:
            data = json.loads(response)
            return ReflectionResult(**data)
        except Exception as e:
            logger.warning(f"Failed to parse reflection JSON: {e}")
            return ReflectionResult(ok=True, issues=[], revised_answer=draft_answer)
