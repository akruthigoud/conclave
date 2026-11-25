"""App settings, loaded from environment variables / .env."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Conclave"

    # LLM backend: "demo" needs no API key; "openai" / "groq" need a key
    llm_provider: Literal["demo", "openai", "groq"] = "demo"
    openai_model: str = "gpt-4o-mini"
    groq_model: str = "llama-3.1-8b-instant"
    openai_api_key: str | None = None
    groq_api_key: str | None = None

    # search backend
    search_provider: Literal["duckduckgo", "none"] = "duckduckgo"
    max_search_results_per_subtask: int = 4

    # graph behavior
    max_subtasks: int = 4
    max_critique_rounds: int = Field(
        default=2, description="Upper bound on planner<->critic loops before forcing a final write-up"
    )

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
