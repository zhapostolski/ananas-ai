import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

required_files = [
    "CLAUDE.md",
    ".claude/settings.json",
    "docs/project-summary.md",
    "docs/architecture/architecture-v1.md",
    "docs/budget/budget.md",
    "docs/roadmap/phase-1-roadmap.md",
    "config/agents.json",
    "config/model-routing.json",
    "config/schedules.json",
    "config/integrations-matrix.json",
    "config/metrics.json",
    "diagrams/source/architecture-v1.mmd",
]

json_files = [
    "config/agents.json",
    "config/model-routing.json",
    "config/schedules.json",
    "config/integrations-matrix.json",
    "config/metrics.json",
    "config/output-schema-summary.json",
    "config/project-overview.json",
    ".claude/settings.json",
]

errors = []

for rel in required_files:
    path = ROOT / rel
    if not path.exists():
        errors.append(f"Missing required file: {rel}")

for rel in json_files:
    path = ROOT / rel
    if path.exists():
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            errors.append(f"Invalid JSON in {rel}: {e}")

agents = ROOT / "config/agents.json"
schedules = ROOT / "config/schedules.json"
if agents.exists() and schedules.exists():
    a = json.loads(agents.read_text(encoding="utf-8"))
    s = json.loads(schedules.read_text(encoding="utf-8"))
    agent_names = {x["name"] for x in a.get("agents", [])}
    sched_names = {x["agent"] for x in s.get("daily_runs", [])}
    if agent_names != sched_names:
        errors.append(
            f"Agent/schedule mismatch: agents={sorted(agent_names)} schedules={sorted(sched_names)}"
        )

subagents = list((ROOT / ".claude/agents").glob("*.md"))
if len(subagents) < 5:
    errors.append("Expected at least 5 project subagents")

if errors:
    print("VALIDATION FAILED")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("VALIDATION OK")
print(
    f"Checked {len(required_files)} required files, {len(json_files)} JSON files, and {len(subagents)} subagents."
)
