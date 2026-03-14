# Testing and Validation Rules

- Validate JSON outputs before storing them.
- New or changed config files must be parseable.
- New or changed diagrams must keep the same top-level structure unless the architecture changed intentionally.
- Before finalizing a change, run `python scripts/validate_pack.py`.
- If adding a new agent, update config, docs, and schedule in the same batch.
