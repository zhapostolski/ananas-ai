from __future__ import annotations

import json

from .config import project_root


def _load_schema(name: str) -> dict:  # type: ignore[return]
    path = project_root() / "schemas" / name
    return json.loads(path.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def validate_required_fields(payload: dict, schema_name: str) -> list[str]:
    schema = _load_schema(schema_name)
    errors = []
    for key in schema.get("required", []):
        if key not in payload:
            errors.append(f"Missing required field: {key}")
    return errors


def validate_agent_output(payload: dict) -> list[str]:
    errors = validate_required_fields(payload, "agent_output.schema.json")
    if payload.get("agent_name", "") == "":
        errors.append("agent_name cannot be empty")
    if payload.get("module_name", "") == "":
        errors.append("module_name cannot be empty")
    return errors
