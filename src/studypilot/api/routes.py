"""
StudyPilot FastAPI backend routes.
Provides REST and Server-Sent Events (SSE) streaming for agent execution,
sessions, notes, and interactive quizzes.
"""

import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from src.studypilot.memory.store import MemoryStore
from src.studypilot.agent.orchestrator import Orchestrator
from src.studypilot.agent.llm import LLMClient
from src.studypilot.tools.study import make_flashcards, make_quiz
from src.studypilot.guardrails import check_output
from src.studypilot.config import LLM_PROVIDER, LLM_MODEL

router = APIRouter(prefix="/api")
memory_store = MemoryStore()


class RunAgentRequest(BaseModel):
    goal: str
    session_id: Optional[str] = None


class NoteCreateRequest(BaseModel):
    title: str
    content: str
    tags: Optional[str] = ""


class QuizResultCreateRequest(BaseModel):
    topic: str
    score: int
    total: int
    session_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class StudyHelperRequest(BaseModel):
    topic: str
    content: str
    n: Optional[int] = 5


@router.get("/status")
def get_status():
    """Return backend operational status."""
    return {
        "status": "online",
        "provider": LLM_PROVIDER,
        "model": LLM_MODEL,
    }


@router.get("/sessions")
def list_sessions(limit: int = 50):
    """Retrieve recent study sessions."""
    return memory_store.list_sessions(limit=limit)


@router.get("/sessions/{session_id}")
def get_session(session_id: str):
    """Retrieve full message history for a specific session."""
    messages = memory_store.get_messages(session_id=session_id, limit=100)
    return {
        "session_id": session_id,
        "messages": messages,
    }


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    """Delete a session."""
    memory_store.delete_session(session_id)
    return {"ok": True}


@router.get("/notes")
def list_notes(query: Optional[str] = Query(None)):
    """List or search notes."""
    if query:
        return memory_store.search_notes(query)
    return memory_store.list_notes()


@router.post("/notes")
def create_note(req: NoteCreateRequest):
    """Save a study note."""
    note_id = memory_store.save_note(title=req.title, content=req.content, tags=req.tags or "")
    return {"id": note_id, "title": req.title}


@router.delete("/notes/{note_id}")
def delete_note(note_id: int):
    """Delete a note."""
    memory_store.delete_note(note_id)
    return {"ok": True}


@router.get("/quizzes")
def list_quizzes(limit: int = 20):
    """Retrieve quiz score history."""
    return memory_store.get_quiz_history(limit=limit)


@router.post("/quizzes")
def save_quiz(req: QuizResultCreateRequest):
    """Save quiz completion result."""
    quiz_id = memory_store.save_quiz_result(
        topic=req.topic,
        score=req.score,
        total=req.total,
        session_id=req.session_id,
        details=req.details,
    )
    return {"id": quiz_id, "score": req.score, "total": req.total}


@router.post("/study/flashcards")
def generate_flashcards(req: StudyHelperRequest):
    """Generate interactive study flashcards using real Groq LLM."""
    try:
        client = LLMClient()
        cards_json = make_flashcards(topic=req.topic, notes_text=req.content, llm_client=client)
        cards = json.loads(cards_json)
        return {"flashcards": cards}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/study/quiz")
def generate_quiz(req: StudyHelperRequest):
    """Generate multiple-choice quiz using real Groq LLM."""
    try:
        client = LLMClient()
        quiz_json = make_quiz(topic=req.topic, notes_text=req.content, n=req.n or 5, llm_client=client)
        questions = json.loads(quiz_json)
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/stream")
async def stream_agent_execution(req: RunAgentRequest):
    """
    Stream live agent events (plan, tool calls, results, reflection, final answer)
    over Server-Sent Events (SSE).
    """
    session_id = req.session_id
    if not session_id:
        title = req.goal[:50].strip() or "Untitled Session"
        session_id = memory_store.create_session(goal=req.goal, title=title)

    async def event_generator():
        yield {
            "event": "session_init",
            "data": json.dumps({"session_id": session_id}),
        }

        orchestrator = Orchestrator(memory_store=memory_store)
        for event in orchestrator.run(goal=req.goal, session_id=session_id):
            # Apply safety disclaimer guardrails to final answers
            if event.get("type") == "final_answer":
                event["answer"] = check_output(event["answer"])
            yield {
                "event": "agent_event",
                "data": json.dumps(event),
            }

    return EventSourceResponse(event_generator())
