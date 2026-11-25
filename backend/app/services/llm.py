"""LLM providers behind a common interface.

DemoProvider runs without an API key: agents check is_real_reasoning
and fall back to template output built from the real search results.
"""

from abc import ABC, abstractmethod
from functools import lru_cache

from app.core.config import Settings, get_settings


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, system: str, user: str) -> str: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    def is_real_reasoning(self) -> bool:
        """False for DemoProvider, so agents use their template fallback."""
        return True


class DemoProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "demo (no LLM — deterministic templates over real search results)"

    @property
    def is_real_reasoning(self) -> bool:
        return False

    def complete(self, system: str, user: str) -> str:
        # not used: agents check is_real_reasoning and use templates instead
        raise NotImplementedError("DemoProvider does not generate text; agents branch on is_real_reasoning")


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        from openai import OpenAI  # imported lazily

        self._client = OpenAI(api_key=api_key)
        self._model = model

    @property
    def name(self) -> str:
        return f"openai:{self._model}"

    def complete(self, system: str, user: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()


class GroqProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        from groq import Groq  # imported lazily

        self._client = Groq(api_key=api_key)
        self._model = model

    @property
    def name(self) -> str:
        return f"groq:{self._model}"

    def complete(self, system: str, user: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()


def _build_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("llm_provider=openai but OPENAI_API_KEY is not set")
        return OpenAIProvider(settings.openai_api_key, settings.openai_model)

    if settings.llm_provider == "groq":
        if not settings.groq_api_key:
            raise RuntimeError("llm_provider=groq but GROQ_API_KEY is not set")
        return GroqProvider(settings.groq_api_key, settings.groq_model)

    return DemoProvider()


@lru_cache
def get_provider() -> LLMProvider:
    return _build_provider(get_settings())
