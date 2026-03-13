from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "CLAUDE.md",
    ".claude/settings.json",
    "config/project-overview.json",
    "config/agents.json",
    "config/model-routing.json",
    "config/schedules.json",
    "config/integrations-matrix.json",
    "config/metrics.json",
    "docs/architecture/architecture.md",
    "docs/implementation/implementation-plan.md",
    "docs/budget/budget.md"
]

def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    if missing:
        print("Missing required files:")
        for p in missing:
            print("-", p)
        return 1
    for rel in ["config/project-overview.json", "config/agents.json", "config/model-routing.json", "config/schedules.json", "config/integrations-matrix.json", "config/metrics.json"]:
        json.loads((ROOT / rel).read_text(encoding="utf-8"))
    print("Repository validation passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
