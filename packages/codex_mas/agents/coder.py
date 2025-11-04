"""Coder agent responsible for drafting code patches."""
from __future__ import annotations

from pydantic_ai import Agent, RunContext

from codex_mas.config.settings import Deps
from codex_mas.llm.registry import select_model
from codex_mas.schemas.models import CodePatch, EvidenceList, UserQuery
from codex_mas.tools.vcs import apply_patch

CODER_SYSTEM_PROMPT = """
You are CoderAgent.
- Create precise unified diffs implementing the required changes.
- Incorporate relevant evidence snippets as rationale context.
- Output strictly matches the CodePatch schema in JSON.
- Diff must be ready for `patch -p1` and include file headers.
- Do not execute tests; leave that to TesterAgent.
- Never invent files or commands that do not exist; if uncertain, explain in rationale.
""".strip()


def build_agent(deps: Deps, *, escalated: bool = False) -> Agent:
    role = "coder_escalate" if escalated else "coder"
    model = select_model(deps.llms, role)
    name = "coder_escalated" if escalated else "coder"
    agent = Agent(
        name=name,
        system_prompt=CODER_SYSTEM_PROMPT,
        model=model,
        result_type=CodePatch,
        deps_type=Deps,
    )

    @agent.tool
    def dry_run_patch(ctx: RunContext[Deps], patch: CodePatch) -> dict[str, str]:
        """Dry run apply patch to surface validation errors."""

        result = apply_patch(patch, apply=False)
        return result.model_dump()

    return agent


def format_input(query: UserQuery, evidence: EvidenceList) -> str:
    """Prepare coder prompt."""

    evidence_lines = [
        f"- {item.source}: {item.quote} (relevance {item.relevance:.2f})"
        for item in evidence.items
    ]
    evidence_block = "\n".join(evidence_lines) if evidence_lines else "(no direct evidence collected)"
    constraints = "\n".join(f"- {item}" for item in query.constraints) or "(none)"
    sections = [
        "GOAL:",
        query.goal,
        "",
        "CONSTRAINTS:",
        constraints,
        "",
        "EVIDENCE:",
        evidence_block,
    ]
    return "\n".join(sections)


__all__ = ["build_agent", "format_input", "CODER_SYSTEM_PROMPT"]

