"""Testing utilities."""
from __future__ import annotations

from pydantic import BaseModel, Field


class TestResultSummary(BaseModel):
    status: str = Field(description="Aggregate result, e.g., success/failure")
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    details: list[str] = Field(default_factory=list)


def run_tests(paths: list[str]) -> TestResultSummary:
    if not paths:
        return TestResultSummary(status="noop", details=["No tests requested"])
    return TestResultSummary(status="simulated", passed=len(paths), details=["Simulation only"])


__all__ = ["run_tests", "TestResultSummary"]

