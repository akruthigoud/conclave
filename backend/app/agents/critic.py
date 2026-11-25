"""Critic agent: checks whether the findings cover the question and lists any gaps.

If gaps are found, the graph routes back to research before writing.
"""

from app.core.config import get_settings
from app.models.state import Critique, Finding
from app.services.llm import LLMProvider

_MIN_USABLE_SUMMARY_CHARS = 40


def critique(findings: list[Finding], provider: LLMProvider) -> Critique:
    thin_findings = [
        f["subtask"]
        for f in findings
        if len(f["summary"]) < _MIN_USABLE_SUMMARY_CHARS or not f["sources"]
    ]

    if not provider.is_real_reasoning:
        # demo mode: every subtask needs a non-trivial, sourced finding
        return Critique(is_sufficient=len(thin_findings) == 0, gaps=thin_findings)

    # with a real LLM, ask it to judge coverage, not just length
    system = (
        "You are a research critic. Given subtask findings, decide if together "
        "they sufficiently cover the topic. Reply with 'SUFFICIENT' or list the "
        "specific gaps, one per line, prefixed with 'GAP:'."
    )
    user = "\n\n".join(f"Subtask: {f['subtask']}\nFinding: {f['summary']}" for f in findings)
    response = provider.complete(system, user)

    if "SUFFICIENT" in response.upper() and "GAP:" not in response.upper():
        return Critique(is_sufficient=True, gaps=[])

    gaps = [line.split("GAP:", 1)[1].strip() for line in response.splitlines() if "GAP:" in line.upper()]
    return Critique(is_sufficient=len(gaps) == 0, gaps=gaps or thin_findings)


def max_rounds_reached(round_number: int) -> bool:
    return round_number >= get_settings().max_critique_rounds
