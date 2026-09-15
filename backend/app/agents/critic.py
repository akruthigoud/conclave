"""
Critic agent: the quality gate between research and writing.

Without this node, the graph would always write a report after exactly
one research pass regardless of how thin the findings were. The critic
is what makes this a *loop* rather than a fixed pipeline — it can send
the graph back to research specific gaps before allowing a final report.
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
        # Demo mode uses the same coverage heuristic a real critic prompt
        # would ultimately be checked against: does every subtask have a
        # non-trivial, sourced finding?
        return Critique(is_sufficient=len(thin_findings) == 0, gaps=thin_findings)

    # With a real LLM available, ask it to judge substantive coverage,
    # not just length — a long finding can still miss the point.
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
