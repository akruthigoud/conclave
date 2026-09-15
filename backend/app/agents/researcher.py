"""
Researcher agent: for one subtask, runs a real web search and turns
the results into a grounded finding.

Search happens identically in demo and real-LLM mode — only the
summarization step branches. This means the demo path is never
searching against nothing; it's genuinely retrieving live results and
presenting them, just without LLM-generated prose stitching them
together.
"""

from app.models.state import Finding
from app.services.llm import LLMProvider
from app.services.search import search

_RESEARCHER_SYSTEM = (
    "You are a research assistant. Using ONLY the search results provided, "
    "write a concise 2-4 sentence summary answering the subtask. "
    "If the results don't cover it, say so plainly rather than inventing detail."
)


def research(subtask: str, provider: LLMProvider) -> Finding:
    results = search(subtask)

    if not results:
        return Finding(
            subtask=subtask,
            summary="No search results were available for this subtask.",
            sources=[],
        )

    sources = [r.url for r in results if r.url]

    if not provider.is_real_reasoning:
        summary = _template_summary(results)
    else:
        context = "\n\n".join(f"- {r.title}: {r.snippet}" for r in results)
        user_prompt = f"Subtask: {subtask}\n\nSearch results:\n{context}"
        summary = provider.complete(_RESEARCHER_SYSTEM, user_prompt)

    return Finding(subtask=subtask, summary=summary, sources=sources)


def _template_summary(results: list) -> str:
    """Demo-mode fallback: presents the real, retrieved snippets directly
    rather than fabricating a synthesized paragraph an LLM would normally
    produce — honest about what a template can and can't do."""
    lines = [f"{r.title}: {r.snippet}" for r in results[:3] if r.snippet]
    return " / ".join(lines) if lines else "Search returned results with no usable snippet text."
