"""Writer agent: the terminal node — turns accumulated findings into
one coherent, structured report with inline source attribution."""

from app.models.state import Finding
from app.services.llm import LLMProvider

_WRITER_SYSTEM = (
    "You are a technical writer. Synthesize the following research findings into "
    "a clear, well-structured report answering the original question. Use "
    "markdown headings per subtask. Cite sources inline where relevant."
)


def write_report(question: str, findings: list[Finding], provider: LLMProvider) -> str:
    if not provider.is_real_reasoning:
        return _template_report(question, findings)

    findings_block = "\n\n".join(
        f"### {f['subtask']}\n{f['summary']}\nSources: {', '.join(f['sources']) or 'none'}"
        for f in findings
    )
    user_prompt = f"Original question: {question}\n\n{findings_block}"
    return provider.complete(_WRITER_SYSTEM, user_prompt)


def _template_report(question: str, findings: list[Finding]) -> str:
    lines = [f"# Research report: {question}", ""]
    for f in findings:
        lines.append(f"## {f['subtask']}")
        lines.append(f["summary"])
        if f["sources"]:
            lines.append("")
            lines.append("**Sources:** " + ", ".join(f["sources"]))
        lines.append("")
    return "\n".join(lines)
