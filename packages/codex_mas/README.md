# codex_mas Package

This package hosts the Codex multi-agent system. Each agent is implemented with `pydantic_ai` and validated against the schemas in `schemas/models.py`.

## Modules

- `app/runner.py` – CLI workflow orchestrator.
- `agents/` – router, specialist, and reviewer agents.
- `config/settings.py` – environment configuration and dependency injection.
- `llm/registry.py` – OpenAI API adapters for `pydantic_ai`.
- `tools/` – auxiliary integrations (web search, RAG, VCS, tests).

Refer to the repository root `README.md` for setup instructions.
