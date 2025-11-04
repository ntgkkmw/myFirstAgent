"""Configuration and dependency management for the Codex MAS."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

from pydantic import BaseModel, Field, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict

from codex_mas.llm.registry import LLMClient, OpenAIClient


class PolicyConfig(BaseModel):
    """Runtime policy guard rails."""

    max_retries: int = Field(default=3, ge=1)
    coder_escalations: int = Field(default=1, ge=0)
    token_budget_total: int = Field(default=16000, ge=1000)
    summary_max_chars: int = Field(default=1200, ge=100)


class Clock(BaseModel):
    """Clock abstraction for easier testing."""

    @staticmethod
    def now() -> float:
        import time

        return time.time()


class Settings(BaseSettings):
    """Application settings loaded from environment/.env."""

    model_config = SettingsConfigDict(env_file=('.env', '.env.local'), env_prefix="", extra='ignore')

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    model_router: str = Field(default="gpt-4o-mini", alias="MODEL_ROUTER")
    model_researcher: str = Field(default="gpt-4o-mini", alias="MODEL_RESEARCHER")
    model_coder: str = Field(default="gpt-4o-mini", alias="MODEL_CODER")
    model_coder_escalate: str = Field(default="gpt-4.1", alias="MODEL_CODER_ESCALATE")
    model_tester: str = Field(default="gpt-4o-mini", alias="MODEL_TESTER")
    model_summarizer: str = Field(default="gpt-4o-mini", alias="MODEL_SUMMARIZER")
    model_reviewer: str = Field(default="gpt-4o-mini", alias="MODEL_REVIEWER")
    token_budget_total: int = Field(default=16000, alias="TOKEN_BUDGET_TOTAL")

    def create_llm_clients(self) -> Dict[str, LLMClient]:
        if not self.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required. Set it in your .env file.")

        llm_roles = {
            "router": self.model_router,
            "researcher": self.model_researcher,
            "coder": self.model_coder,
            "coder_escalate": self.model_coder_escalate,
            "tester": self.model_tester,
            "summarizer": self.model_summarizer,
            "reviewer": self.model_reviewer,
        }
        return {
            role: OpenAIClient(model=model_name, api_key=self.openai_api_key)
            for role, model_name in llm_roles.items()
        }


class Deps(BaseModel):
    """Dependency container injected into each run."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    llms: Dict[str, LLMClient]
    rag: Optional["RagClient"] = None
    policy: PolicyConfig = Field(default_factory=PolicyConfig)
    clock: Clock = Field(default_factory=Clock)
    token_budget: int = Field(default=16000)
    cache_dir: Path = Field(default_factory=lambda: Path(".cache/codex-mas"))


class RagClient(BaseModel):
    """Placeholder RAG client wrapper."""

    name: str = "local-rag"

    def retrieve(self, query: str, *, k: int = 8) -> list[dict]:  # pragma: no cover - thin wrapper
        from codex_mas.tools.rag import rag_retrieve

        return rag_retrieve(query, k=k)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


__all__ = [
    "Settings",
    "Deps",
    "PolicyConfig",
    "Clock",
    "RagClient",
    "get_settings",
]

