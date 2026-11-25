"""Web search via DuckDuckGo (no API key needed)."""

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

    from ddgs import DDGS  # lazy import

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
