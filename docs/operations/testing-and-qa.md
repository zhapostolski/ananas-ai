# Testing and QA

## Release process (mandatory)

Never push a tag manually. Use the Makefile:

```bash
make release VERSION=v0.4.0
```

This runs the full local QA gate before tagging and pushing:

1. `ruff format` — auto-formats code
2. `ruff check` — lints for errors
3. `mypy` — type checks `src/ananas_ai/`
4. `pytest` — runs all 31+ tests with coverage
5. `python scripts/validate_pack.py` — validates all config JSON, required files, and subagent definitions

If any step fails, the release is aborted before the tag is created.

## GitHub Actions gate

On every `v*.*.*` tag, the Release workflow runs four parallel QA jobs:

| Job | Checks |
|---|---|
| `quality` | ruff format check, ruff lint, mypy |
| `test` | pytest with coverage |
| `validate` | scripts/validate_pack.py |
| `secrets-scan` | TruffleHog verified secrets scan |

The `deploy` job has `needs: [quality, test, validate, secrets-scan]` — it will not run if any QA job fails. Broken code cannot reach EC2.

CI also runs on every push to `main` and every pull request.

## Running QA locally

```bash
# Quick check (mirrors CI exactly — no auto-fix)
make ci-check

# Auto-fix formatting first, then full check
make qa

# Individual steps
make fmt          # auto-format
make lint         # ruff lint only
make types        # mypy only
make test         # pytest only
make validate     # config validation only
```

## Before changing an agent

Before enabling, changing, or adding an agent:

- [ ] Config files parse: `make validate`
- [ ] Output schema passes validation
- [ ] Token caps defined in `config/model-routing.json`
- [ ] Agent schedule updated in `config/schedules.json`
- [ ] Agent definition updated in `.claude/agents/`
- [ ] CHANGELOG updated
- [ ] All tests pass: `make test`

## Before changing integrations

- [ ] `config/integrations-matrix.json` updated
- [ ] `is_configured()` returns `False` cleanly when credentials are absent
- [ ] `safe_fetch()` returns `{}` or `None` on failure (never raises)
- [ ] No credentials hardcoded anywhere
- [ ] TruffleHog scan passes: `make release` will catch this

## Validate script coverage

`python scripts/validate_pack.py` checks:

- 12 required files exist (architecture, config, docs)
- 8 JSON config files parse without errors
- 16 subagent definitions exist in `.claude/agents/`
- `docs/budget/budget.md` exists
- `docs/architecture/CHANGELOG.md` exists
