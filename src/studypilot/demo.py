"""
StudyPilot Demo Mode.

Deterministic offline mock LLM that returns believable plans, tool calls,
and answers for example prompts. Works with ZERO API keys and ZERO internet.

Used for:
- Running the app without any API key
- Automated tests (pytest in CI)
- Live demos / screenshots
"""

import json
import os
from typing import Any, Dict, List, Optional

from src.studypilot.config import DEMO_MODE, GROQ_API_KEY, logger


def is_demo_mode() -> bool:
    """
    Check whether the application should run in demo mode.

    Returns True if STUDYPILOT_DEMO env var is set or GROQ_API_KEY is missing.
    """
    if DEMO_MODE:
        return True
    if not GROQ_API_KEY:
        return True
    return False


class DemoLLM:
    """
    Deterministic offline mock that mimics the LLMClient interface.

    Detects the phase of the agent loop from message content and returns
    appropriate canned responses.
    """

    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.3,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a deterministic response based on message context."""
        if not messages:
            return {"role": "assistant", "content": ""}

        # Collect all message content for context detection
        all_content = " ".join(
            str(m.get("content", "")) for m in messages if m.get("content")
        ).lower()
        last_content = str(messages[-1].get("content", "")).lower()
        system_content = ""
        for m in messages:
            if m.get("role") == "system":
                system_content += str(m.get("content", "")).lower() + " "

        has_tool_results = any(m.get("role") == "tool" for m in messages)

        # Detect agent phase from system prompt keywords
        is_planning = "plan" in system_content and "steps" in system_content
        is_reflecting = "reflect" in system_content or "critic" in system_content
        is_flashcard_request = "flashcard" in all_content
        is_quiz_request = "quiz" in all_content and "question" in system_content

        # ── Reflection phase ────────────────────────────────────
        if is_reflecting:
            return {
                "role": "assistant",
                "content": json.dumps({
                    "ok": True,
                    "issues": [],
                    "revised_answer": "",
                }),
            }

        # ── Flashcard generation ────────────────────────────────
        if is_flashcard_request and "front" in system_content:
            return {"role": "assistant", "content": self._flashcards_for(all_content)}

        # ── Quiz generation ─────────────────────────────────────
        if is_quiz_request:
            return {"role": "assistant", "content": self._quiz_for(all_content)}

        # ── Planning phase ──────────────────────────────────────
        if is_planning:
            return {"role": "assistant", "content": self._plan_for(all_content)}

        # ── Execution phase (tool calling) ──────────────────────
        if tools and not has_tool_results:
            return self._tool_calls_for(all_content)

        # ── Execution phase (after tool results → final text) ───
        if has_tool_results:
            return {"role": "assistant", "content": self._answer_for(all_content)}

        # ── Default text response ───────────────────────────────
        return {"role": "assistant", "content": self._answer_for(all_content)}

    def generate_text(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.3,
    ) -> str:
        """Convenience: return just the text content."""
        result = self.generate(messages, temperature=temperature)
        return result.get("content") or ""

    # ── Private helpers ─────────────────────────────────────────

    def _plan_for(self, text: str) -> str:
        """Return a plan JSON based on detected topic."""
        if "black hole" in text:
            plan = {
                "steps": [
                    {"step": 1, "description": "Search for current information about black holes", "tools_needed": ["web_search"]},
                    {"step": 2, "description": "Get Wikipedia summary on black holes", "tools_needed": ["wikipedia_summary"]},
                    {"step": 3, "description": "Compile a comprehensive explanation with key concepts", "tools_needed": []},
                ]
            }
        elif "solar" in text or "wind" in text or "energy" in text:
            plan = {
                "steps": [
                    {"step": 1, "description": "Research solar energy advantages and costs", "tools_needed": ["web_search"]},
                    {"step": 2, "description": "Research wind energy advantages and costs", "tools_needed": ["web_search"]},
                    {"step": 3, "description": "Compare both energy sources and provide analysis", "tools_needed": ["calculator"]},
                ]
            }
        elif "neural network" in text:
            plan = {
                "steps": [
                    {"step": 1, "description": "Search for information on how neural networks learn", "tools_needed": ["web_search"]},
                    {"step": 2, "description": "Get Wikipedia summary on neural networks", "tools_needed": ["wikipedia_summary"]},
                    {"step": 3, "description": "Explain key concepts: forward pass, backpropagation, gradient descent", "tools_needed": []},
                ]
            }
        elif "weather" in text:
            plan = {
                "steps": [
                    {"step": 1, "description": "Get current weather data", "tools_needed": ["weather"]},
                    {"step": 2, "description": "Summarise the weather report", "tools_needed": []},
                ]
            }
        else:
            plan = {
                "steps": [
                    {"step": 1, "description": "Research the topic using web search", "tools_needed": ["web_search"]},
                    {"step": 2, "description": "Compile a comprehensive answer", "tools_needed": []},
                ]
            }
        return json.dumps(plan)

    def _tool_calls_for(self, text: str) -> Dict[str, Any]:
        """Return tool_calls based on detected topic."""
        if "black hole" in text:
            calls = [
                {
                    "id": "call_demo_1",
                    "type": "function",
                    "function": {
                        "name": "web_search",
                        "arguments": json.dumps({"query": "black holes physics explained"}),
                    },
                },
            ]
        elif "solar" in text or "energy" in text:
            calls = [
                {
                    "id": "call_demo_solar",
                    "type": "function",
                    "function": {
                        "name": "web_search",
                        "arguments": json.dumps({"query": "solar energy vs wind energy comparison"}),
                    },
                },
            ]
        elif "weather" in text:
            city = "London"
            if "tokyo" in text:
                city = "Tokyo"
            calls = [
                {
                    "id": "call_demo_weather",
                    "type": "function",
                    "function": {
                        "name": "weather",
                        "arguments": json.dumps({"city": city}),
                    },
                },
            ]
        else:
            calls = [
                {
                    "id": "call_demo_default",
                    "type": "function",
                    "function": {
                        "name": "web_search",
                        "arguments": json.dumps({"query": "research topic overview"}),
                    },
                },
            ]
        return {"role": "assistant", "content": None, "tool_calls": calls}

    def _answer_for(self, text: str) -> str:
        """Return a canned answer based on detected topic."""
        if "black hole" in text:
            return (
                "## Black Holes: A Comprehensive Overview\n\n"
                "A **black hole** is a region of spacetime where gravity is so intense that nothing — "
                "not even light or other electromagnetic waves — can escape once past the boundary known "
                "as the **event horizon**.\n\n"
                "### How Black Holes Form\n"
                "Most black holes form when massive stars (at least 20-25 times the mass of our Sun) "
                "exhaust their nuclear fuel and collapse under their own gravity in a supernova explosion. "
                "The remaining core, if massive enough, collapses to a singularity.\n\n"
                "### Types of Black Holes\n"
                "- **Stellar black holes**: 5-100 solar masses, formed from collapsed stars\n"
                "- **Supermassive black holes**: Millions to billions of solar masses, found at galaxy centres\n"
                "- **Intermediate black holes**: Between stellar and supermassive\n\n"
                "### Key Concepts\n"
                "- **Event Horizon**: The point of no return\n"
                "- **Singularity**: The infinitely dense centre\n"
                "- **Hawking Radiation**: Theoretical thermal radiation emitted near the event horizon\n"
                "- **Spaghettification**: The stretching of objects by extreme tidal forces\n\n"
                "The first image of a black hole (M87*) was captured by the Event Horizon Telescope in 2019."
            )
        elif "solar" in text or "wind" in text or "energy" in text:
            return (
                "## Solar vs Wind Energy Comparison\n\n"
                "| Feature | Solar Energy | Wind Energy |\n"
                "|---------|-------------|-------------|\n"
                "| Source | Sunlight (photovoltaic/thermal) | Wind currents |\n"
                "| Efficiency | 15-22% (panels) | 35-45% (turbines) |\n"
                "| Installation | Rooftops, deserts, farms | Open fields, offshore |\n"
                "| Consistency | Intermittent (day/weather) | Intermittent (wind patterns) |\n"
                "| Lifespan | 25-30 years | 20-25 years |\n"
                "| Maintenance | Low | Moderate |\n"
                "| Space Required | Moderate | High |\n"
                "| Noise | None | Some |\n\n"
                "### Cost Analysis\n"
                "If solar installation costs ₹50,000 and saves ₹5,000/year:\n"
                "- **Payback period** = 50,000 ÷ 5,000 = **10 years**\n"
                "- With a 25-year panel life, net savings = 15 × 5,000 = **₹75,000**\n\n"
                "Both sources are vital for a sustainable energy future."
            )
        elif "neural network" in text:
            return (
                "## How Neural Networks Learn\n\n"
                "Neural networks learn through a process of **forward propagation**, "
                "**loss calculation**, and **backpropagation**.\n\n"
                "1. **Forward Pass**: Input data flows through layers of neurons, "
                "each applying weights, biases, and activation functions.\n"
                "2. **Loss Calculation**: The network's output is compared to the expected "
                "output using a loss function (e.g., MSE, cross-entropy).\n"
                "3. **Backpropagation**: Gradients of the loss are computed with respect to "
                "each weight using the chain rule of calculus.\n"
                "4. **Weight Update**: An optimizer (e.g., SGD, Adam) adjusts weights to minimise loss.\n\n"
                "This cycle repeats over many **epochs** until the network converges."
            )
        elif "weather" in text:
            return (
                "## Weather Report\n\n"
                "**London**: Currently 15°C, partly cloudy. "
                "Forecast: 14-17°C over the next 3 days with occasional rain.\n\n"
                "**Tokyo**: Currently 22°C, clear skies. "
                "Forecast: 20-25°C over the next 3 days with sunshine."
            )
        else:
            return (
                "## Research Summary\n\n"
                "Based on my research, here is what I found about this topic.\n\n"
                "This is an interesting subject with many facets. "
                "The key points are:\n\n"
                "1. The topic has significant relevance in modern understanding\n"
                "2. Multiple perspectives exist in current research\n"
                "3. Further study is recommended for deeper understanding\n\n"
                "Feel free to ask follow-up questions for more details!"
            )

    def _flashcards_for(self, text: str) -> str:
        """Return flashcard JSON."""
        if "black hole" in text:
            cards = [
                {"front": "What is a black hole?", "back": "A region of spacetime where gravity is so strong that nothing, not even light, can escape."},
                {"front": "What is the event horizon?", "back": "The boundary around a black hole beyond which nothing can escape — the point of no return."},
                {"front": "What is Hawking radiation?", "back": "Theoretical thermal radiation predicted to be emitted near the event horizon due to quantum effects."},
                {"front": "What is spaghettification?", "back": "The stretching of objects into long thin shapes by extreme tidal forces near a black hole."},
                {"front": "What was the first black hole image?", "back": "The supermassive black hole M87*, imaged by the Event Horizon Telescope in 2019."},
            ]
        else:
            cards = [
                {"front": "What is the main concept?", "back": "The fundamental idea discussed in this topic."},
                {"front": "Why is this topic important?", "back": "It has significant applications in science and technology."},
                {"front": "What are the key components?", "back": "The topic consists of several interconnected ideas and principles."},
                {"front": "Who are key contributors?", "back": "Many researchers and scientists have contributed to this field."},
                {"front": "What are current developments?", "back": "Research continues to expand our understanding of this topic."},
            ]
        return json.dumps(cards)

    def _quiz_for(self, text: str) -> str:
        """Return quiz JSON."""
        if "black hole" in text:
            questions = [
                {"question": "What prevents anything from escaping a black hole?", "options": ["A) Magnetic force", "B) Extreme gravity", "C) Nuclear force", "D) Dark energy"], "correct": "B", "explanation": "Black holes have such extreme gravitational pull that nothing, not even light, can escape."},
                {"question": "What is the boundary of a black hole called?", "options": ["A) Singularity", "B) Corona", "C) Event horizon", "D) Photon sphere"], "correct": "C", "explanation": "The event horizon is the boundary beyond which nothing can escape a black hole."},
                {"question": "What type of black hole is found at the centre of galaxies?", "options": ["A) Stellar", "B) Micro", "C) Intermediate", "D) Supermassive"], "correct": "D", "explanation": "Supermassive black holes with millions to billions of solar masses exist at the centres of most galaxies."},
                {"question": "What is Hawking radiation?", "options": ["A) Light from stars near black holes", "B) Theoretical thermal radiation near the event horizon", "C) X-rays from accretion disks", "D) Gamma ray bursts"], "correct": "B", "explanation": "Hawking radiation is theoretical thermal radiation predicted to be emitted near the event horizon due to quantum effects."},
                {"question": "When was the first black hole image captured?", "options": ["A) 2015", "B) 2017", "C) 2019", "D) 2021"], "correct": "C", "explanation": "The Event Horizon Telescope captured the first image of black hole M87* in April 2019."},
            ]
        else:
            questions = [
                {"question": "What is the primary focus of this topic?", "options": ["A) Understanding core concepts", "B) Memorising dates", "C) Learning languages", "D) Physical exercise"], "correct": "A", "explanation": "The topic focuses on understanding fundamental concepts."},
                {"question": "Why is research important?", "options": ["A) It's not important", "B) To expand knowledge", "C) To pass time", "D) For entertainment only"], "correct": "B", "explanation": "Research expands our collective knowledge and drives progress."},
                {"question": "What method is best for learning?", "options": ["A) Passive reading only", "B) Active recall and practice", "C) Copying notes", "D) Watching only"], "correct": "B", "explanation": "Active recall and practice are proven to be the most effective learning methods."},
                {"question": "How does studying benefit you?", "options": ["A) No benefits", "B) Only grades", "C) Knowledge and critical thinking", "D) Social status only"], "correct": "C", "explanation": "Studying builds knowledge and develops critical thinking skills."},
                {"question": "What is a good study habit?", "options": ["A) Cramming the night before", "B) Consistent daily review", "C) Skipping difficult topics", "D) Only reading summaries"], "correct": "B", "explanation": "Consistent daily review with spaced repetition is the most effective study strategy."},
            ]
        return json.dumps(questions)
