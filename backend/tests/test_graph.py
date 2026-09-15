"""
End-to-end tests of the compiled graph, running the real demo provider
(no LLM needed) with the search function mocked so tests are fast and
don't depend on network access or DuckDuckGo's availability.
"""

from app.core.graph import run_research
from app.services.search import SearchResult


def _fake_search(subtask: str) -> list[SearchResult]:
    return [
        SearchResult(title=f"Result for {subtask}", snippet=f"Detailed information about {subtask}.", url=f"https://example.com/{hash(subtask) % 1000}")
    ]


def test_run_research_end_to_end_produces_report(monkeypatch):
    monkeypatch.setattr("app.agents.researcher.search", _fake_search)

    result = run_research("What is renewable energy?")

    assert result["question"] == "What is renewable energy?"
    assert len(result["subtasks"]) > 0
    assert len(result["findings"]) == len(result["subtasks"])
    assert result["report"] is not None
    assert "renewable energy" in result["report"]
    assert result["round"] >= 1


def test_run_research_terminates_within_max_rounds(monkeypatch):
    """Even findings that would repeatedly look 'thin' to the critic must
    not loop forever — this is the test that would fail if the round
    counter or routing logic had an off-by-one bug."""
    monkeypatch.setattr("app.agents.researcher.search", lambda subtask: [])  # always empty -> always "thin"

    result = run_research("What is an untestable hypothetical?")

    from app.core.config import get_settings

    assert result["round"] <= get_settings().max_critique_rounds + 1
    assert result["report"] is not None  # graph must still reach `write`, not hang


def test_run_research_every_finding_has_matching_subtask(monkeypatch):
    monkeypatch.setattr("app.agents.researcher.search", _fake_search)

    result = run_research("How does encryption work?")

    finding_subtasks = {f["subtask"] for f in result["findings"]}
    assert finding_subtasks.issubset(set(result["subtasks"]))
