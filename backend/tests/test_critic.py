from app.agents.critic import critique, max_rounds_reached
from app.models.state import Finding
from app.services.llm import DemoProvider


def _finding(subtask: str, summary: str, sources: list[str]) -> Finding:
    return Finding(subtask=subtask, summary=summary, sources=sources)


def test_critique_demo_mode_flags_thin_findings():
    findings = [
        _finding("Topic A", "A" * 100, ["https://a.example"]),
        _finding("Topic B", "too short", []),  # under length threshold AND no sources
    ]

    result = critique(findings, DemoProvider())

    assert result["is_sufficient"] is False
    assert "Topic B" in result["gaps"]
    assert "Topic A" not in result["gaps"]


def test_critique_demo_mode_sufficient_when_all_findings_are_solid():
    findings = [
        _finding("Topic A", "A" * 100, ["https://a.example"]),
        _finding("Topic B", "B" * 100, ["https://b.example"]),
    ]

    result = critique(findings, DemoProvider())

    assert result["is_sufficient"] is True
    assert result["gaps"] == []


def test_critique_with_real_provider_parses_sufficient():
    class FakeProvider:
        is_real_reasoning = True

        def complete(self, system, user):
            return "SUFFICIENT"

    result = critique([_finding("A", "x" * 100, ["s"])], FakeProvider())
    assert result["is_sufficient"] is True


def test_critique_with_real_provider_parses_gaps():
    class FakeProvider:
        is_real_reasoning = True

        def complete(self, system, user):
            return "GAP: missing recent data\nGAP: no counterargument covered"

    result = critique([_finding("A", "x" * 100, ["s"])], FakeProvider())
    assert result["is_sufficient"] is False
    assert result["gaps"] == ["missing recent data", "no counterargument covered"]


def test_max_rounds_reached_respects_setting(monkeypatch):
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "max_critique_rounds", 2)
    assert max_rounds_reached(2) is True
    assert max_rounds_reached(1) is False
