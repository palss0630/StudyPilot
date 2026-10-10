"""Planner for the agent loop."""
import json
from typing import List
from pydantic import BaseModel
from src.studypilot.agent.llm import LLMClient
from src.studypilot.agent.prompts import PLANNER_PROMPT, REPAIR_JSON_PROMPT
from src.studypilot.config import logger

MIN_PLAN_STEPS = 2
MAX_PLAN_STEPS = 6

class PlanStep(BaseModel):
    step: int
    description: str
    tools_needed: List[str]

class PlanResult(BaseModel):
    steps: List[PlanStep]

class Planner:
    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client
        
    def create_plan(self, goal: str, context: str = "") -> PlanResult:
        messages = [
            {"role": "system", "content": PLANNER_PROMPT},
            {"role": "user", "content": f"Context: {context}\nGoal: {goal}"}
        ]
        
        response = self.llm_client.generate_text(messages)
        
        try:
            data = json.loads(response)
            plan = PlanResult(**data)
        except Exception as e:
            logger.warning(f"Failed to parse plan JSON: {e}, attempting repair")
            repair_messages = [
                {"role": "system", "content": REPAIR_JSON_PROMPT},
                {"role": "user", "content": response}
            ]
            repaired = self.llm_client.generate_text(repair_messages)
            try:
                data = json.loads(repaired)
                plan = PlanResult(**data)
            except Exception as e2:
                logger.error(f"Failed to repair plan JSON: {e2}")
                plan = PlanResult(steps=[PlanStep(step=1, description="Research and answer the question", tools_needed=[])])
                
        # Validate step count
        step_count = len(plan.steps)
        if step_count < MIN_PLAN_STEPS or step_count > MAX_PLAN_STEPS:
            logger.warning(f"Plan step count {step_count} out of bounds, using default plan.")
            plan = PlanResult(steps=[PlanStep(step=1, description="Research and answer the question", tools_needed=[])])
            
        return plan
