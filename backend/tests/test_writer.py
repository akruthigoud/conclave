from app.agents.writer import write_report
from app.models.state import Finding
from app.services.llm import DemoProvider


def test_write_report_demo_mode_includes_all_findings():
    findings = [
        Finding(subtask="Background", summary="Some background info.", sources=["https://a.example"]),
        Finding(subtask="Current state", summary="Some current info.", sources=[]),
    ]

    report = write_report("What is X?", findings, DemoProvider())

    assert "What is X?" in report
    assert "Background" in report
    assert "Some background info." in report
    assert "https://a.example" in report
    assert "Current state" in report


def test_write_report_omits_sources_line_when_none_present():
    findings = [Finding(subtask="Topic", summary="Summary text.", sources=[])]
    report = write_report("Q?", findings, DemoProvider())
    assert "**Sources:**" not in report


def test_write_report_with_real_provider_delegates_to_llm():
    class FakeProvider:
        is_real_reasoning = True

        def complete(self, system, user):
            assert "Background" in user
            return "A polished synthesized report."

    findings = [Finding(subtask="Background", summary="info", sources=["s"])]
    report = write_report("Q?", findings, FakeProvider())
    assert report == "A polished synthesized report."
