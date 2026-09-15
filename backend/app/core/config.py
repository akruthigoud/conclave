"""Centralized configuration, mirroring the same pattern used across
this portfolio's other projects: every tunable lives here, read once
from environment variables, never scattered through the codebase."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Conclave"

    # --- Generation backend ---
    # "demo"   -> deterministic templated responses, zero cost, zero API key,
    #             so the graph topology and agent handoffs can be inspected
    #             and demoed without paying for tokens.
    # "openai" / "groq" -> real reasoning, requires an API key.
    llm_provider: Literal["demo", "openai", "groq"] = "demo"
    openai_model: str = "gpt-4o-mini"
    groq_model: str = "llama-3.1-8b-instant"
    openai_api_key: str | None = None
    groq_api_key: str | None = None

    # --- Search backend ---
    # DuckDuckGo requires no API key or signup, which keeps the zero-cost
    # default consistent with the LLM backend above.
    search_provider: Literal["duckduckgo", "none"] = "duckduckgo"
    max_search_results_per_subtask: int = 4

    # --- Graph behavior ---
    max_subtasks: int = 4
    max_critique_rounds: int = Field(
        default=2, description="Upper bound on planner<->critic loops before forcing a final write-up"
    )

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
