"""Version control utilities."""
from __future__ import annotations

from pydantic import BaseModel

from codex_mas.schemas.models import CodePatch


class PatchResult(BaseModel):
    applied: bool
    message: str


def apply_patch(patch: CodePatch, *, apply: bool = False) -> PatchResult:
    """Dry-run patch application (non-destructive)."""

    if not patch.diff.strip():
        return PatchResult(applied=False, message="Empty diff provided")
    status = "Patch applied" if apply else "Patch validated"
    return PatchResult(applied=apply, message=f"{status} for {patch.path}")


__all__ = ["apply_patch", "PatchResult"]

