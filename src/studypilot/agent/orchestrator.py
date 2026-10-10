"""
Orchestrator - ties plan -> execute -> reflect -> final answer.

Yields live events so the UI can stream progress:
  plan_created, step_start, tool_called, tool_result, step_complete,
  reflection, final_answer, error, guardrail_blocked
"""

import time
import json
from typing import Any, Dict, Generator, List, Optional

from src.studypilot.config import AGENT_TIMEOUT_SECONDS, logger
from src.studypilot.agent.llm import LLMClient
from src.studypilot.agent.planner import Planner, PlanStep
from src.studypilot.agent.executor import Executor
from src.studypilot.agent.reflector import Reflector
from src.studypilot.tools.registry import get_default_registry
from src.studypilot.memory.store import MemoryStore
from src.studypilot.guardrails import check_input


class Orchestrator:
    """
    Central orchestrator for the StudyPilot agent.

    Coordinates: input guardrails -> memory retrieval -> planning ->
    execution (with tool calls) -> reflection -> final answer -> memory save.
    """

    def __init__(
        self,
        memory_store: Optional[MemoryStore] = None,
    ) -> None:
        self.llm_client: LLMClient = LLMClient()

        # Tool registry
        self.tool_registry = get_default_registry()

        # Agent sub-modules
        self.planner = Planner(self.llm_client)
        self.executor = Executor(self.llm_client, self.tool_registry)
        self.reflector = Reflector(self.llm_client)

        # Memory
        self.memory_store = memory_store or MemoryStore()

    def get_llm_client(self) -> Any:
        """Expose the LLM client for study tools (flashcards/quiz)."""
        return self.llm_client

    def run(
        self, goal: str, session_id: Optional[str] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Run the full agent loop on a user goal.

        Yields event dicts that the UI/CLI can consume for live updates.
        """
        start_time = time.time()

        try:
            # ── 1. Input guardrails ──────────────────────────────
            guardrail_result = check_input(goal)
            if not guardrail_result.ok:
                if guardrail_result.blocked:
                    yield {
                        "type": "guardrail_blocked",
                        "message": guardrail_result.message,
                    }
                else:
                    yield {"type": "error", "message": guardrail_result.message}
                return

            # Use sanitized text (may have prompt-injection neutralised)
            safe_goal = guardrail_result.sanitized_text or goal.strip()

            # ── 2. Retrieve relevant context from long-term memory ─
            context = self.memory_store.retrieve_relevant_context(safe_goal)

            # ── 3. Create plan ───────────────────────────────────
            plan = self.planner.create_plan(safe_goal, context)
            yield {
                "type": "plan_created",
                "plan": plan.model_dump(),
            }

            # ── 4. Execute each step ─────────────────────────────
            self.executor.reset_counters()
            all_tool_observations: List[Dict[str, Any]] = []
            step_results: List[str] = []

            for plan_step in plan.steps:
                # Timeout check
                if time.time() - start_time > AGENT_TIMEOUT_SECONDS:
                    yield {
                        "type": "error",
                        "message": "Stopped: agent timeout reached.",
                    }
                    return

                yield {
                    "type": "step_start",
                    "step": plan_step.model_dump(),
                }

                # Compile context from prior step findings so executor does not repeat work
                prior_findings = "\n\n".join(
                    f"Prior step {i+1} output: {res}" for i, res in enumerate(step_results) if res
                )
                accumulated_context = context
                if prior_findings:
                    accumulated_context = f"{context}\n\n{prior_findings}".strip()

                step_result = self.executor.execute_step(
                    step_description=f"Overall Goal: {safe_goal}\nStep: {plan_step.description}",
                    context=accumulated_context,
                    messages_so_far=[],
                )

                # Yield individual tool calls
                for tc in step_result.tool_calls_made:
                    yield {
                        "type": "tool_called",
                        "name": tc.get("name", "?"),
                        "args": tc.get("args", {}),
                    }
                    # Parse args for display
                    args_parsed = tc.get("args", {})
                    if isinstance(args_parsed, str):
                        try:
                            args_parsed = json.loads(args_parsed)
                        except Exception:
                            pass

                    result_str = str(tc.get("result", ""))
                    yield {
                        "type": "tool_result",
                        "name": tc.get("name", "?"),
                        "result": result_str[:500],
                    }
                    all_tool_observations.append(tc)

                yield {
                    "type": "step_complete",
                    "step": plan_step.model_dump(),
                    "content": step_result.content,
                }
                step_results.append(step_result.content)

            # ── 5. Compile draft answer ──────────────────────────
            draft_answer = "\n\n".join(
                r for r in step_results if r and r.strip()
            )

            if not draft_answer.strip():
                draft_answer = (
                    "I researched your question but couldn't compile "
                    "a detailed answer. Please try rephrasing your goal."
                )

            # ── 6. Reflect ───────────────────────────────────────
            reflection = self.reflector.reflect(
                safe_goal, draft_answer, all_tool_observations
            )
            yield {
                "type": "reflection",
                "result": reflection.model_dump(),
            }

            # ── 7. Apply revision (max 1) ────────────────────────
            final_answer = draft_answer
            if not reflection.ok and reflection.revised_answer:
                final_answer = reflection.revised_answer

            # ── 8. Extract sources ───────────────────────────────
            sources = _extract_sources(all_tool_observations)

            # ── 9. Save to memory ────────────────────────────────
            if session_id:
                self.memory_store.add_message(session_id, "user", safe_goal)
                self.memory_store.add_message(
                    session_id, "assistant", final_answer
                )
                # Log tool calls
                for obs in all_tool_observations:
                    args = obs.get("args", {})
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except Exception:
                            args = {"raw": args}
                    self.memory_store.log_tool_call(
                        tool_name=obs.get("name", "unknown"),
                        inputs=args,
                        output=str(obs.get("result", ""))[:2000],
                        session_id=session_id,
                    )

            # ── 10. Final answer ─────────────────────────────────
            yield {
                "type": "final_answer",
                "answer": final_answer,
                "sources": sources,
            }

        except Exception as e:
            logger.exception("Orchestrator error")
            yield {"type": "error", "message": str(e)}


def _extract_sources(observations: List[Dict[str, Any]]) -> List[str]:
    """Extract unique source descriptions from tool observations."""
    sources: List[str] = []
    seen: set = set()

    for obs in observations:
        name = obs.get("name", "")
        result = str(obs.get("result", ""))

        if name == "web_search":
            # Extract URLs from search results
            for line in result.split("\n"):
                if "http" in line:
                    for word in line.split():
                        if word.startswith("http"):
                            url = word.strip("()[]<>,.")
                            if url not in seen:
                                seen.add(url)
                                sources.append(url)
        elif name == "wikipedia_summary":
            args = obs.get("args", {})
            topic = ""
            if isinstance(args, str):
                try:
                    topic = json.loads(args).get("topic", "")
                except Exception:
                    pass
            elif isinstance(args, dict):
                topic = args.get("topic", "")
            if topic:
                src = f"Wikipedia: {topic}"
                if src not in seen:
                    seen.add(src)
                    sources.append(src)
        elif name == "read_webpage":
            args = obs.get("args", {})
            url = ""
            if isinstance(args, str):
                try:
                    url = json.loads(args).get("url", "")
                except Exception:
                    pass
            elif isinstance(args, dict):
                url = args.get("url", "")
            if url and url not in seen:
                seen.add(url)
                sources.append(url)

    return sources
