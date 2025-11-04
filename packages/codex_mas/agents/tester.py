"""Tester agent designs validation plans."""
from __future__ import annotations

from pydantic_ai import Agent, RunContext

from codex_mas.config.settings import Deps
from codex_mas.llm.registry import select_model
from codex_mas.schemas.models import EvidenceList, TestPlan, UserQuery
from codex_mas.tools.tests import run_tests

TESTER_SYSTEM_PROMPT = """
You are TesterAgent.
- Produce a targeted test plan validating the proposed code changes.
- Include high-value manual and automated checks as TestCase objects.
- Provide explicit instructions in `how_to_run` for local execution.
- Call the run_tests tool when execution is requested by the user.
- Output strictly matches the TestPlan schema as JSON.
- If tests cannot be executed, note why within `how_to_run`.
""".strip()


def build_agent(deps: Deps) -> Agent:
    model = select_model(deps.llms, "tester")
    agent = Agent(
        name="tester",
        system_prompt=TESTER_SYSTEM_PROMPT,
        model=model,
        result_type=TestPlan,
        deps_type=Deps,
    )

    @agent.tool
    def execute_tests(ctx: RunContext[Deps], paths: list[str]) -> dict[str, str]:
        summary = run_tests(paths)
        return summary.model_dump()

    return agent


def format_input(query: UserQuery, evidence: EvidenceList) -> str:
    constraints = "\n".join(f"- {item}" for item in query.constraints) or "(none)"
    key_findings = "\n".join(
        f"- {item.source}: {item.quote} (relevance {item.relevance:.2f})" for item in evidence.items
    )
    return "\n".join(
        [
            "GOAL:",
            query.goal,
            "",
            "CONSTRAINTS:",
            constraints,
            "",
            "KEY EVIDENCE:",
            key_findings or "(none)",
        ]
    )


__all__ = ["build_agent", "format_input", "TESTER_SYSTEM_PROMPT"]

