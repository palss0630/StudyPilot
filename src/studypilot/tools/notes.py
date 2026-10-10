"""Notes memory tools."""
import traceback
from typing import Any

from src.studypilot.config import logger

def save_note_tool(title: str, content: str, memory_store: Any) -> str:
    """Save a note to memory."""
    try:
        if hasattr(memory_store, 'save_note'):
            note_id = memory_store.save_note(title=title, content=content)
        else:
            note_id = memory_store.save(title=title, content=content)
        return f"Note saved successfully with ID: {note_id}"
    except Exception as e:
        logger.error(f"Error saving note: {e}\n{traceback.format_exc()}")
        return f"Error saving note: {e}"

def search_notes_tool(query: str, memory_store: Any) -> str:
    """Search saved notes."""
    try:
        if hasattr(memory_store, 'search_notes'):
            results = memory_store.search_notes(query=query)
        else:
            results = memory_store.search(query=query)
        if not results:
            return f"No notes found for query: '{query}'"
            
        formatted = []
        for i, note in enumerate(results, 1):
            title = note.get('title', 'Untitled')
            content = note.get('content', '')
            nid = note.get('id', 'N/A')
            formatted.append(f"Result {i} (ID: {nid}):\nTitle: {title}\nContent:\n{content}\n")
            
        return "\n".join(formatted)
    except Exception as e:
        logger.error(f"Error searching notes: {e}\n{traceback.format_exc()}")
        return f"Error searching notes: {e}"

def list_notes_tool(memory_store: Any) -> str:
    """List all saved notes."""
    try:
        if hasattr(memory_store, 'list_notes'):
            results = memory_store.list_notes()
        elif hasattr(memory_store, 'list_all'):
            results = memory_store.list_all()
        else:
            results = memory_store.search("")
            
        if not results:
            return "No saved notes found."
            
        formatted = []
        for note in results:
            title = note.get('title', 'Untitled')
            nid = note.get('id', 'N/A')
            formatted.append(f"- {title} (ID: {nid})")
            
        return "\n".join(formatted)
    except Exception as e:
        logger.error(f"Error listing notes: {e}\n{traceback.format_exc()}")
        return f"Error listing notes: {e}"
