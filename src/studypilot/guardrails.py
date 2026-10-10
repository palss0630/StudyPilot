"""
Guardrails module for StudyPilot.

Provides input validation, prompt-injection detection, harmful-content blocking,
output disclaimers, and web-content sanitisation.
"""

import re
from typing import List, Optional

from pydantic import BaseModel

from src.studypilot.config import MAX_INPUT_LENGTH, logger


class GuardrailResult(BaseModel):
    """Result of an input guardrail check."""

    ok: bool
    blocked: bool = False
    message: str = ""
    sanitized_text: str = ""


# ── Prompt-injection patterns ───────────────────────────────────
_INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"ignore all instructions",
    r"disregard your instructions",
    r"you are now",
    r"act as if",
    r"pretend you are",
    r"system prompt",
    r"reveal your prompt",
    r"override safety",
    r"forget your rules",
    r"new instruction",
]

# ── Harmful-content patterns ───────────────────────────────────
_HARMFUL_PATTERNS = [
    r"how to make .{0,20}(bomb|explosive|weapon)",
    r"(make|build|create) .{0,20}(bomb|explosive|weapon)",
    r"weapons? manufacturing",
    r"explosives? manufacturing",
    r"kill myself",
    r"commit suicide",
    r"self[- ]?harm",
    r"illegal drug synthesis",
    r"synthesiz(e|ing) .{0,20}(meth|cocaine|heroin|fentanyl)",
    r"how to hack",
    r"exploit (instructions|vulnerability|system)",
]

# ── Health / legal / financial keyword sets ──────────────────
_HEALTH_TERMS = {
    "medicine", "drug", "symptom", "diagnosis", "treatment",
    "disease", "health", "medical", "dosage", "prescription",
}
_LEGAL_TERMS = {
    "law", "legal", "court", "sue", "attorney", "lawyer",
    "liability", "lawsuit", "verdict",
}
_FINANCIAL_TERMS = {
    "invest", "stock", "tax", "financial", "mortgage",
    "insurance", "loan", "trading", "crypto",
}


def check_input(text: str) -> GuardrailResult:
    """
    Validate user input for safety and quality.

    Checks:
    1. Non-empty
    2. Length ≤ MAX_INPUT_LENGTH
    3. Prompt-injection patterns → neutralise
    4. Harmful-content patterns → block with a kind message
    """
    # Empty check
    if not text or not text.strip():
        return GuardrailResult(
            ok=False,
            message="Please enter a study goal or question.",
        )

    # Length check
    if len(text) > MAX_INPUT_LENGTH:
        return GuardrailResult(
            ok=False,
            message=f"Input is too long (max {MAX_INPUT_LENGTH} characters).",
        )

    # Prompt-injection check
    for pattern in _INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning("Prompt-injection pattern detected and neutralised.")
            sanitized = re.sub(
                pattern, "[REDACTED]", text, flags=re.IGNORECASE
            )
            return GuardrailResult(
                ok=True,
                message="Prompt-injection pattern neutralised.",
                sanitized_text=sanitized.strip(),
            )

    # Harmful-content check
    for pattern in _HARMFUL_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning("Harmful content request detected and blocked.")
            return GuardrailResult(
                ok=False,
                blocked=True,
                message=(
                    "I'm designed to help with studying and research. "
                    "I can't assist with that topic, but I'd love to help "
                    "you learn something else!"
                ),
            )

    return GuardrailResult(ok=True, sanitized_text=text.strip())


def check_output(
    text: str, topic_keywords: Optional[List[str]] = None
) -> str:
    """
    Add disclaimers for health / legal / financial topics.

    If topic_keywords is not provided, extracts keywords from the text itself.
    """
    if not text:
        return text

    # If no keywords provided, extract from the text
    if not topic_keywords:
        words = set(text.lower().split())
    else:
        words = {k.lower() for k in topic_keywords}

    disclaimers: List[str] = []

    if words & _HEALTH_TERMS:
        disclaimers.append(
            "⚕️ *Disclaimer: This information is for educational purposes only "
            "and is not medical advice. Please consult a healthcare professional.*"
        )
    if words & _LEGAL_TERMS:
        disclaimers.append(
            "⚖️ *Disclaimer: This information is for educational purposes only "
            "and is not legal advice. Please consult a qualified attorney.*"
        )
    if words & _FINANCIAL_TERMS:
        disclaimers.append(
            "💰 *Disclaimer: This information is for educational purposes only "
            "and is not financial advice. Please consult a financial advisor.*"
        )

    if disclaimers:
        return text + "\n\n---\n" + "\n".join(disclaimers)

    return text


def sanitize_web_content(text: str) -> str:
    """
    Sanitise web-scraped content by stripping injected instructions
    and truncating to a reasonable length.
    """
    if not text:
        return ""

    lines = text.splitlines()
    clean_lines: List[str] = []

    for line in lines:
        skip = False
        for pattern in _INJECTION_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                skip = True
                break
        if not skip:
            clean_lines.append(line)

    sanitized = "\n".join(clean_lines)

    max_len = 10_000
    if len(sanitized) > max_len:
        sanitized = sanitized[:max_len] + "\n... [Content Truncated]"

    return sanitized
