from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class FindingResponse(BaseModel):
    subtask: str
    summary: str
    sources: list[str]


class ResearchResponse(BaseModel):
    question: str
    subtasks: list[str]
    findings: list[FindingResponse]
    rounds_used: int
    report: str
    provider: str


class HealthResponse(BaseModel):
    status: str
    llm_provider: str
    search_provider: str
