"""Executor for the agent loop."""
from typing import List, Dict, Any
from pydantic import BaseModel
from src.studypilot.agent.llm import LLMClient
from src.studypilot.agent.prompts import EXECUTOR_PROMPT
from src.studypilot.config import logger

MAX_TOOL_CALLS_PER_STEP = 5
MAX_TOOL_CALLS_PER_RUN = 20

class StepResult(BaseModel):
    content: str
    tool_calls_made: List[Dict[str, Any]]
    completed: bool

class Executor:
    def __init__(self, llm_client: LLMClient, tool_registry: Any) -> None:
        self.llm_client = llm_client
        self.tool_registry = tool_registry
        self.total_tool_calls = 0
        
    def reset_counters(self) -> None:
        self.total_tool_calls = 0
        
    def execute_step(self, step_description: str, context: str, messages_so_far: List[Dict[str, Any]]) -> StepResult:
        messages = [
            {"role": "system", "content": EXECUTOR_PROMPT},
            {"role": "user", "content": f"Context: {context}\nStep: {step_description}"}
        ]
        messages.extend(messages_so_far)
        
        tool_calls_made = []
        iterations = 0
        
        while iterations < MAX_TOOL_CALLS_PER_STEP:
            if self.total_tool_calls >= MAX_TOOL_CALLS_PER_RUN:
                return StepResult(
                    content="Execution stopped: Maximum total tool calls per run exceeded.",
                    tool_calls_made=tool_calls_made,
                    completed=False
                )
                
            response = self.llm_client.generate(
                messages=messages,
                tools=self.tool_registry.get_schemas()
            )
            
            messages.append(response)
            
            if "tool_calls" in response and response["tool_calls"]:
                for tc in response["tool_calls"]:
                    self.total_tool_calls += 1
                    name = tc["function"]["name"]
                    args = tc["function"]["arguments"]
                    
                    try:
                        import json
                        parsed_args = json.loads(args)
                        result = self.tool_registry.call(name, parsed_args)
                    except Exception as e:
                        result = f"Error calling tool {name}: {e}"
                        
                    tool_calls_made.append({"name": name, "args": args, "result": result})
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": str(result)
                    })
                iterations += 1
            else:
                return StepResult(
                    content=response.get("content", ""),
                    tool_calls_made=tool_calls_made,
                    completed=True
                )
                
        return StepResult(
            content="Execution stopped: Maximum tool calls per step exceeded.",
            tool_calls_made=tool_calls_made,
            completed=False
        )
