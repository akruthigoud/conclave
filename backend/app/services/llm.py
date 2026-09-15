"""
Pluggable text-generation backends behind one interface — the same
Strategy pattern used elsewhere in this portfolio, applied here to
agent reasoning instead of RAG answer synthesis.

`DemoProvider` deliberately does *not* try to fake real reasoning with
canned text pretending to be an LLM. Instead it does the honest thing:
every agent that calls the LLM falls back to a clearly-labeled
template transformation of its real inputs (real search results, real
question text). Nothing about the demo path is fabricated — it's just
un-synthesized. That's what makes the whole graph runnable and
inspectable with zero API key, which matters far more for a portfolio
project than a demo mode that looks impressive but is fake.
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
        """False for the demo provider — lets calling agents choose a
        template fallback instead of sending a prompt that expects an
        LLM-quality response."""
        return True


class DemoProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "demo (no LLM — deterministic templates over real search results)"

    @property
    def is_real_reasoning(self) -> bool:
        return False

    def complete(self, system: str, user: str) -> str:
        # Never called directly in demo mode — every agent checks
        # is_real_reasoning first and takes its template path instead.
        # Kept here so the interface stays uniform and swapping providers
        # never requires touching agent code.
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
