"""Tool registry for StudyPilot."""
import functools
import traceback
from typing import Any, Callable, Dict, List

from src.studypilot.config import logger
from src.studypilot.tools.search import web_search
from src.studypilot.tools.wiki import wikipedia_summary
from src.studypilot.tools.webpage import read_webpage
from src.studypilot.tools.calculator import calculator
from src.studypilot.tools.weather import weather
from src.studypilot.tools.notes import save_note_tool, search_notes_tool, list_notes_tool
from src.studypilot.tools.study import make_flashcards, make_quiz
from src.studypilot.tools.clock import current_datetime

# Attempt to import MemoryStore
try:
    from src.studypilot.memory.store import MemoryStore
except ImportError:
    # Fallback mock if not yet implemented
    class MemoryStore:
        def save(self, *args, **kwargs): pass
        def search(self, *args, **kwargs): return []
        def list_all(self, *args, **kwargs): return []

class ToolRegistry:
    """Registry for AI agent tools."""
    
    def __init__(self) -> None:
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, description: str, parameters_schema: dict, func: Callable) -> None:
        """Register a tool."""
        self.tools[name] = {
            "function": func,
            "schema": {
                "name": name,
                "description": description,
                "parameters": parameters_schema
            }
        }

    def get_schemas(self) -> List[Dict[str, Any]]:
        """Get OpenAI compatible tool schemas."""
        return [{"type": "function", "function": t["schema"]} for t in self.tools.values()]

    def call(self, name: str, arguments_dict: dict) -> dict:
        """Call a tool safely."""
        if name not in self.tools:
            return {"error": f"Tool '{name}' not found."}
        
        try:
            func = self.tools[name]["function"]
            result = func(**arguments_dict)
            return {"result": result}
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}\n{traceback.format_exc()}")
            return {"error": str(e)}

_memory_store = MemoryStore()

def get_default_registry() -> ToolRegistry:
    """Create and return a default registry populated with all tools."""
    registry = ToolRegistry()
    
    registry.register(
        "web_search",
        "Search the web using DuckDuckGo.",
        {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"},
                "max_results": {"type": "integer", "description": "Maximum number of results to return"}
            },
            "required": ["query"]
        },
        web_search
    )
    
    registry.register(
        "wikipedia_summary",
        "Get a summary of a topic from Wikipedia.",
        {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "The topic to look up"}
            },
            "required": ["topic"]
        },
        wikipedia_summary
    )
    
    registry.register(
        "read_webpage",
        "Read text content from a webpage URL safely.",
        {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to read"}
            },
            "required": ["url"]
        },
        read_webpage
    )
    
    registry.register(
        "calculator",
        "Evaluate mathematical expressions safely.",
        {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "The mathematical expression"}
            },
            "required": ["expression"]
        },
        calculator
    )
    
    registry.register(
        "weather",
        "Get the current weather and forecast for a city.",
        {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "The city name"}
            },
            "required": ["city"]
        },
        weather
    )
    
    registry.register(
        "save_note",
        "Save a note to memory.",
        {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Title of the note"},
                "content": {"type": "string", "description": "Content of the note"}
            },
            "required": ["title", "content"]
        },
        functools.partial(save_note_tool, memory_store=_memory_store)
    )
    
    registry.register(
        "search_notes",
        "Search saved notes.",
        {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        },
        functools.partial(search_notes_tool, memory_store=_memory_store)
    )
    
    registry.register(
        "list_notes",
        "List all saved notes.",
        {
            "type": "object",
            "properties": {},
            "required": []
        },
        functools.partial(list_notes_tool, memory_store=_memory_store)
    )
    
    def _flashcards_caller(topic: str, notes_text: str):
        from src.studypilot.agent.llm import LLMClient
        return make_flashcards(topic, notes_text, llm_client=LLMClient())

    def _quiz_caller(topic: str, notes_text: str, n: int = 5):
        from src.studypilot.agent.llm import LLMClient
        return make_quiz(topic, notes_text, n=n, llm_client=LLMClient())

    registry.register(
        "make_flashcards",
        "Generate study flashcards from a topic and notes text.",
        {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "The main topic"},
                "notes_text": {"type": "string", "description": "Text to generate flashcards from"}
            },
            "required": ["topic", "notes_text"]
        },
        _flashcards_caller
    )
    
    registry.register(
        "make_quiz",
        "Generate a multiple-choice quiz from text.",
        {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "The main topic"},
                "notes_text": {"type": "string", "description": "Text to generate the quiz from"},
                "n": {"type": "integer", "description": "Number of questions"}
            },
            "required": ["topic", "notes_text"]
        },
        _quiz_caller
    )
    
    registry.register(
        "current_datetime",
        "Get the current date and time.",
        {
            "type": "object",
            "properties": {},
            "required": []
        },
        current_datetime
    )
    
    return registry
