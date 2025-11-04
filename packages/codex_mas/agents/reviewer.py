"""Reviewer agent validates final deliverables."""
from __future__ import annotations

from pydantic_ai import Agent, RunContext

from codex_mas.config.settings import Deps
from codex_mas.llm.registry import select_model
from codex_mas.schemas.models import (
    Brief,
    CodePatch,
    EvidenceList,
    FinalAnswer,
    TestPlan,
    UserQuery,
)

REVIEWER_SYSTEM_PROMPT = """
You are ReviewerAgent, the final gatekeeper.
- Audit prior agent outputs for safety, completeness, and feasibility.
- Ensure references align with collected evidence.
- Highlight outstanding risks and next steps in `next_actions`.
- `artifacts` must include serialized outputs (diffs, plans, briefs).
- If outputs are unsafe or invalid, request follow-up actions in diagnostics.
- Respond strictly using the FinalAnswer schema in JSON.
""".strip()


def build_agent(deps: Deps) -> Agent:
    model = select_model(deps.llms, "reviewer")
    agent = Agent(
        name="reviewer",
        system_prompt=REVIEWER_SYSTEM_PROMPT,
        model=model,
        result_type=FinalAnswer,
        deps_type=Deps,
    )

    @agent.tool
    def clock(ctx: RunContext[Deps]) -> float:
        return ctx.deps.clock.now()

    return agent


def format_input(
    query: UserQuery,
    evidence: EvidenceList | None,
    coder: CodePatch | None,
    tester: TestPlan | None,
    summary: Brief | None,
) -> str:
    sections: list[str] = ["USER GOAL:", query.goal]
    if evidence is not None:
        sections.extend([
            "",
            "EVIDENCE:",
            "\n".join(f"- {item.source}: {item.quote}" for item in evidence.items) or "(none)",
            "",
            "EVIDENCE GAPS:",
            "\n".join(f"- {gap}" for gap in evidence.gaps) or "(none)",
        ])
    if coder is not None:
        sections.extend([
            "",
            "CODE PATCH:",
            coder.diff,
            "",
            "CODER RATIONALE:",
            coder.rationale,
        ])
    if tester is not None:
        sections.extend([
            "",
            "TEST PLAN SUMMARY:",
            tester.how_to_run,
        ])
    if summary is not None:
        sections.extend([
            "",
            "SUMMARY BULLETS:",
            "\n".join(summary.bullets) or "(none)",
            "",
            "SUMMARY RISKS:",
            "\n".join(summary.risks) or "(none)",
        ])
    return "\n".join(sections)


__all__ = ["build_agent", "format_input", "REVIEWER_SYSTEM_PROMPT"]

