"""Researcher agent collects evidence via tools."""
from __future__ import annotations

from typing import Sequence

from pydantic_ai import Agent, RunContext

from codex_mas.config.settings import Deps
from codex_mas.llm.registry import select_model
from codex_mas.schemas.models import EvidenceList, UserQuery
from codex_mas.tools.rag import rag_retrieve
from codex_mas.tools.web_search import SearchHit, web_search

RESEARCHER_SYSTEM_PROMPT = """
You are ResearcherAgent.
- Collect grounded evidence supporting the user's goal.
- Prefer calling the provided search and RAG tools before reasoning.
- Extract concise quotes and assign relevance scores (0-1).
- Identify missing information in the `gaps` list.
- Output must strictly follow the EvidenceList schema as JSON.
- Do not fabricate citations or claim certainty without support.
""".strip()


def _normalize_hits(hits: Sequence[SearchHit]) -> list[dict[str, str]]:
    return [hit.model_dump() for hit in hits]


def build_agent(deps: Deps) -> Agent:
    model = select_model(deps.llms, "researcher")
    agent = Agent(
        name="researcher",
        system_prompt=RESEARCHER_SYSTEM_PROMPT,
        model=model,
        result_type=EvidenceList,
        deps_type=Deps,
    )

    @agent.tool
    def search(ctx: RunContext[Deps], query: str, k: int = 6) -> list[dict[str, str]]:
        ctx.deps.cache_dir.mkdir(parents=True, exist_ok=True)
        hits = web_search(query, k=k)
        return _normalize_hits(hits)

    @agent.tool
    def retrieve(ctx: RunContext[Deps], query: str, k: int = 6) -> list[dict[str, str]]:
        if ctx.deps.rag is not None:
            docs = ctx.deps.rag.retrieve(query, k=k)
        else:
            docs = rag_retrieve(query, k=k)
        return docs

    return agent


def format_input(query: UserQuery, prior: EvidenceList | None = None) -> str:
    """Prepare the researcher prompt body."""

    constraints = "\n".join(f"- {item}" for item in query.constraints) or "(none)"
    prompt = [
        "USER GOAL:",
        query.goal,
        "",
        "CONSTRAINTS:",
        constraints,
    ]
    if query.preferred_style:
        prompt.extend(["", f"PREFERRED STYLE: {query.preferred_style}"])
    if prior and prior.gaps:
        prompt.extend(["", "KNOWN GAPS:"])
        prompt.extend(f"- {gap}" for gap in prior.gaps)
    return "\n".join(prompt)


__all__ = ["build_agent", "format_input", "RESEARCHER_SYSTEM_PROMPT"]

