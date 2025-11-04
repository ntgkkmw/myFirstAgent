"""Pydantic schemas for Codex MAS."""
from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, PositiveFloat


class UserQuery(BaseModel):
    """User supplied objective for the run."""

    goal: str = Field(..., description="Primary objective articulated by the user")
    constraints: List[str] = Field(default_factory=list, description="Constraints supplied by the user")
    preferred_style: Optional[str] = Field(default=None, description="Preferred style or tone of responses")


class EvidenceItem(BaseModel):
    source: str = Field(..., description="Source identifier for the evidence")
    quote: str = Field(..., description="Quoted material from the source")
    relevance: PositiveFloat = Field(..., le=1.0, description="Relevance score between 0 and 1")


class EvidenceList(BaseModel):
    items: List[EvidenceItem] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list, description="Unanswered questions or missing information")


class TestCase(BaseModel):
    name: str
    steps: List[str] = Field(default_factory=list)
    expect: str


class TestPlan(BaseModel):
    cases: List[TestCase] = Field(default_factory=list)
    how_to_run: str = Field(..., description="Instructions for executing the test plan")


class CodePatch(BaseModel):
    path: str
    diff: str = Field(..., description="Unified diff payload")
    rationale: str = Field(..., description="Summary of the reasoning behind the change")


class Brief(BaseModel):
    bullets: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)


class FinalAnswer(BaseModel):
    summary: str
    artifacts: Dict[str, str] = Field(default_factory=dict)
    next_actions: List[str] = Field(default_factory=list)
    diagnostics: List[str] = Field(default_factory=list)


class RouterDecision(BaseModel):
    route: Literal["code", "summarize", "research_only"]
    reasoning: str = Field(..., description="Short justification for the chosen route")

