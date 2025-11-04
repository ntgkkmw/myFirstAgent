"""LLM registry and adapters for pydantic_ai."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Protocol

try:  # pragma: no cover - optional dependency
    from openai import OpenAI
except ModuleNotFoundError:  # pragma: no cover - guard for docs/testing
    OpenAI = None  # type: ignore[assignment]

try:  # pragma: no cover
    from pydantic_ai.models.openai import OpenAIModel
except ModuleNotFoundError as exc:  # pragma: no cover
    raise RuntimeError(
        "pydantic-ai with the OpenAI extra is required. Install with 'pip install pydantic-ai[openai]'"
    ) from exc


class LLMClient(Protocol):
    """Protocol describing how we interact with LLM providers."""

    name: str

    def as_model(self) -> Any:
        """Return a pydantic_ai model instance compatible with Agent."""

    def complete(self, messages: Iterable[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        """Low-level completion API primarily for diagnostics."""


@dataclass(slots=True)
class OpenAIClient:
    """OpenAI chat-completions wrapper compatible with pydantic_ai."""

    model: str
    api_key: str

    def __post_init__(self) -> None:
        if OpenAI is None:  # pragma: no cover - missing optional dependency
            raise RuntimeError("openai python client is required. Install with 'pip install openai>=1.0.0'.")
        self._client = OpenAI(api_key=self.api_key)

    @property
    def name(self) -> str:  # pragma: no cover - trivial
        return self.model

    def as_model(self) -> OpenAIModel:
        return OpenAIModel(model=self.model, client=self._client)

    def complete(self, messages: Iterable[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:  # pragma: no cover - diag only
        response = self._client.chat.completions.create(model=self.model, messages=list(messages), **kwargs)
        return response.model_dump() if hasattr(response, "model_dump") else response


def select_model(llms: Dict[str, LLMClient], role: str) -> OpenAIModel:
    try:
        return llms[role].as_model()
    except KeyError as exc:  # pragma: no cover - misconfiguration guard
        raise KeyError(f"No LLM client registered for role '{role}'. Available roles: {list(llms)}") from exc


__all__ = ["LLMClient", "OpenAIClient", "select_model"]

