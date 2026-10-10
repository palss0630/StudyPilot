import json
from src.studypilot.agent.planner import Planner, PlanResult
from src.studypilot.agent.llm import LLMClient

class MockLLM(LLMClient):
    def __init__(self, response_text):
        self.response_text = response_text
    def generate_text(self, messages, **kwargs):
        return self.response_text

def test_plan_validation_valid():
    valid_json = '{"steps": [{"step": 1, "description": "Do A", "tools_needed": []}, {"step": 2, "description": "Do B", "tools_needed": []}]}'
    planner = Planner(MockLLM(valid_json))
    plan = planner.create_plan("test goal")
    assert len(plan.steps) == 2
    assert plan.steps[0].description == "Do A"

def test_plan_validation_invalid_json_fallback():
    invalid_json = 'not json'
    planner = Planner(MockLLM(invalid_json))
    plan = planner.create_plan("test goal")
    assert len(plan.steps) == 1
    assert "Research" in plan.steps[0].description

def test_plan_validation_too_many_steps():
    steps = [{"step": i, "description": f"Step {i}", "tools_needed": []} for i in range(10)]
    too_many_json = json.dumps({"steps": steps})
    planner = Planner(MockLLM(too_many_json))
    plan = planner.create_plan("test goal")
    assert len(plan.steps) == 1
    assert "Research" in plan.steps[0].description

def test_plan_validation_missing_fields():
    missing_fields_json = '{"steps": [{"step": 1}]}'
    planner = Planner(MockLLM(missing_fields_json))
    plan = planner.create_plan("test goal")
    assert len(plan.steps) == 1
    assert "Research" in plan.steps[0].description
