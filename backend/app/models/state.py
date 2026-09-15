"""
The state object every node in the graph reads from and writes to.

LangGraph passes this dict-like state between nodes; using a TypedDict
(rather than passing loose positional arguments) makes the contract
between agents explicit and lets a type checker catch a node that
forgets to populate a field the next node depends on.
"""

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
