from __future__ import annotations
import argparse
from datetime import date
from ananas_ai.config import load_settings
from ananas_ai.persistence import bootstrap, insert_agent_output, log_agent_run, upsert_health, fetch_latest_outputs
from ananas_ai.validator import validate_agent_output
from ananas_ai.teams import post_message
from ananas_ai.agents.performance import PerformanceAgent
from ananas_ai.agents.crm_lifecycle import CRMLifecycleAgent
from ananas_ai.agents.reputation import ReputationAgent
from ananas_ai.agents.marketing_ops import MarketingOpsAgent
from ananas_ai.agents.cross_channel_brief import CrossChannelBriefAgent

AGENT_MAP = {
    "performance-agent": PerformanceAgent,
    "crm-lifecycle-agent": CRMLifecycleAgent,
    "reputation-agent": ReputationAgent,
    "marketing-ops-agent": MarketingOpsAgent,
    "cross-channel-brief-agent": CrossChannelBriefAgent,
}

def doctor() -> int:
    settings = load_settings()
    print("Project:", settings.project_overview["project_name"])
    print("Domain:", settings.project_overview["domain"])
    print("Phase 1 agents:", len(settings.agents["phase_1_agents"]))
    print("Model policy:", settings.model_routing["default_execution_model"], "default /", settings.model_routing["escalation_model"], "escalation")
    return 0

def run_agent(agent_name: str) -> int:
    if agent_name not in AGENT_MAP:
        raise SystemExit(f"Unknown agent: {agent_name}")
    bootstrap()
    cls = AGENT_MAP[agent_name]
    agent = cls()
    today = str(date.today())
    mapping = {
        "performance-agent": (agent.sample_summary(), "#marketing-performance", "Performance Summary"),
        "crm-lifecycle-agent": (agent.sample_summary(), "#marketing-crm", "CRM & Lifecycle Summary"),
        "reputation-agent": (agent.sample_summary(), "#marketing-reputation", "Reputation Summary"),
        "marketing-ops-agent": (agent.sample_summary(), "#marketing-ops", "Marketing Ops Summary"),
    }
    if agent_name not in mapping:
        raise SystemExit("Use run-brief for the cross-channel brief.")
    data, channel, title = mapping[agent_name]
    payload = agent.build_payload(data, today, today)
    errors = validate_agent_output(payload)
    if errors:
        log_agent_run(agent_name, "sample", payload.get("model_used", "unknown"), "error", error_message="; ".join(errors))
        upsert_health(agent_name, "error", "; ".join(errors))
        raise SystemExit("Validation failed: " + "; ".join(errors))
    insert_agent_output(payload)
    log_agent_run(agent_name, "sample", payload.get("model_used", "unknown"), "ok")
    upsert_health(agent_name, "ok", "Sample run successful")
    post_message(channel, title, payload["data"]["headline"])
    print(f"Ran {agent_name}")
    return 0

def run_brief() -> int:
    bootstrap()
    perf, crm, rep, ops, brief = PerformanceAgent(), CRMLifecycleAgent(), ReputationAgent(), MarketingOpsAgent(), CrossChannelBriefAgent()
    today = str(date.today())
    specialist_payloads = [
        perf.build_payload(perf.sample_summary(), today, today),
        crm.build_payload(crm.sample_summary(), today, today),
        rep.build_payload(rep.sample_summary(), today, today),
        ops.build_payload(ops.sample_summary(), today, today),
    ]
    data = brief.build_from_specialists(specialist_payloads)
    payload = brief.build_payload(data, today, today, complexity="high")
    errors = validate_agent_output(payload)
    if errors:
        log_agent_run("cross-channel-brief-agent", "sample", payload.get("model_used", "unknown"), "error", error_message="; ".join(errors))
        upsert_health("cross-channel-brief-agent", "error", "; ".join(errors))
        raise SystemExit("Validation failed: " + "; ".join(errors))
    insert_agent_output(payload)
    log_agent_run("cross-channel-brief-agent", "sample", payload.get("model_used", "unknown"), "ok")
    upsert_health("cross-channel-brief-agent", "ok", "Sample run successful")
    post_message("#marketing-summary", "Marketing Summary", payload["data"]["summary"])
    post_message("#executive-summary", "Executive Summary", "Concise executive brief ready.")
    print("Ran cross-channel-brief-agent")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description="Ananas AI CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    sub.add_parser("bootstrap-db")
    ra = sub.add_parser("run-agent")
    ra.add_argument("agent_name")
    sub.add_parser("run-brief")
    sub.add_parser("list-latest")
    args = parser.parse_args()
    if args.command == "doctor":
        return doctor()
    if args.command == "bootstrap-db":
        bootstrap(); print("Database bootstrapped"); return 0
    if args.command == "run-agent":
        return run_agent(args.agent_name)
    if args.command == "run-brief":
        return run_brief()
    if args.command == "list-latest":
        for row in fetch_latest_outputs():
            print(row)
        return 0
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
