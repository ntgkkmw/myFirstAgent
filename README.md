# Codex MAS

Codex MAS is a production-oriented multi-agent workflow built with [pydantic_ai](https://github.com/pydantic/pydantic-ai) and the OpenAI API. The system routes each user query through a router → specialists → reviewer pipeline and validates every agent output with Pydantic models.

## Features

- Router, Researcher, Coder, Tester, Summarizer, and Reviewer agents with structured outputs.
- Token budget guardrails and coder model escalation.
- Tool integrations for web search, RAG retrieval, dry-run patch application, and simulated test execution.
- Configurable via `.env` / `.env.local` with typed settings and dependency injection.
- Pre-commit setup with `detect-secrets` to prevent accidental key leakage.

## Getting Started

1. **Create environment files**

   ```bash
   cp .env.example .env
   ```

   Populate `OPENAI_API_KEY` with a valid key. Never commit `.env` or `.env.local`; both are ignored via `.gitignore`.

2. **Install dependencies**

   ```bash
   make dev
   ```

   This bootstraps a virtual environment (`.venv`), installs runtime requirements (`pydantic_ai[openai]`, `openai`, `pydantic`, etc.), and development tooling (`pre-commit`, `detect-secrets`).

3. **Run the workflow**

   ```bash
   make run ask="Summarize the latest release notes"
   ```

   Additional flags:

   - `make run ask="..." constraints="needs unit tests"`
   - `make run ask="..." style="concise"`

4. **Pre-commit hooks**

   ```bash
   .venv/bin/pre-commit install
   ```

   Secrets should be managed via platform vaults (e.g., GitHub Actions Secrets, 1Password). Use the provided `detect-secrets` baseline (`.secrets.baseline`) to maintain coverage.

5. **Smoke evaluation**

   ```bash
   make eval
   ```

   Runs three representative flows (summarization, testing guidance, and coding) to verify agent orchestration.

## Repository Layout

```
packages/
  codex-mas -> symlink for spec compliance
  codex_mas/
    app/runner.py
    agents/
    tools/
    schemas/
    config/
    llm/
    examples/
```

- `config/settings.py` – typed settings & dependency container (`Deps`).
- `llm/registry.py` – OpenAI client adapters for `pydantic_ai`.
- `schemas/models.py` – shared Pydantic schemas enforced across agents.
- `app/runner.py` – CLI orchestrator orchestrating Router → specialists → Reviewer.
- `examples/quickstart.ipynb` – walkthrough notebook for interactive exploration.

## Secrets & Environment Management

- `.env` / `.env.local` are ignored by Git.
- Use `OPENAI_API_KEY` from secure storage (GitHub Secrets, 1Password, Vault).
- CI pipelines should inject secrets via environment variables.
- `detect-secrets` prevents committing accidental credentials; refresh the baseline after intentional config updates.

## Development Notes

- Token budget guard: configurable via `TOKEN_BUDGET_TOTAL`. Agents estimate usage and short-circuit if the budget would be exceeded.
- Coder escalation: failed schema validation retries once with the higher-tier model defined in `.env`.
- Tooling is mocked for offline development—replace stubs with production integrations as needed.

## License

MIT
