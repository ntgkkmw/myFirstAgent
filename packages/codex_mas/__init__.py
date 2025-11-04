"""Codex MAS package."""
from __future__ import annotations

import sys
import types

__all__ = ["__version__"]
__version__ = "0.1.0"

# Provide backward-compatible alias for the hyphenated directory name required by the spec.
_alias = types.ModuleType("codex-mas")
_alias.__dict__.update(globals())
_alias.__path__ = __path__  # type: ignore[name-defined]
sys.modules.setdefault("codex-mas", _alias)
