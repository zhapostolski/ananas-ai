"""
guardrail_check.py — Output sanity checker for all Ananas AI agents.

Run this before writing any agent output to the DB or posting to Teams.
Returns exit code 0 (pass) or 1 (fail). Prints a structured result.

Usage:
    python scripts/guardrail_check.py <agent_name> <output_json_file>
    python scripts/guardrail_check.py performance-agent /tmp/perf_output.json

Or import and call check() directly:
    from scripts.guardrail_check import check
    result = check("performance-agent", output_dict)
    if not result["passed"]:
        raise ValueError(result["errors"])
"""

import json
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Structural requirements (applies to all agents)
# ---------------------------------------------------------------------------
REQUIRED_COMMON_FIELDS = [
    "agent_name",
    "module_name",
    "output_type",
    "date_from",
    "date_to",
    "data_json",
    "version",
    "model_used",
    "created_at",
    "run_type",  # "live" | "sample" — must always be explicit
]

# ---------------------------------------------------------------------------
# Per-agent KPI sanity bounds
# Each rule: (field_path_in_data_json, min, max, required)
# field_path uses dot notation: "kpis.poas"
# ---------------------------------------------------------------------------
AGENT_RULES: dict[str, list[tuple[str, float | None, float | None, bool]]] = {
    "performance-agent": [
        ("kpis.blended_roas", 0, 200, False),
        ("kpis.poas", 0, 50, False),
        ("kpis.cac", 0, 10_000, False),
        ("kpis.google_shopping_impression_share", 0, 100, False),
        ("kpis.cpc_trend_wow_pct", -100, 500, False),
        ("kpis.total_ad_spend", 0, None, False),
        ("kpis.net_revenue", 0, None, False),
    ],
    "crm-lifecycle-agent": [
        ("kpis.cart_abandonment_rate", 0, 100, False),
        ("kpis.cart_recovery_rate", 0, 100, False),
        ("kpis.email_open_rate", 0, 100, False),
        ("kpis.email_revenue_per_send", 0, 1000, False),
        ("kpis.active_subscribers", 0, None, False),
        ("kpis.repeat_purchase_rate", 0, 100, False),
    ],
    "reputation-agent": [
        ("kpis.trustpilot_rating", 1.0, 5.0, True),
        ("kpis.trustpilot_response_rate", 0, 100, False),
        ("kpis.average_response_time_hours", 0, 720, False),
        ("kpis.google_business_rating", 1.0, 5.0, False),
        ("kpis.review_count", 0, None, False),
    ],
    "marketing-ops-agent": [
        ("kpis.coupon_dependency_ratio", 0, 1.0, False),
        ("kpis.token_usage_pct", 0, 500, False),
        ("kpis.agent_uptime_pct", 0, 100, False),
        ("kpis.tracking_coverage_pct", 0, 100, False),
    ],
    "cross-channel-brief-agent": [
        # Must reference all 4 source agents
    ],
}

# cross-channel-brief must name all 4 source agents somewhere in its output
CROSS_CHANNEL_REQUIRED_SOURCES = [
    "performance-agent",
    "crm-lifecycle-agent",
    "reputation-agent",
    "marketing-ops-agent",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_nested(d: dict, path: str) -> Any:
    """Traverse dot-path into a nested dict. Returns None if missing."""
    parts = path.split(".")
    cur = d
    for p in parts:
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur


def _check_range(
    value: Any,
    min_val: float | None,
    max_val: float | None,
    field: str,
) -> str | None:
    """Return an error string if value is out of range, else None."""
    if value is None:
        return None  # missing fields handled separately
    try:
        v = float(value)
    except (TypeError, ValueError):
        return f"{field}: expected numeric, got {type(value).__name__}({value!r})"
    if min_val is not None and v < min_val:
        return f"{field}: {v} is below minimum {min_val}"
    if max_val is not None and v > max_val:
        return f"{field}: {v} exceeds maximum {max_val}"
    return None


# ---------------------------------------------------------------------------
# Core check function
# ---------------------------------------------------------------------------


def check(agent_name: str, output: dict) -> dict:
    """
    Run all guardrail checks on an agent output dict.

    Returns:
        {
            "passed": bool,
            "agent": str,
            "run_type": str | None,
            "errors": list[str],
            "warnings": list[str],
        }
    """
    errors: list[str] = []
    warnings: list[str] = []

    # 1. Structural check — required common fields
    for field in REQUIRED_COMMON_FIELDS:
        if field not in output or output[field] is None:
            errors.append(f"Missing required field: {field}")

    # 2. run_type must be explicit and valid
    run_type = output.get("run_type")
    if run_type not in ("live", "sample"):
        errors.append(f"run_type must be 'live' or 'sample', got: {run_type!r}")

    if run_type == "sample":
        warnings.append("run_type=sample: this output is based on hardcoded data, not live sources")

    # 3. agent_name must match
    declared_agent = output.get("agent_name")
    if declared_agent and declared_agent != agent_name:
        errors.append(f"agent_name mismatch: expected {agent_name!r}, got {declared_agent!r}")

    # 4. data_json must be a non-empty dict or JSON string
    data_json = output.get("data_json")
    if isinstance(data_json, str):
        try:
            data_json = json.loads(data_json)
        except json.JSONDecodeError as e:
            errors.append(f"data_json is not valid JSON: {e}")
            data_json = {}
    if not isinstance(data_json, dict) or not data_json:
        errors.append("data_json must be a non-empty object")
        data_json = {}

    # 5. Per-agent KPI range checks
    rules = AGENT_RULES.get(agent_name, [])
    for field_path, min_val, max_val, required in rules:
        value = _get_nested(data_json, field_path)
        if value is None:
            if required:
                errors.append(f"Required KPI missing: {field_path}")
            # non-required missing fields are fine (data may not always be available)
            continue
        err = _check_range(value, min_val, max_val, field_path)
        if err:
            errors.append(err)

    # 6. cross-channel-brief: must reference all source agents
    if agent_name == "cross-channel-brief-agent":
        raw_text = json.dumps(output)
        for src in CROSS_CHANNEL_REQUIRED_SOURCES:
            if src not in raw_text:
                errors.append(f"cross-channel-brief output does not reference source agent: {src}")

    # 7. Warn if Teams post would go out with sample data
    outputs = output.get("outputs", [])
    if run_type == "sample" and any("teams:" in str(o) for o in outputs):
        warnings.append(
            "SAMPLE DATA is routed to a Teams channel — ensure output includes a [SAMPLE] label"
        )

    return {
        "passed": len(errors) == 0,
        "agent": agent_name,
        "run_type": run_type,
        "errors": errors,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python scripts/guardrail_check.py <agent_name> <output_json_file>")
        sys.exit(2)

    agent_name = sys.argv[1]
    json_path = Path(sys.argv[2])

    if not json_path.exists():
        print(f"File not found: {json_path}")
        sys.exit(2)

    try:
        output = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in {json_path}: {e}")
        sys.exit(1)

    result = check(agent_name, output)

    print(f"Agent:    {result['agent']}")
    print(f"run_type: {result['run_type']}")

    if result["warnings"]:
        print("\nWarnings:")
        for w in result["warnings"]:
            print(f"  ! {w}")

    if result["passed"]:
        print("\nGUARDRAIL CHECK PASSED")
    else:
        print("\nGUARDRAIL CHECK FAILED")
        for e in result["errors"]:
            print(f"  x {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
