from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.core.graph import run_research
from app.models.schemas import HealthResponse, ResearchRequest, ResearchResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_settings)):
    return HealthResponse(status="ok", llm_provider=settings.llm_provider, search_provider=settings.search_provider)


@router.post("/research", response_model=ResearchResponse)
def research_endpoint(request: ResearchRequest):
    result = run_research(request.question)
    return ResearchResponse(
        question=result["question"],
        subtasks=result["subtasks"],
        findings=result["findings"],
        rounds_used=result["round"],
        report=result["report"],
        provider=result["provider_name"],
    )
