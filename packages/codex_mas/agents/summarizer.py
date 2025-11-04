"""Summarizer agent responsible for creating concise briefs."""
from __future__ import annotations

from pydantic_ai import Agent

from codex_mas.config.settings import Deps
from codex_mas.llm.registry import select_model
from codex_mas.schemas.models import Brief, EvidenceList, UserQuery

SUMMARIZER_SYSTEM_PROMPT = """
You are SummarizerAgent.
- Produce an executive brief summarizing research findings.
- Populate the `bullets` list with key takeaways and `risks` with known caveats.
- Remain faithful to supplied evidence; do not speculate.
- Output must strictly follow the Brief schema as JSON.
- Keep bullets sharp and under 40 words each.
""".strip()


def build_agent(deps: Deps) -> Agent:
    model = select_model(deps.llms, "summarizer")
    return Agent(
        name="summarizer",
        system_prompt=SUMMARIZER_SYSTEM_PROMPT,
        model=model,
        result_type=Brief,
        deps_type=Deps,
    )


def format_input(query: UserQuery, evidence: EvidenceList) -> str:
    bullets = "\n".join(f"- {item.source}: {item.quote}" for item in evidence.items)
    gaps = "\n".join(f"- {gap}" for gap in evidence.gaps) or "(none)"
    return "\n".join(
        [
            "USER GOAL:",
            query.goal,
            "",
            "EVIDENCE BULLETS:",
            bullets or "(none)",
            "",
            "KNOWN GAPS:",
            gaps,
        ]
    )


__all__ = ["build_agent", "format_input", "SUMMARIZER_SYSTEM_PROMPT"]

