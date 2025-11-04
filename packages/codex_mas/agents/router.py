"""Routing agent responsible for selecting the workflow path."""
from __future__ import annotations

from pydantic_ai import Agent, RunContext

from codex_mas.config.settings import Deps
from codex_mas.llm.registry import select_model
from codex_mas.schemas.models import RouterDecision, UserQuery

ROUTER_SYSTEM_PROMPT = """
You are RouterAgent, the entry point for Codex MAS.
- Goal: inspect the user query and choose the correct processing route.
- Available routes: "code", "summarize", "research_only".
- Output strictly conforms to the RouterDecision schema as JSON.
- Provide a concise reasoning string; no markdown, no prose introductions.
- Consider constraints, style preferences, security, and feasibility.
- Never invoke tools directly; only provide decisions.
""".strip()


def build_agent(deps: Deps) -> Agent:
    """Instantiate the router agent bound to the router model."""

    model = select_model(deps.llms, "router")
    agent = Agent(
        system_prompt=ROUTER_SYSTEM_PROMPT,
        model=model,
        result_type=RouterDecision,
        deps_type=Deps,
        name="router",
    )

    @agent.tool
    def remaining_budget(ctx: RunContext[Deps]) -> int:
        """Expose remaining token budget to the router."""

        return ctx.deps.token_budget

    return agent


def format_input(query: UserQuery) -> str:
    """Prepare prompt text for the router model."""

    constraints = "\n".join(f"- {item}" for item in query.constraints) or "(none)"
    style = query.preferred_style or "not specified"
    return (
        "USER GOAL:\n"
        f"{query.goal}\n\n"
        "CONSTRAINTS:\n"
        f"{constraints}\n\n"
        f"PREFERRED STYLE: {style}"
    )


__all__ = ["build_agent", "format_input", "ROUTER_SYSTEM_PROMPT"]

