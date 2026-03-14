.DEFAULT_GOAL := help
.PHONY: help install install-dev lint fmt fmt-check typecheck test validate ci \
        bootstrap run-agent run-brief doctor clean

PYTHON  := .venv/bin/python
PIP     := .venv/bin/pip
PYTEST  := .venv/bin/pytest
RUFF    := .venv/bin/ruff
MYPY    := .venv/bin/mypy

# ── Setup ─────────────────────────────────────────────────────────────────────

install:          ## Install runtime dependencies
	$(PIP) install -e .

install-dev:      ## Install all dependencies including dev tools
	$(PIP) install -e ".[dev]"
	$(PYTHON) -m pre_commit install

# ── Code quality ──────────────────────────────────────────────────────────────

lint:             ## Run ruff linter
	$(RUFF) check src/ tests/ scripts/

fmt:              ## Auto-format code with ruff
	$(RUFF) format src/ tests/ scripts/
	$(RUFF) check --fix src/ tests/ scripts/

fmt-check:        ## Check formatting without modifying files (used in CI)
	$(RUFF) format --check src/ tests/ scripts/
	$(RUFF) check src/ tests/ scripts/

typecheck:        ## Run mypy type checker
	$(MYPY) src/ananas_ai/

# ── Tests ─────────────────────────────────────────────────────────────────────

test:             ## Run test suite with coverage
	ANANAS_DB_PATH=:memory: $(PYTEST)

test-fast:        ## Run tests without coverage (faster)
	ANANAS_DB_PATH=:memory: $(PYTEST) --no-cov -q

# ── Validation ────────────────────────────────────────────────────────────────

validate:         ## Run repository/config validation script
	$(PYTHON) scripts/validate_pack.py

# ── Full CI check + release ───────────────────────────────────────────────────

ci: fmt-check typecheck test validate  ## Run everything CI runs (no auto-fix)

release:          ## QA → tag → push: make release VERSION=v0.4.0
ifndef VERSION
	$(error VERSION is required: make release VERSION=v0.4.0)
endif
	@echo "==> Running QA gate..."
	$(MAKE) fmt lint typecheck test validate
	@echo "==> Tagging $(VERSION)..."
	git tag $(VERSION)
	git push
	git push --tags
	@echo "==> Release $(VERSION) pushed — CI+Deploy running on GitHub Actions"

# ── Runtime ───────────────────────────────────────────────────────────────────

bootstrap:        ## Initialise the local SQLite database
	$(PYTHON) -m ananas_ai.cli bootstrap-db

doctor:           ## Check config and platform health
	$(PYTHON) -m ananas_ai.cli doctor

run-agent:        ## Run a single agent: make run-agent AGENT=performance-agent
	$(PYTHON) -m ananas_ai.cli run-agent $(AGENT)

run-brief:        ## Run the full cross-channel brief pipeline
	$(PYTHON) -m ananas_ai.cli run-brief

list-latest:      ## Show latest agent outputs from DB
	$(PYTHON) -m ananas_ai.cli list-latest

# ── Housekeeping ──────────────────────────────────────────────────────────────

clean:            ## Remove build artefacts, caches, coverage files
	find . -type d -name __pycache__ -not -path "./.venv/*" | xargs rm -rf
	find . -type f -name "*.pyc" -not -path "./.venv/*" -delete
	rm -rf .mypy_cache .ruff_cache .pytest_cache htmlcov coverage.xml

help:             ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'
