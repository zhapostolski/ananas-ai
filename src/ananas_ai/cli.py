from __future__ import annotations

import argparse
from datetime import date

from ananas_ai.agents.crm_lifecycle import CRMLifecycleAgent
from ananas_ai.agents.cross_channel_brief import CrossChannelBriefAgent
from ananas_ai.agents.marketing_ops import MarketingOpsAgent
from ananas_ai.agents.performance import PerformanceAgent
from ananas_ai.agents.reputation import ReputationAgent
from ananas_ai.config import load_settings
from ananas_ai.logging_config import get_logger
from ananas_ai.persistence import (
    bootstrap,
    fetch_latest_outputs,
    insert_agent_output,
    log_agent_run,
    upsert_health,
)
from ananas_ai.teams import post_message
from ananas_ai.validator import validate_agent_output

logger = get_logger(__name__)

AGENT_MAP = {
    "performance-agent": PerformanceAgent,
    "crm-lifecycle-agent": CRMLifecycleAgent,
    "reputation-agent": ReputationAgent,
    "marketing-ops-agent": MarketingOpsAgent,
    "cross-channel-brief-agent": CrossChannelBriefAgent,
}

AGENT_CHANNELS = {
    "performance-agent": ("#marketing-performance", "Performance Summary"),
    "crm-lifecycle-agent": ("#marketing-crm", "CRM & Lifecycle Summary"),
    "reputation-agent": ("#marketing-reputation", "Reputation Summary"),
    "marketing-ops-agent": ("#marketing-ops", "Marketing Ops Summary"),
}


def doctor() -> int:
    settings = load_settings()
    logger.info("Project:       %s", settings.project_overview["project_name"])
    logger.info("Domain:        %s", settings.project_overview["domain"])
    logger.info("Phase 1 agents: %d", len(settings.agents["phase_1_agents"]))
    logger.info(
        "Model policy:  %s default / %s escalation",
        settings.model_routing["models"]["default"]["model"],
        settings.model_routing["models"]["escalation"]["model"],
    )
    return 0


def run_agent(agent_name: str) -> int:
    if agent_name not in AGENT_MAP:
        raise SystemExit(f"Unknown agent: {agent_name}")
    if agent_name not in AGENT_CHANNELS:
        raise SystemExit("Use run-brief for the cross-channel brief.")

    bootstrap()
    agent = AGENT_MAP[agent_name]()
    today = str(date.today())
    channel, title = AGENT_CHANNELS[agent_name]

    logger.info("Running %s", agent_name)
    # Use run() if the agent supports live data, otherwise fall back to sample_summary()
    run_type = "live"
    if hasattr(agent, "run"):
        data = agent.run(today, today)
    else:
        data = agent.sample_summary()
        run_type = "sample"

    payload = agent.build_payload(data, today, today)
    errors = validate_agent_output(payload)

    if errors:
        log_agent_run(
            agent_name,
            run_type,
            payload.get("model_used", "unknown"),
            "error",
            error_message="; ".join(errors),
        )
        upsert_health(agent_name, "error", "; ".join(errors))
        raise SystemExit("Validation failed: " + "; ".join(errors))

    insert_agent_output(payload)
    log_agent_run(agent_name, run_type, payload.get("model_used", "unknown"), "ok")
    upsert_health(agent_name, "ok", f"{run_type.capitalize()} run successful")
    post_message(channel, title, payload["data"]["headline"])
    logger.info("Completed %s", agent_name)
    return 0


def run_brief() -> int:
    bootstrap()
    perf = PerformanceAgent()
    crm = CRMLifecycleAgent()
    rep = ReputationAgent()
    ops = MarketingOpsAgent()
    brief = CrossChannelBriefAgent()
    today = str(date.today())

    logger.info("Running all specialist agents")
    specialists = [
        ("performance-agent", perf),
        ("crm-lifecycle-agent", crm),
        ("reputation-agent", rep),
        ("marketing-ops-agent", ops),
    ]
    specialist_payloads = []
    for agent_name, agent in specialists:
        logger.info("  Running %s", agent_name)
        data = agent.run(today, today)
        pl = agent.build_payload(data, today, today)
        errors = validate_agent_output(pl)
        run_type = "live" if data.get("sources_active") or data.get("sources_live") else "sample"
        if errors:
            log_agent_run(agent_name, run_type, pl.get("model_used", "unknown"), "error", error_message="; ".join(errors))
            upsert_health(agent_name, "error", "; ".join(errors))
            logger.warning("  %s validation errors: %s", agent_name, errors)
        else:
            insert_agent_output(pl)
            log_agent_run(agent_name, run_type, pl.get("model_used", "unknown"), "ok")
            upsert_health(agent_name, "ok", f"{run_type.capitalize()} run successful")
            channel, title = AGENT_CHANNELS[agent_name]
            post_message(channel, title, pl["data"].get("analysis", pl["data"].get("headline", "")))
        specialist_payloads.append(pl)

    logger.info("Running cross-channel-brief-agent")
    data = brief.build_from_specialists(specialist_payloads)
    payload = brief.build_payload(data, today, today, complexity="high")
    errors = validate_agent_output(payload)

    if errors:
        log_agent_run(
            "cross-channel-brief-agent",
            "live",
            payload.get("model_used", "unknown"),
            "error",
            error_message="; ".join(errors),
        )
        upsert_health("cross-channel-brief-agent", "error", "; ".join(errors))
        raise SystemExit("Validation failed: " + "; ".join(errors))

    insert_agent_output(payload)
    log_agent_run("cross-channel-brief-agent", "live", payload.get("model_used", "unknown"), "ok")
    upsert_health("cross-channel-brief-agent", "ok", "Live run successful")
    analysis = payload["data"].get("analysis", payload["data"].get("headline", "Brief ready."))
    post_message("#marketing-summary", "Daily Marketing Brief", analysis)
    post_message("#executive-summary", "Executive Summary", analysis)
    logger.info("Completed cross-channel-brief-agent")
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
        bootstrap()
        logger.info("Database bootstrapped")
        return 0
    if args.command == "run-agent":
        return run_agent(args.agent_name)
    if args.command == "run-brief":
        return run_brief()
    if args.command == "list-latest":
        for row in fetch_latest_outputs():
            logger.info("%s", row)
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
