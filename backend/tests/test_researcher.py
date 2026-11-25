from app.agents.researcher import research
from app.services.llm import DemoProvider
from app.services.search import SearchResult


def test_research_with_no_results(monkeypatch):
    monkeypatch.setattr("app.agents.researcher.search", lambda subtask: [])

    finding = research("Obscure topic with no results", DemoProvider())

    assert finding["sources"] == []
    assert "No search results" in finding["summary"]


def test_research_demo_mode_uses_real_snippets(monkeypatch):
    fake_results = [
        SearchResult(title="Source A", snippet="Fact one about the topic.", url="https://a.example"),
        SearchResult(title="Source B", snippet="Fact two about the topic.", url="https://b.example"),
    ]
    monkeypatch.setattr("app.agents.researcher.search", lambda subtask: fake_results)

    finding = research("Some subtask", DemoProvider())

    assert "Fact one about the topic." in finding["summary"]
    assert "Fact two about the topic." in finding["summary"]
    assert finding["sources"] == ["https://a.example", "https://b.example"]


def test_research_with_real_provider_calls_complete(monkeypatch):
    fake_results = [SearchResult(title="T", snippet="S", url="https://x.example")]
    monkeypatch.setattr("app.agents.researcher.search", lambda subtask: fake_results)

    class FakeRealProvider:
        is_real_reasoning = True
        name = "fake-real"

        def complete(self, system, user):
            assert "Some subtask" in user
            return "A synthesized answer."

    finding = research("Some subtask", FakeRealProvider())
    assert finding["summary"] == "A synthesized answer."
