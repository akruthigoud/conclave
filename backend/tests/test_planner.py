from app.agents.planner import _extract_topic, _parse_numbered_list, plan
from app.services.llm import DemoProvider


def test_extract_topic_strips_question_scaffolding():
    assert _extract_topic("What is quantum computing?") == "quantum computing"
    assert _extract_topic("How does photosynthesis work?") == "photosynthesis work"
    assert _extract_topic("Explain neural networks") == "neural networks"


def test_extract_topic_handles_plain_statement():
    assert _extract_topic("Renewable energy trends") == "Renewable energy trends"


def test_parse_numbered_list_handles_various_formats():
    text = "1. First item\n2) Second item\n- Third item\n* Fourth item"
    assert _parse_numbered_list(text) == ["First item", "Second item", "Third item", "Fourth item"]


def test_parse_numbered_list_ignores_blank_lines():
    text = "1. First\n\n2. Second\n\n"
    assert _parse_numbered_list(text) == ["First", "Second"]


def test_plan_demo_mode_produces_bounded_subtasks():
    provider = DemoProvider()
    subtasks = plan("What is renewable energy?", provider)

    assert 1 <= len(subtasks) <= 4
    assert all("renewable energy" in s for s in subtasks)
    # no duplicate subtasks
    assert len(set(subtasks)) == len(subtasks)


def test_plan_demo_mode_never_exceeds_configured_max(monkeypatch):
    from app.core import config

    monkeypatch.setattr(config.get_settings(), "max_subtasks", 2)
    provider = DemoProvider()
    subtasks = plan("What is AI safety?", provider)
    assert len(subtasks) <= 2
