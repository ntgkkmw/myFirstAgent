"""Command-line entry point for Codex MAS."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from typing import Any, Optional

from pydantic import ValidationError

from codex_mas.agents import coder, researcher, reviewer, router, summarizer, tester
from codex_mas.config.settings import Deps, PolicyConfig, RagClient, Settings, get_settings
from codex_mas.schemas.models import (
    Brief,
    CodePatch,
    EvidenceList,
    FinalAnswer,
    RouterDecision,
    TestPlan,
    UserQuery,
)


@dataclass(slots=True)
class TokenBudget:
    limit: int
    remaining: int = field(init=False)

    def __post_init__(self) -> None:
        self.remaining = self.limit

    def estimate(self, text: str) -> int:
        return max(1, len(text) // 4)

    def consume(self, text: str) -> None:
        cost = self.estimate(text)
        if cost > self.remaining:
            raise RuntimeError(
                "Token budget exceeded while preparing to send context to the model. "
                "Shorten intermediate summaries or increase TOKEN_BUDGET_TOTAL."
            )
        self.remaining -= cost


class Workflow:
    def __init__(self, deps: Deps) -> None:
        self.deps = deps
        self.policy: PolicyConfig = deps.policy
        self.budget = TokenBudget(deps.token_budget)
        self.router_agent = router.build_agent(deps)
        self.researcher_agent = researcher.build_agent(deps)
        self.coder_agent = coder.build_agent(deps)
        self.coder_agent_escalated = coder.build_agent(deps, escalated=True)
        self.tester_agent = tester.build_agent(deps)
        self.summarizer_agent = summarizer.build_agent(deps)
        self.reviewer_agent = reviewer.build_agent(deps)

    def run(self, query: UserQuery) -> FinalAnswer:
        route_decision = self._run_router(query)
        evidence: Optional[EvidenceList] = None
        patch: Optional[CodePatch] = None
        plan: Optional[TestPlan] = None
        brief: Optional[Brief] = None

        if route_decision.route == "research_only":
            evidence = self._run_researcher(query)
        elif route_decision.route == "summarize":
            evidence = self._run_researcher(query)
            brief = self._run_summarizer(query, evidence)
        elif route_decision.route == "code":
            evidence = self._run_researcher(query)
            patch = self._run_coder(query, evidence)
            plan = self._run_tester(query, evidence)
        else:  # pragma: no cover - defensive
            raise ValueError(f"Unsupported route: {route_decision.route}")

        return self._run_reviewer(query, evidence, patch, plan, brief)

    def _invoke_agent(self, *, agent: Any, prompt: str, label: str) -> Any:
        self.budget.consume(prompt)
        result = agent.run_sync(prompt, deps=self.deps)
        self.deps.token_budget = self.budget.remaining
        if hasattr(result, "result"):
            return result.result
        return result

    def _run_router(self, query: UserQuery) -> RouterDecision:
        prompt = router.format_input(query)
        result = self._invoke_agent(agent=self.router_agent, prompt=prompt, label="router")
        if isinstance(result, RouterDecision):
            return result
        return RouterDecision.model_validate(result)

    def _run_researcher(self, query: UserQuery) -> EvidenceList:
        prompt = researcher.format_input(query)
        result = self._invoke_agent(agent=self.researcher_agent, prompt=prompt, label="researcher")
        if isinstance(result, EvidenceList):
            return result
        return EvidenceList.model_validate(result)

    def _run_coder(self, query: UserQuery, evidence: EvidenceList) -> CodePatch:
        prompt = coder.format_input(query, evidence)
        try:
            result = self._invoke_agent(agent=self.coder_agent, prompt=prompt, label="coder")
            return CodePatch.model_validate(result)
        except ValidationError:
            if self.policy.coder_escalations <= 0:
                raise
            self.policy.coder_escalations -= 1
        result = self._invoke_agent(agent=self.coder_agent_escalated, prompt=prompt, label="coder")
        return CodePatch.model_validate(result)

    def _run_tester(self, query: UserQuery, evidence: EvidenceList) -> TestPlan:
        prompt = tester.format_input(query, evidence)
        result = self._invoke_agent(agent=self.tester_agent, prompt=prompt, label="tester")
        return TestPlan.model_validate(result)

    def _run_summarizer(self, query: UserQuery, evidence: EvidenceList) -> Brief:
        prompt = summarizer.format_input(query, evidence)
        result = self._invoke_agent(agent=self.summarizer_agent, prompt=prompt, label="summarizer")
        return Brief.model_validate(result)

    def _run_reviewer(
        self,
        query: UserQuery,
        evidence: EvidenceList | None,
        patch: CodePatch | None,
        plan: TestPlan | None,
        brief: Brief | None,
    ) -> FinalAnswer:
        prompt = reviewer.format_input(query, evidence, patch, plan, brief)
        result = self._invoke_agent(agent=self.reviewer_agent, prompt=prompt, label="reviewer")
        return FinalAnswer.model_validate(result)


def build_deps(settings: Settings) -> Deps:
    llms = settings.create_llm_clients()
    rag_client = RagClient()
    policy = PolicyConfig(token_budget_total=settings.token_budget_total)
    deps = Deps(
        llms=llms,
        rag=rag_client,
        policy=policy,
        token_budget=settings.token_budget_total,
    )
    deps.cache_dir.mkdir(parents=True, exist_ok=True)
    return deps


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Codex MAS workflow")
    parser.add_argument("--ask", required=True, help="User request to route through the agents")
    parser.add_argument("--constraints", nargs="*", default=[], help="Optional constraint strings")
    parser.add_argument("--style", default=None, help="Preferred response style")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    settings = get_settings()
    deps = build_deps(settings)
    workflow = Workflow(deps)
    query = UserQuery(goal=args.ask, constraints=args.constraints, preferred_style=args.style)
    final_answer = workflow.run(query)
    print(json.dumps(final_answer.model_dump(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())

