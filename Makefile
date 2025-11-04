PYTHON ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/pip
PY := $(VENV)/bin/python

.PHONY: dev run eval

$(VENV)/bin/activate: pyproject.toml
python3 -m venv $(VENV)
$(PIP) install --upgrade pip
$(PIP) install -r requirements.txt
$(PIP) install -r requirements-dev.txt

touch-venv: $(VENV)/bin/activate
@:

dev: touch-venv
$(PIP) install -r requirements.txt
$(PIP) install -r requirements-dev.txt

run: touch-venv
@if [ -z "$(ask)" ]; then echo "Usage: make run ask='your question'"; exit 1; fi
$(PY) -m codex_mas.app.runner --ask "$(ask)"

eval: touch-venv
@echo "Running smoke evaluation..."
$(PY) -m codex_mas.app.runner --ask "Summarize project status" --constraints "3 bullets" >/dev/null || true
$(PY) -m codex_mas.app.runner --ask "Propose tests for new feature" --constraints "focus on unit tests" >/dev/null || true
$(PY) -m codex_mas.app.runner --ask "Fix bug in module" --constraints "update docs" >/dev/null || true
@echo "Evaluation complete (simulated)."
