from __future__ import annotations

import argparse
from datetime import date

from ananas_ai.agents.crm_lifecycle import CRMLifecycleAgent
from ananas_ai.agents.cross_channel_brief import CrossChannelBriefAgent
from ananas_ai.agents.marketing_ops import MarketingOpsAgent
from ananas_ai.agents.performance import PerformanceAgent
from ananas_ai.agents.reputation import ReputationAgent
from ananas_ai.config import load_agent_channels, load_settings
from ananas_ai.email_delivery import send_brief
from ananas_ai.logging_config import get_logger
from ananas_ai.persistence import (
    bootstrap,
    fetch_daily_tokens,
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


def _agent_channels() -> dict[str, tuple[str, str]]:
    """Load agent → (channel, title) mapping from config/output-channels.json."""
    try:
        return load_agent_channels()
    except Exception:
        # Fallback so CLI never hard-breaks if config is temporarily unavailable
        return {
            "performance-agent": ("#marketing-performance", "Performance Summary"),
            "crm-lifecycle-agent": ("#marketing-crm", "CRM & Lifecycle Summary"),
            "reputation-agent": ("#marketing-reputation", "Reputation Summary"),
            "marketing-ops-agent": ("#marketing-ops", "Marketing Ops Summary"),
        }


def _daily_cap() -> int:
    try:
        return int(load_settings().model_routing["controls"]["per_day_token_cap_per_agent"])
    except Exception:
        return 200_000


def _check_daily_cap(agent_name: str) -> bool:
    """Return True if agent is within daily token cap, False if exceeded."""
    cap = _daily_cap()
    used = fetch_daily_tokens(agent_name)
    if used >= cap:
        logger.warning(
            "%s: daily token cap reached (%d/%d tokens) — skipping run",
            agent_name,
            used,
            cap,
        )
        upsert_health(agent_name, "warning", f"Daily token cap reached ({used:,}/{cap:,} tokens)")
        return False
    return True


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
    agent_channels = _agent_channels()
    if agent_name not in agent_channels:
        raise SystemExit("Use run-brief for the cross-channel brief.")

    bootstrap()

    if not _check_daily_cap(agent_name):
        return 0

    agent = AGENT_MAP[agent_name]()
    today = str(date.today())
    channel, title = agent_channels[agent_name]

    logger.info("Running %s", agent_name)
    data = agent.run(today, today)
    run_type = "live" if data.get("sources_active") or data.get("sources_live") else "sample"

    payload = agent.build_payload(data, today, today)
    errors = validate_agent_output(payload)

    tokens_in = data.get("tokens_in", 0)
    tokens_out = data.get("tokens_out", 0)
    cost = data.get("estimated_cost", 0.0)
    actual_model = data.get("model_used", payload.get("model_used", "unknown"))

    if errors:
        log_agent_run(
            agent_name,
            run_type,
            actual_model,
            "error",
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            estimated_cost=cost,
            error_message="; ".join(errors),
        )
        upsert_health(agent_name, "error", "; ".join(errors))
        raise SystemExit("Validation failed: " + "; ".join(errors))

    insert_agent_output(payload)
    log_agent_run(
        agent_name,
        run_type,
        actual_model,
        "ok",
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        estimated_cost=cost,
    )
    upsert_health(
        agent_name,
        "ok",
        f"{run_type.capitalize()} run — {tokens_in + tokens_out:,} tokens / ${cost:.4f}",
    )
    logger.info("Completed %s (%d tokens, $%.4f)", agent_name, tokens_in + tokens_out, cost)
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
        if not _check_daily_cap(agent_name):
            specialist_payloads.append(agent.build_payload(agent.sample_summary(), today, today))
            continue

        logger.info("  Running %s", agent_name)
        data = agent.run(today, today)
        pl = agent.build_payload(data, today, today)
        errors = validate_agent_output(pl)
        run_type = "live" if data.get("sources_active") or data.get("sources_live") else "sample"

        tokens_in = data.get("tokens_in", 0)
        tokens_out = data.get("tokens_out", 0)
        cost = data.get("estimated_cost", 0.0)
        actual_model = data.get("model_used", pl.get("model_used", "unknown"))

        if errors:
            log_agent_run(
                agent_name,
                run_type,
                actual_model,
                "error",
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                estimated_cost=cost,
                error_message="; ".join(errors),
            )
            upsert_health(agent_name, "error", "; ".join(errors))
            logger.warning("  %s validation errors: %s", agent_name, errors)
        else:
            insert_agent_output(pl)
            log_agent_run(
                agent_name,
                run_type,
                actual_model,
                "ok",
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                estimated_cost=cost,
            )
            upsert_health(
                agent_name,
                "ok",
                f"{run_type.capitalize()} run — {tokens_in + tokens_out:,} tokens / ${cost:.4f}",
            )
            ch_cfg = _agent_channels()
            if agent_name in ch_cfg:
                ch, ch_title = ch_cfg[agent_name]
                post_message(ch, ch_title, data.get("analysis", data.get("headline", "")))
        specialist_payloads.append(pl)

    logger.info("Running cross-channel-brief-agent")
    if not _check_daily_cap("cross-channel-brief-agent"):
        return 0

    data = brief.build_from_specialists(specialist_payloads)
    payload = brief.build_payload(data, today, today, complexity="high")
    errors = validate_agent_output(payload)

    tokens_in = data.get("tokens_in", 0)
    tokens_out = data.get("tokens_out", 0)
    cost = data.get("estimated_cost", 0.0)
    actual_model = data.get("model_used", payload.get("model_used", "unknown"))

    if errors:
        log_agent_run(
            "cross-channel-brief-agent",
            "live",
            actual_model,
            "error",
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            estimated_cost=cost,
            error_message="; ".join(errors),
        )
        upsert_health("cross-channel-brief-agent", "error", "; ".join(errors))
        raise SystemExit("Validation failed: " + "; ".join(errors))

    insert_agent_output(payload)
    log_agent_run(
        "cross-channel-brief-agent",
        "live",
        actual_model,
        "ok",
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        estimated_cost=cost,
    )
    upsert_health(
        "cross-channel-brief-agent",
        "ok",
        f"Live run — {tokens_in + tokens_out:,} tokens / ${cost:.4f}",
    )
    analysis = data.get("analysis", data.get("headline", "Brief ready."))
    post_message("#ai-marketing", "Daily Marketing Brief", analysis)
    send_brief("Daily Marketing Brief", analysis)
    logger.info(
        "Completed cross-channel-brief-agent (%d tokens, $%.4f)",
        tokens_in + tokens_out,
        cost,
    )
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
