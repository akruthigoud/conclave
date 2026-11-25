"""LangGraph workflow.

    plan -> research -> critique --[sufficient or max rounds]--> write -> END
                ^                |
                +--[gaps found]--+

The critic can send the graph back to research with new subtasks.
The loop stops when coverage is sufficient or MAX_CRITIQUE_ROUNDS is reached.
"""

from langgraph.graph import END, StateGraph

from app.agents.critic import critique, max_rounds_reached
from app.agents.planner import plan
from app.agents.researcher import research
from app.agents.writer import write_report
from app.models.state import ResearchState
from app.services.llm import LLMProvider, get_provider


def _plan_node(state: ResearchState) -> dict:
    provider = get_provider()
    subtasks = plan(state["question"], provider)
    return {"subtasks": subtasks, "provider_name": provider.name}


def _research_node(state: ResearchState) -> dict:
    provider = get_provider()
    already_researched = {f["subtask"] for f in state["findings"]}
    pending = [s for s in state["subtasks"] if s not in already_researched]

    new_findings = [research(subtask, provider) for subtask in pending]
    return {"findings": state["findings"] + new_findings}


def _critique_node(state: ResearchState) -> dict:
    provider = get_provider()
    result = critique(state["findings"], provider)
    return {"critique": result, "round": state["round"] + 1}


def _route_after_critique(state: ResearchState) -> str:
    critique_result = state["critique"]
    if critique_result["is_sufficient"] or max_rounds_reached(state["round"]):
        return "write"
    # Gaps become new subtasks the research node will pick up on the next pass.
    state["subtasks"].extend(g for g in critique_result["gaps"] if g not in state["subtasks"])
    return "research"


def _write_node(state: ResearchState) -> dict:
    provider = get_provider()
    report = write_report(state["question"], state["findings"], provider)
    return {"report": report}


def build_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("plan", _plan_node)
    graph.add_node("research", _research_node)
    graph.add_node("critic", _critique_node)
    graph.add_node("write", _write_node)

    graph.set_entry_point("plan")
    graph.add_edge("plan", "research")
    graph.add_edge("research", "critic")
    graph.add_conditional_edges("critic", _route_after_critique, {"write": "write", "research": "research"})
    graph.add_edge("write", END)

    return graph.compile()


def run_research(question: str) -> ResearchState:
    app = build_graph()
    initial_state: ResearchState = {
        "question": question,
        "subtasks": [],
        "findings": [],
        "critique": None,
        "round": 0,
        "report": None,
        "provider_name": "",
    }
    result: ResearchState = app.invoke(initial_state)
    return result
