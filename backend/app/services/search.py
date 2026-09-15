"""
Web search, free and keyless by default.

DuckDuckGo's HTML search requires no signup or API key, which keeps
the zero-cost-by-default philosophy consistent with the LLM layer —
the researcher agent does real, live retrieval even when no LLM
provider is configured.
"""

from dataclasses import dataclass

from app.core.config import get_settings


@dataclass
class SearchResult:
    title: str
    snippet: str
    url: str


def search(query: str, max_results: int | None = None) -> list[SearchResult]:
    settings = get_settings()
    if settings.search_provider == "none":
        return []

    limit = max_results or settings.max_search_results_per_subtask

    from ddgs import DDGS  # imported lazily — network dependency, not needed for unit tests

    results: list[SearchResult] = []
    with DDGS() as ddgs:
        for hit in ddgs.text(query, max_results=limit):
            results.append(
                SearchResult(
                    title=hit.get("title", ""),
                    snippet=hit.get("body", ""),
                    url=hit.get("href", ""),
                )
            )
    return results
