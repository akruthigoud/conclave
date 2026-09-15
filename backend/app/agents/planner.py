"""
Planner agent: turns one broad research question into a small set of
concrete, independently-searchable subtasks.

Splitting the question up front — rather than researching it as one
blob — is what lets the researcher agent run focused searches instead
of one query trying to cover everything at once, and lets the critic
reason about coverage subtask-by-subtask.
"""

import re

from app.core.config import get_settings
from app.services.llm import LLMProvider

_PLANNER_SYSTEM = (
    "You are a research planner. Given a question, break it into 3-4 concrete, "
    "independently-researchable subtasks that together would let someone answer "
    "the question thoroughly. Reply with ONLY a numbered list, one subtask per line."
)

_DEMO_ANGLES = [
    "Background and definition of {topic}",
    "Current state and recent developments in {topic}",
    "Key challenges, risks, or criticisms of {topic}",
    "Outlook and what's likely to change about {topic}",
]


def plan(question: str, provider: LLMProvider) -> list[str]:
    settings = get_settings()
    max_subtasks = settings.max_subtasks

    if not provider.is_real_reasoning:
        topic = _extract_topic(question)
        return [angle.format(topic=topic) for angle in _DEMO_ANGLES[:max_subtasks]]

    raw = provider.complete(_PLANNER_SYSTEM, question)
    subtasks = _parse_numbered_list(raw)
    return subtasks[:max_subtasks] if subtasks else [question]


def _extract_topic(question: str) -> str:
    """Best-effort topic extraction for the demo path: strips common question
    scaffolding ('what is', 'how does', trailing '?') to get a noun phrase
    that reads naturally inside the template angles above."""
    cleaned = question.strip().rstrip("?")
    cleaned = re.sub(
        r"^(what is|what are|how does|how do|why is|why are|explain|tell me about)\s+",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned or question


def _parse_numbered_list(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        stripped = re.sub(r"^\s*\d+[\.\)]\s*", "", line).strip()
        stripped = re.sub(r"^[-*]\s*", "", stripped)
        if stripped:
            lines.append(stripped)
    return lines
