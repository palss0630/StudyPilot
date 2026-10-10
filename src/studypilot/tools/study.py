"""
Study material generation tools – flashcards and quizzes.

When llm_client is None (e.g. in demo mode or registry default), returns
example JSON so the app still works without an API key.
"""

import json
import traceback
from typing import Any, Optional

from src.studypilot.config import logger


def make_flashcards(
    topic: str,
    notes_text: str,
    llm_client: Any = None,
) -> str:
    """
    Generate study flashcards for a topic.

    Args:
        topic: The study topic.
        notes_text: Text content to base flashcards on.
        llm_client: An LLMClient or DemoLLM instance. If None, returns examples.

    Returns:
        JSON string of flashcard array [{front, back}, ...].
    """
    try:
        if llm_client is None:
            return json.dumps([
                {"front": f"What is {topic}?", "back": f"A key concept in the study of {topic}."},
                {"front": f"Why is {topic} important?", "back": "It has significant applications in science and daily life."},
                {"front": "What are the main components?", "back": "Several interconnected ideas and principles."},
            ])

        prompt = (
            f"Create 5 study flashcards for the topic '{topic}' based on this text.\n"
            f"Output ONLY a JSON array of objects with 'front' and 'back' keys.\n\n"
            f"Text:\n{notes_text[:3000]}"
        )
        from src.studypilot.agent.prompts import STUDY_MATERIAL_PROMPT
        messages = [
            {"role": "system", "content": STUDY_MATERIAL_PROMPT},
            {"role": "user", "content": prompt},
        ]
        response_text = llm_client.generate_text(messages, temperature=0.4)

        # Try to parse to validate JSON
        try:
            cards = json.loads(response_text)
            return json.dumps(cards)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            start = response_text.find("[")
            end = response_text.rfind("]")
            if start != -1 and end != -1:
                return response_text[start : end + 1]
            return response_text

    except Exception as e:
        logger.error(f"Error making flashcards: {e}\n{traceback.format_exc()}")
        return json.dumps([
            {"front": "Error generating flashcards", "back": str(e)},
        ])


def make_quiz(
    topic: str,
    notes_text: str,
    n: int = 5,
    llm_client: Any = None,
) -> str:
    """
    Generate a multiple-choice quiz for a topic.

    Args:
        topic: The study topic.
        notes_text: Text content to base quiz on.
        n: Number of questions (default 5).
        llm_client: An LLMClient or DemoLLM instance. If None, returns examples.

    Returns:
        JSON string of quiz array [{question, options, correct, explanation}, ...].
    """
    try:
        if llm_client is None:
            return json.dumps([
                {
                    "question": f"What is a key aspect of {topic}?",
                    "options": [
                        "A) It is well-studied",
                        "B) It is not important",
                        "C) It was discovered recently",
                        "D) None of the above",
                    ],
                    "correct": "A",
                    "explanation": f"{topic} is a well-studied area of knowledge.",
                },
            ] * min(n, 5))

        prompt = (
            f"Create a {n}-question multiple choice quiz for '{topic}' based on this text.\n"
            f"Output ONLY a JSON array. Each object must have:\n"
            f'- "question": the question text\n'
            f'- "options": array of 4 strings like ["A) ...", "B) ...", "C) ...", "D) ..."]\n'
            f'- "correct": the letter of the correct answer (e.g. "A")\n'
            f'- "explanation": brief explanation\n\n'
            f"Text:\n{notes_text[:3000]}"
        )
        from src.studypilot.agent.prompts import STUDY_MATERIAL_PROMPT
        messages = [
            {"role": "system", "content": STUDY_MATERIAL_PROMPT},
            {"role": "user", "content": prompt},
        ]
        response_text = llm_client.generate_text(messages, temperature=0.4)

        # Try to parse to validate JSON
        try:
            questions = json.loads(response_text)
            return json.dumps(questions)
        except json.JSONDecodeError:
            start = response_text.find("[")
            end = response_text.rfind("]")
            if start != -1 and end != -1:
                return response_text[start : end + 1]
            return response_text

    except Exception as e:
        logger.error(f"Error making quiz: {e}\n{traceback.format_exc()}")
        return json.dumps([
            {
                "question": "Error generating quiz",
                "options": ["A) Try again", "B) Check logs", "C) Use demo mode", "D) Report bug"],
                "correct": "A",
                "explanation": str(e),
            },
        ])
