"""Shared state passed between the graph nodes."""

from typing import TypedDict


class Finding(TypedDict):
    subtask: str
    summary: str
    sources: list[str]


class Critique(TypedDict):
    is_sufficient: bool
    gaps: list[str]


class ResearchState(TypedDict):
    question: str
    subtasks: list[str]
    findings: list[Finding]
    critique: Critique | None
    round: int
    report: str | None
    provider_name: str
